import re
from efsm.dataAnalysis.func import *
import random


if __name__ == "__main__":

    '''spectrum'''
    file_paths = all_path(r'D:\pythonProject\efsm\spectrumGeneration\MLS(250)\Spectrum')
    root_path = r'D:\pythonProject\efsm\spectrumGeneration\MLS(250)\Spectrum'
    '''scoreFiles'''
    scoreFiles = all_path(r'D:\pythonProject\efsm\dataAnalysis\MLS(250)\EXP4')
    root = r'D:\pythonProject\efsm\dataAnalysis\MLS(250)\EXP4'

    # 使用random.sample从file_paths和scoreFiles中同时随机选择相同位置的x个测试文件
    selected_files = random.sample(list(zip(file_paths, scoreFiles)), 21)  # !!!

    # 将结果分离成两个列表
    file_paths, scoreFiles = zip(*selected_files)

    '''----------------------------- -----------------------------'''
    formulaDict = initFormulaDict()
    formulasList = list(formulaDict.keys())

    columnLen = len(formulasList) + 1
    indexLen = len(file_paths)
    columnList = formulasList + ['combine']
    indexList = []
    for i in range(len(file_paths)):

        match = re.search(r'_(.*?)\.', file_paths[i])
        indexList.append(match.group(1))

    Ranktable = pd.DataFrame(np.zeros([indexLen, columnLen]), index=indexList, columns=columnList)
    # Examscore
    EXAMtable = pd.DataFrame(np.zeros([indexLen, columnLen]), index=indexList, columns=columnList)

    evaluation_Table = pd.DataFrame(np.zeros([11, columnLen]), columns=columnList)
    evaluation_Table.index = ['median_Examscore(%)', 'mean_Examscore(%)', 'sd_Examscore(%)', 'Total_acc1', 'Total_acc2',
                              'Total_acc3', 'Total_acc5', 'rate_acc1', 'rate_acc2', 'rate_acc3', 'rate_acc5']

    for i in range(len(file_paths)):
        print(file_paths[i], "-----------------------------------------")
        filepath = root_path + '\\' + file_paths[i]
        faultpos, spectrum, total_transitions = readCSV(filepath)


        Ranktable, EXAMtable, evaluation_Table = classical(spectrum, indexList[i], Ranktable, EXAMtable, evaluation_Table, total_transitions, faultpos)


    for i in range(len(scoreFiles)):
        print(scoreFiles[i], "---------------------")
        path = root + '\\' + scoreFiles[i]
        scoredata = pd.read_csv(path, sep='\t', header=None)

        '''transitionNum: 
         SCP_mut-8; ATM_mut-30; Network_mut-17; INRES_mut-18; OLSR_mut -23; InFlight_mut -32; SIP_mut -57; MLS_mut -81   
        '''
        total_transitions = 81                              # !!!!!
        # 使用正则表达式匹配数字
        match = re.search(r'T(\d+)', scoreFiles[i])
        faultPos = match.group(1)  # group(1) 来获取捕获的数字部分

        Ranktable, EXAMtable, evaluation_Table = combineFormulas(scoredata, indexList[i], Ranktable, EXAMtable, evaluation_Table, total_transitions, int(faultPos))

    # 计算每一列的中位数、平均值和标准差
    median_values = EXAMtable.median()
    mean_values = EXAMtable.mean()
    std_dev_values = EXAMtable.std()
    # 将计算结果存储到 evaluation_Table 的对应的位置
    evaluation_Table.loc['median_Examscore(%)'] = median_values
    evaluation_Table.loc['mean_Examscore(%)'] = mean_values
    evaluation_Table.loc['sd_Examscore(%)'] = std_dev_values
    # 计算accuracy的占比
    rate_values = evaluation_Table.loc[['Total_acc1', 'Total_acc2', 'Total_acc3', 'Total_acc5']] / indexLen
    matching_indices = ['rate_acc1', 'rate_acc2', 'rate_acc3', 'rate_acc5']
    # 将索引名对应的数据更新到 evaluation_Table
    for i, index_name in enumerate(matching_indices):
        evaluation_Table.loc[index_name] = rate_values.iloc[i]


    file_name1 = 'EXP4_MLS(250)_rankFault.csv'
    Ranktable.to_csv(file_name1, mode='w', header=True, sep=',')

    file_name2 = 'EXP4_MLS(250)_evaluation.csv'
    evaluation_Table.to_csv(file_name2, mode='w', sep=',')

