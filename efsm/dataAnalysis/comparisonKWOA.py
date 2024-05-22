import re
from efsm.dataAnalysis.func import *
import random


if __name__ == "__main__":

    '''spectrum'''
    file_paths = all_path(r'D:\pythonProject\efsm\spectrumGeneration\class2(250)\Spectrum')
    root_path = r'D:\pythonProject\efsm\spectrumGeneration\class2(250)\Spectrum'
    '''scoreFiles'''
    scoreFiles = all_path(r'D:\pythonProject\efsm\dataAnalysis\class2(250)\KWOA_RN')
    root = r'D:\pythonProject\efsm\dataAnalysis\class2(250)\KWOA_RN'

    '''testNum: 
      ATM_mut-28; Network_mut-24; INRES_mut-26; OLSR_mut -24; InFlight_mut -26; SIP_mut -22; MLS_mut -21; class2 -40
    '''
    selected_files = random.sample(list(zip(file_paths, scoreFiles)), 40)
    file_paths, scoreFiles = zip(*selected_files)

    '''------------------------------------------------------'''
    formulaDict = initFormulaDict()
    formulasList = list(formulaDict.keys())
    formulaset = [24, 5, 1247, 1526, 1011, 8, 9]                # formulas subset

    columnLen = len(formulasList) + len(formulaset) + 1
    indexLen = len(file_paths)
    columnList = formulasList + formulaset + ['combine']
    indexList = []
    for i in range(len(file_paths)):

        match = re.search(r'_(.*?)\.', file_paths[i])
        indexList.append(match.group(1))

    Ranktable = pd.DataFrame(np.zeros([indexLen, columnLen]), index=indexList, columns=columnList)

    EXAMtable = pd.DataFrame(np.zeros([indexLen, columnLen]), index=indexList, columns=columnList)

    evaluation_Table = pd.DataFrame(np.zeros([11, columnLen]), columns=columnList)
    evaluation_Table.index = ['median_Examscore(%)', 'mean_Examscore(%)', 'sd_Examscore(%)', 'Total_acc1', 'Total_acc2',
                              'Total_acc3', 'Total_acc5', 'rate_acc1', 'rate_acc2', 'rate_acc3', 'rate_acc5']

    for i in range(len(file_paths)):
        print(file_paths[i], "-----------------------------------------")
        filepath = root_path + '\\' + file_paths[i]
        faultpos, spectrum, total_transitions = readCSV(filepath)

        Ranktable, EXAMtable, evaluation_Table = classical(spectrum, indexList[i], Ranktable, EXAMtable, evaluation_Table, total_transitions, faultpos)

        gpFormulaDict = readGPFormulas(r"D:\pythonProject\WOA_modelSpectrum\class2(250)\formula(3000)_class2.csv")
        formulas_list = list(gpFormulaDict.values())
        Ranktable, EXAMtable, evaluation_Table = GPformulas(formulas_list, formulaset, spectrum, indexList[i], Ranktable, EXAMtable, evaluation_Table, total_transitions, faultpos)


    for i in range(len(scoreFiles)):
        print(scoreFiles[i], "---------------------")
        path = root + '\\' + scoreFiles[i]
        scoredata = pd.read_csv(path, sep='\t', header=None)

        '''transitionNum: 
          class2_mut-21; ATM_mut-30; Network_mut-17; INRES_mut-18; OLSR_mut -23; InFlight_mut -32; SIP_mut -57; MLS_mut -81   
        '''
        total_transitions = 21                              # !!!!!

        match = re.search(r'T(\d+)', scoreFiles[i])
        faultPos = match.group(1)

        Ranktable, EXAMtable, evaluation_Table = combineFormulas(scoredata, indexList[i], Ranktable, EXAMtable, evaluation_Table, total_transitions, int(faultPos))

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


    file_name1 = 'KWOA_RN_class2(250)_rankFault.csv'                   # !!!!
    Ranktable.to_csv(file_name1, mode='w', header=True, sep=',')

    file_name2 = 'KWOA_RN_class2(250)_evaluation.csv'                  # !!!!
    evaluation_Table.to_csv(file_name2, mode='w', sep=',')

