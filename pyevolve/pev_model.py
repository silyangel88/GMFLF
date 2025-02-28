# coding:utf-8
import os
# import sys
import numpy as np
import pandas as pd
# import time
# import pickle
import warnings
import random
from pyevolve import *
warnings.filterwarnings('ignore')


def gp_add(a, b): return a + b
def gp_sub(a, b): return a - b
def gp_div(a, b): return np.where(b == 0, 1, a.astype(float)/b)  # prevent "divided by 0
def gp_mul(a, b): return a * b
def gp_sqrt(a): return np.sqrt(abs(a))


# return all filenames in current dirname
def all_path(dirname):

    result = []
    for maindir, subdir, file_name_list in os.walk(dirname):

        for filename in file_name_list:
            apath = os.path.join(maindir, filename)
            result.append(apath)
    return result


# loading program spectrum
def readCSV(dataFiles):

    nFaultVersion = len(dataFiles)                   # the number of faulty versions
    vFaultLocation = np.zeros(nFaultVersion)         # the index of the faulty transition (the zero-based)
    vTransitionCount = np.zeros(nFaultVersion)       # the total number of statements in each faulty version
    i = 0
    FaultVersionsDict = dict()

    for csvFile in dataFiles:
        print (csvFile)
        nFirstFault = (pd.read_csv(csvFile, sep=',', nrows=0)).columns[0]            # the location of first fault
        # the first line of each file contains the zero-based index of the faulty statement
        df = pd.read_csv(csvFile, sep=',', header=None, skiprows=1)
        prMatrix = df.as_matrix()
        vFaultLocation[i] = nFirstFault
        vTransitionCount[i] = prMatrix.shape[0]
        FaultVersionsDict[str(i)] = prMatrix
        i = i + 1

    print ("Total Files:",i)
    return [vFaultLocation, vTransitionCount, FaultVersionsDict]


def eval_func(chromosome):
    F = chromosome.getCompiledCode()
    fit = []
    for version in range(len(numberOfversion)):
        spectrum = FaultVersionsDict[str(numberOfversion[version])]
        EP = spectrum[:, 0]
        EF = spectrum[:, 1]
        NP = spectrum[:, 2]
        NF = spectrum[:, 3]
        susp_v = eval(F)

        sortedSusp_v = -np.sort(-susp_v)
        faultLocation = int(vFaultLocation[numberOfversion[version]])

        if 1000 <= numberOfversion[version] <= 1500:
            susForFault = susp_v[faultLocation]
            # print ("class2.....",str(numberOfversion[version]))
        else:
            susForFault = susp_v[faultLocation - 1]

        tieCount = np.where(sortedSusp_v == susForFault)
        # firstTie = tieCount[0].min() + 1      # zero-based
        LastTie =  tieCount[0].max() + 1        # the last index of a tie of faulty statement
        faultPosinRank = LastTie
        currentFit = 100 - (faultPosinRank / vTransitionCount[numberOfversion[version]]) * 100
        fit.append(currentFit)

    avgFiteness = np.mean(fit)               # avgexamscore
    # print (avgFiteness)
    return avgFiteness


def oneEvolveRun():
    genome = GTree.GTreeGP()
    genome.setParams(max_depth=4, method="ramped")
    genome.evaluator.set(eval_func)          # return avgFiteness
    ga = GSimpleGA.GSimpleGA(genome)
    ga.setParams(gp_terminals=['NP', 'EF', 'EP', 'NF'],
                 gp_function_prefix="gp")
    ga.setElitism(True)
    ga.setGenerations(60)
    ga.setCrossoverRate(1.0)
    ga.setMutationRate(0.08)
    ga.setPopulationSize(40)
    ga.setElitismReplacement(15)     # the number of the best individuals to copy to the next generation on the elitism

    ga(freq_stats=20)
    bestFormula = ga.bestIndividual()
    Fitness = bestFormula.getFitnessScore()
    RawScore = bestFormula.getRawScore()
    strFormula = bestFormula.getPreOrderExpression()
    return [Fitness, RawScore, strFormula]
    #print(best)


def main_run(outputFolder):
    if os.path.exists(outputFolder) is False:
        os.mkdir(outputFolder)
    outputFile_i = os.path.join(outputFolder, "formula(3000)_MLS.csv")
    outputFile_v = os.path.join(outputFolder, "VersionSamples(3000)_MLS.csv")
    outputFile_f = os.path.join(outputFolder, "Fiteness(3000)_MLS.csv")
    file_v = open(outputFile_v, "a")
    file_f = open(outputFile_f, "a")
    with open(outputFile_i, "a") as file:
        global numberOfversion
        for i in range(3000):
           print(i)
           numberOfversion = random.sample(range(0, 92), 74)
           file_v.write(str(numberOfversion)+"\n")
           file_v.flush()

           Fitness, RawScore, Formula = oneEvolveRun()
           file.write(Formula +"\n")
           file_f.write(str(Fitness) + "," + str(RawScore) +"\n")
           file_f.flush()

           file.flush()

        file.close()
        file_v.close()


def testExpression():
    spectrum = FaultVersionsDict['0']
    EP = spectrum[:, 0]
    EF = spectrum[:, 1]
    NP = spectrum[:, 2]
    NF = spectrum[:, 3]
    F = "gp_add(gp_add(gp_sqrt(gp_sqrt(NF)), gp_sqrt(gp_div(EF, NF))), gp_add(gp_sqrt(gp_add(NP, NP)), gp_sqrt(gp_add(NP, NP))))"
    susp_v = eval(F)

    return susp_v


if __name__ == "__main__":

    dataFiles = all_path("C:\Users\lenovo\Desktop\spectrum\MLS(250)")
    vFaultLocation, vTransitionCount, FaultVersionsDict = readCSV(dataFiles)

    '''GP'''
    global numberOfversion
    main_run("C:\Users\lenovo\Desktop\GP_model\ev_results_MLS")              # outputFolder



