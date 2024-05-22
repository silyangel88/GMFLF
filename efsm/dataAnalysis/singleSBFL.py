import re
from efsm.dataAnalysis.func import *


if __name__ == "__main__":

    '''spectrum'''
    file_paths = all_path(r'D:\pythonProject\efsm\spectrumGeneration\MLS(250)\Spectrum')
    root_path = r'D:\pythonProject\efsm\spectrumGeneration\MLS(250)\Spectrum'

    '''---------------------------------------------------------'''
    formulaDict = initFormulaDict()
    formulasList = list(formulaDict.keys())

    columnLen = len(formulasList)
    indexLen = len(file_paths)
    columnList = formulasList
    indexList = []
    for i in range(indexLen):

        match = re.search(r'_(.*?)\.', file_paths[i])
        indexList.append(match.group(1))


    Ranktable = pd.DataFrame(np.zeros([indexLen, columnLen]), index=indexList, columns=columnList)
    # Examscore
    EXAMtable = pd.DataFrame(np.zeros([indexLen, columnLen]), index=indexList, columns=columnList)

    evaluation_Table = pd.DataFrame(np.zeros([11, columnLen]), columns=columnList)
    evaluation_Table.index = ['median_Examscore(%)', 'mean_Examscore(%)', 'sd_Examscore(%)', 'Total_acc1', 'Total_acc2',
                              'Total_acc3', 'Total_acc5', 'rate_acc1', 'rate_acc2', 'rate_acc3', 'rate_acc5']

    for i in range(indexLen):
        print(file_paths[i], "-----------------------------------------")
        filepath = root_path + '\\' + file_paths[i]
        faultpos, spectrum, total_transitions = readCSV(filepath)

        Ranktable, EXAMtable, evaluation_Table = classical(spectrum, indexList[i], Ranktable, EXAMtable, evaluation_Table, total_transitions, faultpos)


    median_values = EXAMtable.median()
    mean_values = EXAMtable.mean()
    std_dev_values = EXAMtable.std()
    # evaluation_Table
    evaluation_Table.loc['median_Examscore(%)'] = median_values
    evaluation_Table.loc['mean_Examscore(%)'] = mean_values
    evaluation_Table.loc['sd_Examscore(%)'] = std_dev_values

    rate_values = evaluation_Table.loc[['Total_acc1', 'Total_acc2', 'Total_acc3', 'Total_acc5']] / indexLen
    matching_indices = ['rate_acc1', 'rate_acc2', 'rate_acc3', 'rate_acc5']

    for i, index_name in enumerate(matching_indices):
        evaluation_Table.loc[index_name] = rate_values.iloc[i]

    file_name1 = 'EXP1_MLS(250)_rankFault.csv'
    Ranktable.to_csv(file_name1, mode='w', header=True, sep=',')

    file_name2 = 'EXP1_MLS(250)_evaluation.csv'
    evaluation_Table.to_csv(file_name2, mode='w', sep=',')
