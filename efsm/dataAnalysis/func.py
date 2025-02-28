import numpy as np
import pandas as pd
import csv
import os
import time


# Define the GP Operators
def gp_add(a, b): return a + b
def gp_sub(a, b): return a - b
def gp_div(a, b):
    eps = 1e-6
    c = np.divide(a, np.where(b != 0, b, eps))
    return c
def gp_mul(a, b): return a * b
def gp_sqrt(a): return np.sqrt(abs(a))


def all_path(file_path):

    result = []
    for maindir, subdir, file_name_list in os.walk(file_path):
        for filename in file_name_list:
            result.append(filename)
    # print(result)
    return result


def readCSV(file_path):

    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        result = list(reader)
        faultpos = eval(result[0][0])

    # 读取程序谱
    dataset = pd.read_csv(file_path, names=['EP', 'EF', 'NP', 'NF'], skiprows=1)
    total_transitions = dataset.shape[0]                # total transitions

    # print("total transitions：", total_transitions, "fault position：", faultpos)
    return faultpos, dataset, total_transitions


'''公式-16个'''
def initFormulaDict():
    FormulaDict = dict()

    FormulaDict["Tarantula"] = "gp_div(gp_div(EF,(EF + NF )),(gp_div(EF,(EF + NF )) + gp_div(EP,(EP + NP))))"
    FormulaDict["Ochiai1"] = "gp_div(EF, gp_sqrt((EF + EP) * (EF + NF)))"
    FormulaDict["Ochiai2"] = "gp_div((EF * NP),gp_sqrt((EF+EP) * (NF+NP) * (EF+NP) * (EP+NF)))"
    FormulaDict["Ample"] = "gp_sub(gp_div(EF,(EF+NF)),gp_div(EP,(EP+NP)))"
    FormulaDict["Jaccard"] = "gp_div(EF, (EF + EP + NF))"
    FormulaDict["Kulczynski"] = "gp_div(EF,(NF + EP ))"
    FormulaDict["Dstar2"] = "gp_div((EF * EF), (NF + EP ))"

    FormulaDict["Naish1"] = "-1 if np.all(EF>0) else NP"
    FormulaDict["Naish2"] = "gp_sub(EF,gp_div(EP,(EP+NP+1)))"
    FormulaDict["GP13"] = "gp_mul(EF,gp_add(1.0,gp_div(np.ones_like(EP, dtype=float),gp_add(gp_mul(2, EP), EF))))"

    FormulaDict["Wong1"] = "EF"
    FormulaDict["RusselRao"] = "gp_div(EF, (EF + EP + NF +NP ))"
    # FormulaDict["Binary"] = "0 if np.all(NF>0) else gp_div(EF, EF)"
    FormulaDict["Binary"] = "0 if np.all(EF>0) else gp_div(EF, EF)"

    FormulaDict["GP02"] = "gp_add(gp_mul(2,gp_add(EF,gp_sqrt(NP))),gp_sqrt(EP))"
    FormulaDict["GP03"] = "gp_sqrt(gp_sub(gp_mul(EF,EF),gp_sqrt(EP)))"
    FormulaDict["GP19"] = "gp_mul(EF,gp_sqrt((EP - EF + NF - NP )))"

    return FormulaDict


def classical(spectrum, indexName, Ranktable, EXAMtable, evaluation_Table, total_transitions, faultpos):

    formula_time_dict = {}

    spectrum = spectrum.values
    EP = spectrum[:, 0]
    EF = spectrum[:, 1]
    NP = spectrum[:, 2]
    NF = spectrum[:, 3]

    formulaDict = initFormulaDict()
    formulasList = list(formulaDict.keys())

    for f in range(len(formulasList)):
        formula = formulaDict[formulasList[f]]
        formula_name = formulasList[f]

        start_time = time.time()

        suspList = eval(formula)

        suspList = pd.DataFrame(suspList)
        rank = suspList.rank(method="first", ascending=False)
        rank_No = rank.at[faultpos-1, 0]
        # rank_No = rank.at[faultpos, 0]                         # class2!!!!
        Ranktable.at[indexName, formula_name] = rank_No

        EXAMscore = computeEXAMscore(rank_No, total_transitions)
        EXAMtable.at[indexName, formula_name] = EXAMscore

        acc1, acc2, acc3, acc5 = computeAccuracy(rank_No)
        evaluation_Table.at['Total_acc1', formula_name] += acc1
        evaluation_Table.at['Total_acc2', formula_name] += acc2
        evaluation_Table.at['Total_acc3', formula_name] += acc3
        evaluation_Table.at['Total_acc5', formula_name] += acc5

        end_time = time.time()
        execution_time_ms = (end_time - start_time) * 1000
        # 统计执行时间
        if formula_name not in formula_time_dict:
            formula_time_dict[formula_name] = {'total_time_ms': 0, 'count': 0}
        formula_time_dict[formula_name]['total_time_ms'] += execution_time_ms
        formula_time_dict[formula_name]['count'] += 1

    return Ranktable, EXAMtable, evaluation_Table, formula_time_dict


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


