import numpy as np
import pandas as pd
import csv
import os
import re


# Define the GP Operators
def gp_add(a, b): return a + b
def gp_sub(a, b): return a - b
def gp_div(a, b):
    eps = 1e-6
    c = np.divide(a, np.where(b != 0, b, eps))
    return c
def gp_mul(a, b): return a * b
def gp_sqrt(a): return np.sqrt(abs(a))


def initFormulaDict():
    FormulaDict = dict()

    FormulaDict["Binary"] = "0 if np.all(NF>0) else gp_div(EF, EF)"
    # FormulaDict["Binary"] = "0 if np.all(EF>0) else gp_div(EF, EF)"
    FormulaDict["GP13"] = "gp_mul(EF,gp_add(1.0,gp_div(np.ones_like(EP, dtype=float),gp_add(gp_mul(2, EP), EF))))"
    FormulaDict["Naish1"] = "-1 if np.all(EF>0) else NP"
    FormulaDict["Naish2"] = "gp_sub(EF,gp_div(EP,(EP+NP+1)))"
    FormulaDict["RusselRao"] = "gp_div(EF, (EF + EP + NF +NP ))"
    FormulaDict["Wong1"] = "EF"
    FormulaDict["Jaccard"] = "gp_div(EF, (EF + EP + NF))"
    FormulaDict["Ochiai1"] = "gp_div(EF, gp_sqrt((EF + EP) * (EF + NF)))"

    return FormulaDict


def readGPFormulas(dataFile):
    gpFormulaDict = dict()
    gpFormulaFile = open(dataFile, 'r')

    i = 0
    formulas = gpFormulaFile.readlines()
    for gpformula in formulas:
        gpFormulaDict[str(i)] = gpformula.strip()
        i = i + 1
    gpFormulaFile.close()

    return gpFormulaDict


def readCSV(file_path):

    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        result = list(reader)
        faultpos = eval(result[0][0])

    dataset = pd.read_csv(file_path, names=['EP', 'EF', 'NP', 'NF'], skiprows=1)
    total_transitions = dataset.shape[0]                          # total transitions

    print("total transitions：", total_transitions, "fault position：", faultpos)
    return faultpos, dataset, total_transitions


def all_path(file_path):

    result = []
    for maindir, subdir, file_name_list in os.walk(file_path):
        for filename in file_name_list:
            result.append(filename)

    return result


if __name__ == "__main__":

    file_paths = all_path(r'D:\pythonProject\efsm\spectrumGeneration\RM2(250)\Spectrum')     # !!!!!
    root_path = r'D:\pythonProject\efsm\spectrumGeneration\RM2(250)\Spectrum'            # !!!!!

    for file in file_paths:
        print(file, "-----------------------------------------")
        filepath = root_path + '\\' + file
        faultpos, spectrum, total_transitions = readCSV(filepath)

        Maximalsus_table = pd.DataFrame(np.zeros([total_transitions, 1]))
        Maximalsus_table.columns = ['transition']
        Maximalsus_table['transition'] = pd.DataFrame(np.arange(1, total_transitions + 1))
        # Maximalsus_table['transition'] = pd.DataFrame(np.arange(0, total_transitions))             # class2-t0

        spectrum = spectrum.values
        EP = spectrum[:, 0]
        EF = spectrum[:, 1]
        NP = spectrum[:, 2]
        NF = spectrum[:, 3]

        formulaDict = initFormulaDict()
        formulasList = list(formulaDict.keys())

        for f in range(8):
            formula = formulaDict[formulasList[f]]
            formula_name = formulasList[f]

            suspList = eval(formula)
            Maximalsus_table[formula_name] = suspList

        match = re.search(r'_(.*?)\.', file)
        result_name = match.group(1)

        file_name1 = r'D:\pythonProject\WOA_modelSpectrum\RM2(250)\PRINCESusp_Test\PRINCESusp_{0}.csv'.format(result_name)  # !!!
        Maximalsus_table.to_csv(file_name1, mode='w', header=True, index=False, sep=',')


