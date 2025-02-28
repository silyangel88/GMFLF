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


def readGPFormulas(dataFile):
    gpFormulaDict = dict()
    gpFormulaFile = open(dataFile, 'r')

    i=0
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
    # print(result)
    return result


if __name__ == "__main__":

    gpFormulaDict = readGPFormulas(r"D:\pythonProject\WOA_modelSpectrum\RM2(250)\formula(3000)_RM2.csv")     # !!!
    formulas_list = list(gpFormulaDict.values())
    # print(formulas_list)

    file_paths = all_path(r'D:\pythonProject\efsm\spectrumGeneration\RM2(250)\Spectrum')     # !!!!!
    root_path = r'D:\pythonProject\efsm\spectrumGeneration\RM2(250)\Spectrum'            # !!!!!

    for file in file_paths:
        print(file, "-----------------------------------------")
        filepath = root_path + '\\' + file
        faultpos, spectrum, total_transitions = readCSV(filepath)

        GPsus_table_Raw = pd.DataFrame(np.zeros([total_transitions, 1]))
        GPsus_table_Raw.columns = ['transition']
        GPsus_table_Raw['transition'] = pd.DataFrame(np.arange(1, total_transitions + 1))
        # GPsus_table_Raw['transition'] = pd.DataFrame(np.arange(0, total_transitions))             # class2-t0

        rank_table_Raw = pd.DataFrame(np.zeros([total_transitions, 1]))
        rank_table_Raw.columns = ['transition']
        rank_table_Raw['transition'] = pd.DataFrame(np.arange(1, total_transitions + 1))
        # rank_table_Raw['transition'] = pd.DataFrame(np.arange(0, total_transitions))             # class2-t0

        spectrum = spectrum.values
        EP = spectrum[:, 0]
        EF = spectrum[:, 1]
        NP = spectrum[:, 2]
        NF = spectrum[:, 3]

        i = 1
        for f in range(len(formulas_list)):
            formula = formulas_list[f]
            suspName = str(i)

            suspList = eval(formula)
            GPsus_table_Raw[suspName] = suspList

            suspList = pd.DataFrame(suspList)
            rank = suspList.rank(method="first", ascending=False)
            rank_name = str(i)
            rank_table_Raw[rank_name] = rank

            i = i + 1

        match = re.search(r'_(.*?)\.', file)
        result_name = match.group(1)

        file_name1 = r'D:\pythonProject\WOA_modelSpectrum\RM2(250)\TrainSusp\GPsusp(3000)_{0}.csv'.format(result_name)  # !!!
        GPsus_table_Raw.to_csv(file_name1, mode='w', header=True, index=False, sep=',')

        rankfile_name1 = r'D:\pythonProject\WOA_modelSpectrum\RM2(250)\rankTable\GPrank(3000)_{0}.csv'.format(result_name)  # !!!
        rank_table_Raw.to_csv(rankfile_name1, mode='w', header=True, index=False, sep=',')