def GPformulas(formulas_list, formulaset, spectrum, indexName, Ranktable, EXAMtable, evaluation_Table, total_transitions, faultpos):

    formula_time_dict = {}

    spectrum = spectrum.values
    EP = spectrum[:, 0]
    EF = spectrum[:, 1]
    NP = spectrum[:, 2]
    NF = spectrum[:, 3]

    for f in formulaset:
        formula = formulas_list[f-1]
        # suspName = str(f)
        suspName = f

        start_time = time.time()

        '''原始值'''
        # 计算怀疑度值
        suspList = eval(formula)
        # 排序(包含tie的情况)
        suspList = pd.DataFrame(suspList)
        rank = suspList.rank(method="first", ascending=False)
        rank_No = rank.at[faultpos - 1, 0]
        # rank_No = rank.at[faultpos, 0]                # class2!!!!
        Ranktable.at[indexName, suspName] = rank_No

        ''' 评估 '''
        # 计算EXAMscore
        EXAMscore = computeEXAMscore(rank_No, total_transitions)
        EXAMtable.at[indexName, suspName] = EXAMscore

        # 计算Accuracy
        acc1, acc2, acc3, acc5 = computeAccuracy(rank_No)
        evaluation_Table.at['Total_acc1', suspName] += acc1
        evaluation_Table.at['Total_acc2', suspName] += acc2
        evaluation_Table.at['Total_acc3', suspName] += acc3
        evaluation_Table.at['Total_acc5', suspName] += acc5

        end_time = time.time()
        execution_time_ms = (end_time - start_time) * 1000

        # 统计执行时间
        if suspName not in formula_time_dict:
            formula_time_dict[suspName] = {'total_time_ms': 0, 'count': 0}
        formula_time_dict[suspName]['total_time_ms'] += execution_time_ms
        formula_time_dict[suspName]['count'] += 1

    return Ranktable, EXAMtable, evaluation_Table, formula_time_dict


def combineFormulas(scoredata, indexName, Ranktable, EXAMtable, evaluation_Table, total_transitions, faultpos):

    start_time = time.time()

    rank = scoredata.rank(method="first", ascending=False)
    rank_name = 'combine'
    rank_No = rank.at[faultpos - 1, 0]
    # rank_No = rank.at[faultpos, 0]
    Ranktable.at[indexName, rank_name] = rank_No

    ''' 评估 '''
    # 计算EXAMscore
    EXAMscore = computeEXAMscore(rank_No, total_transitions)
    EXAMtable.at[indexName, rank_name] = EXAMscore

    # 计算Accuracy
    acc1, acc2, acc3, acc5 = computeAccuracy(rank_No)
    evaluation_Table.at['Total_acc1', rank_name] += acc1
    evaluation_Table.at['Total_acc2', rank_name] += acc2
    evaluation_Table.at['Total_acc3', rank_name] += acc3
    evaluation_Table.at['Total_acc5', rank_name] += acc5

    end_time = time.time()
    execution_time_ms = (end_time - start_time) * 1000

    return Ranktable, EXAMtable, evaluation_Table, execution_time_ms


def computeEXAMscore(rank_No, total_transitions):

    EXAMscore = (rank_No / total_transitions) * 100
    return np.round(EXAMscore, 2)


def computeAccuracy(rank_No):
    acc1 = 0
    acc2 = 0
    acc3 = 0
    acc5 = 0

    if rank_No <= 1:
        acc1 = acc1 + 1
    if rank_No <= 2:
        acc2 = acc2 + 1
    if rank_No <= 3:
        acc3 = acc3 + 1
    if rank_No <= 5:
        acc5 = acc5 + 1

    return acc1, acc2, acc3, acc5







