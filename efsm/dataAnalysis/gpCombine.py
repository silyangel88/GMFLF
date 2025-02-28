import re
from efsm.dataAnalysis.func import *
import random


if __name__ == "__main__":

    file_paths = all_path(r'D:\pythonProject\efsm\spectrumGeneration\RM2(250)\Spectrum')  # !!!!
    root_path = r'D:\pythonProject\efsm\spectrumGeneration\RM2(250)\Spectrum'             # !!!!!
    '''scoreFiles'''
    scoreFiles = all_path(r'D:\pythonProject\efsm\dataAnalysis\RM2(250)\KWOA_RN')     # !!!
    root = r'D:\pythonProject\efsm\dataAnalysis\RM2(250)\KWOA_RN'                     # !!!

    '''testNum: 
      ATM_mut-28; Network_mut-24; INRES_mut-26; OLSR_mut -24; InFlight_mut -26; SIP_mut -22; MLS_mut -21; class2 -40
      RM1-26; RM2-25
    '''
    selected_files = random.sample(list(zip(file_paths, scoreFiles)), 25)

    # 将结果分离成两个列表
    file_paths, scoreFiles = zip(*selected_files)

    formulaDict = initFormulaDict()
    formulasList = list(formulaDict.keys())
    formulaset = [333, 1890, 2, 1, 4, 8, 1627, 6]              # selected formulas ！！！

    columnLen = len(formulasList) + len(formulaset) + 1
    indexLen = len(file_paths)
    columnList = formulasList + formulaset + ['combine']
    indexList = []
    for i in range(len(file_paths)):
        # 使用正则表达式提取中间部分
        match = re.search(r'_(.*?)\.', file_paths[i])
        indexList.append(match.group(1))

    # 怀疑度-排序表(只保存错误位置排名）
    Ranktable = pd.DataFrame(np.zeros([indexLen, columnLen]), index=indexList, columns=columnList)
    # Examscore暂存表
    EXAMtable = pd.DataFrame(np.zeros([indexLen, columnLen]), index=indexList, columns=columnList)
    # 评估值表
    evaluation_Table = pd.DataFrame(np.zeros([11, columnLen]), columns=columnList)
    evaluation_Table.index = ['median_Examscore(%)', 'mean_Examscore(%)', 'sd_Examscore(%)', 'Total_acc1', 'Total_acc2',
                              'Total_acc3', 'Total_acc5', 'rate_acc1', 'rate_acc2', 'rate_acc3', 'rate_acc5']   # !!!!

    for i in range(len(file_paths)):
        print(file_paths[i], "-----------------------------------------")
        filepath = root_path + '\\' + file_paths[i]
        faultpos, spectrum, total_transitions = readCSV(filepath)

        Ranktable, EXAMtable, evaluation_Table, classical_formula_time = classical(spectrum, indexList[i], Ranktable, EXAMtable, evaluation_Table, total_transitions, faultpos)

        gpFormulaDict = readGPFormulas(r"D:\pythonProject\WOA_modelSpectrum\RM2(250)\formula(3000)_RM2.csv")     # !!!
        formulas_list = list(gpFormulaDict.values())
        Ranktable, EXAMtable, evaluation_Table, GP_formula_time = GPformulas(formulas_list, formulaset, spectrum,
                                    indexList[i], Ranktable, EXAMtable, evaluation_Table, total_transitions, faultpos)

    for i in range(len(scoreFiles)):
        print(scoreFiles[i], "---------------------")
        path = root + '\\' + scoreFiles[i]
        scoredata = pd.read_csv(path, sep='\t', header=None)

        '''transitionNum: 
          class2_mut-21; ATM_mut-30; Network_mut-17; INRES_mut-18; OLSR_mut -23; InFlight_mut -32; SIP_mut -57; 
          MLS_mut -81; RM1_mut-114; RM2_mut-224      
        '''
        total_transitions = 224                            # !!!!!
        # 使用正则表达式匹配数字
        match = re.search(r'T(\d+)', scoreFiles[i])
        faultPos = match.group(1)  # group(1) 来获取捕获的数字部分
        # print(faultPos)

        Ranktable, EXAMtable, evaluation_Table, execution_time_ms = combineFormulas(scoredata, indexList[i], Ranktable, EXAMtable, evaluation_Table, total_transitions, int(faultPos))

    median_values = EXAMtable.median()
    mean_values = EXAMtable.mean()
    std_dev_values = EXAMtable.std()

    evaluation_Table.loc['median_Examscore(%)'] = median_values
    evaluation_Table.loc['mean_Examscore(%)'] = mean_values
    evaluation_Table.loc['sd_Examscore(%)'] = std_dev_values

    rate_values = evaluation_Table.loc[['Total_acc1', 'Total_acc2', 'Total_acc3', 'Total_acc5']] / indexLen
    matching_indices = ['rate_acc1', 'rate_acc2', 'rate_acc3', 'rate_acc5']

    for i, index_name in enumerate(matching_indices):
        evaluation_Table.loc[index_name] = rate_values.iloc[i]

    file_name1 = 'KWOA_RN_RM2(250)_rankFault.csv'                   # !!!!
    Ranktable.to_csv(file_name1, mode='w', header=True, sep=',')

    file_name2 = 'KWOA_RN_RM2(250)_evaluation.csv'                  # !!!!
    evaluation_Table.to_csv(file_name2, mode='w', sep=',')

    for formula_name, data in classical_formula_time.items():
        avg_time_ms = data['total_time_ms'] / data['count']
        print(f"{formula_name}: {avg_time_ms:.3f} ms")

    for formula_name, data in GP_formula_time.items():
        avg_time_ms = data['total_time_ms'] / data['count']
        print(f"{formula_name}: {avg_time_ms:.3f} ms")

    print(f"combine: {execution_time_ms:.3f} ms")
