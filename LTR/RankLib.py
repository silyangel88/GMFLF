import numpy as np
import pandas as pd
import os
import re


def all_path(file_path):

    result = []

    for maindir, subdir, file_name_list in os.walk(file_path):
        for filename in file_name_list:
            result.append(filename)

    return result


def readCSV(csvFile):

    dataset = pd.read_csv(csvFile)
    dataset = dataset.values
    dataset = dataset[:, 1:]

    return dataset


def combineColumn(formulaset, dataset, transitioncount):

    matrix = np.zeros([transitioncount, len(formulaset)])
    for i in range(len(formulaset)):
        index = formulaset[i] - 1
        matrix[:, i] = dataset[:, index]

    def normalize_column(column):
        min_val = np.min(column)
        max_val = np.max(column)
        if min_val == max_val:
            return pd.Series(1, index=column.index)
        else:
            return (column - min_val) / (max_val - min_val)

    matrix = pd.DataFrame(matrix)
    matrix = matrix.apply(normalize_column, axis=0)

    return matrix.values


def faultPos(csvFile):

    match = re.search(r'T(\d+)', csvFile)
    faultPos = match.group(1)
    return int(faultPos)


def trainTxt(formulaset, TrainRoot, dataFiles, transitioncount):
    strText = []

    id = 1
    for csvFile in dataFiles:

        faultpos = faultPos(csvFile)
        filename = TrainRoot + '\\' + csvFile
        dataset = readCSV(filename)
        matrix = combineColumn(formulaset, dataset, transitioncount)

        for i in range(transitioncount):
            # 开头id
            strline = ''
            # if i == faultpos:
            if (i + 1) == faultpos:             # no class2  !!!
                strline += "1 qid:" + str(id)
            else:
                strline += "0 qid:" + str(id)

            for j in range(len(formulaset)):
                strline += " " + str(formulaset[j]) + ":"
                strline += format(matrix[i, j], '6f')

            strText.append(strline)

        id += 1

    file_name = r"D:\pythonProject\LTR\RM2(250)\Greatest\Greatest_train_RM2.txt"         # !!!

    with open(file_name, 'w', encoding='utf-8') as file:
        for line in strText:
            file.write(line + '\n')

    return 0


def TestTxt(formulaset, TestRoot, Files, transitioncount):

    cmdText = []
    id = 1

    for File in Files:
        strText = []
        filename = TestRoot + '\\' + File
        dataset = readCSV(filename)
        matrix = combineColumn(formulaset, dataset, transitioncount)

        for i in range(transitioncount):
            # id
            strline = "0 qid:" + str(id)

            for j in range(len(formulaset)):
                strline += " " + str(formulaset[j]) + ":"
                strline += format(matrix[i, j], '6f')

            strText.append(strline)

        match = re.search(r'_(.*?)\.', File)
        result_name = match.group(1)

        file_name = r'D:\pythonProject\LTR\RM2(250)\Greatest\Greatest_test_{0}.txt'.format(result_name)    # !!!

        cmdline = 'java -jar bin/RankLib.jar -load Greatest_model_RM2.txt -rank Test/Greatest_test_{0}.txt -score ScoreFile/Greatest_ScoreFile_{0}.txt'.format(result_name)    # ！！！！
        cmdText.append(cmdline)

        with open(file_name, 'w', encoding='utf-8') as file:
            for line in strText:
                file.write(line + '\n')

    cmdName = r'D:\pythonProject\LTR\RM2(250)\Greatest\cmd.txt'   # !!!
    with open(cmdName, 'w', encoding='utf-8') as file:
        for line in cmdText:
            file.write(line + '\n')

    return 0


if __name__ == "__main__":

    # formulaset = [333, 1890, 2, 1, 4, 8, 1627, 6]             # GP  ！！！！
    # formulaset = [1, 2, 3, 4, 5, 6, 7]                       # MULTRIC ！！！
    # formulaset = [1, 2, 3, 4, 5, 6, 7, 8]                    # PRINCE ！！！
    formulaset = [1, 2, 3, 4, 5, 6, 8, 9]                       # Maximal ！！！

    '''transitionNum: 
     class2_mut-21; ATM_mut-30; Network_mut-17; INRES_mut-18; OLSR_mut -23; InFlight_mut -32; SIP_mut -57; MLS_mut -81
     RM1_mut-114; RM2_mut-224
    '''
    transitioncount = 224                                     # ！！！！

    ''' Train '''
    # TrainRoot = r"D:\pythonProject\WOA_modelSpectrum\RM2(250)\TrainSusp"           # GP
    # TrainRoot = r"D:\pythonProject\WOA_modelSpectrum\RM2(250)\MULTRICSusp"       # MULTRIC
    # TrainRoot = r"D:\pythonProject\WOA_modelSpectrum\RM2(250)\PRINCESusp"            # PRINCE
    TrainRoot = r"D:\pythonProject\WOA_modelSpectrum\RM2(250)\GreatestSusp"           # Maximal
    dataFiles = all_path(TrainRoot)
    trainTxt(formulaset, TrainRoot, dataFiles, transitioncount)

    ''' Test '''
    # TestRoot = r'D:\pythonProject\WOA_modelSpectrum\RM2(250)\TestSusp'             # GP
    # TestRoot = r'D:\pythonProject\WOA_modelSpectrum\RM2(250)\MULTRICSusp_Test'   # MULTRIC
    # TestRoot = r'D:\pythonProject\WOA_modelSpectrum\RM2(250)\PRINCESusp_Test'      # PRINCE
    TestRoot = r'D:\pythonProject\WOA_modelSpectrum\RM2(250)\GreatestSusp_Test'       # Maximal
    Files = all_path(TestRoot)
    TestTxt(formulaset, TestRoot, Files, transitioncount)

