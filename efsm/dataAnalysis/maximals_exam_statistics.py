import re
from efsm.dataAnalysis.func import *
import random


if __name__ == "__main__":

    filepaths = all_path(r'D:\pythonProject\efsm\spectrumGeneration\RM2(250)\Spectrum')  # !!!!!
    root_path = r'D:\pythonProject\efsm\spectrumGeneration\RM2(250)\Spectrum'             # !!!!!
    '''scoreFiles'''
    scorefiles = all_path(r'D:\pythonProject\efsm\dataAnalysis\RM2(250)\Greatest')     # !!!
    root = r'D:\pythonProject\efsm\dataAnalysis\RM2(250)\Greatest'                     # !!!

    formulaDict = initFormulaDict()
    formulasList = list(formulaDict.keys())

    columnLen = len(formulasList) + 1
    columnList = formulasList + ['combine']

    # mean_Examscore
    mean_Examscore_Table = pd.DataFrame(np.zeros([30, columnLen]), columns=columnList)
    # sd_Examscore
    sd_Examscore_Table = pd.DataFrame(np.zeros([30, columnLen]), columns=columnList)

    for k in range(30):
        print("round----", k)

        '''testNum: 
          ATM_mut-28; Network_mut-24; INRES_mut-26; OLSR_mut -24; InFlight_mut -26; SIP_mut -22; MLS_mut -21; class2 -40
          RM1-26; RM2-25
        '''
        selected_files = random.sample(list(zip(filepaths, scorefiles)), 25)

        file_paths, scoreFiles = zip(*selected_files)
        indexLen = len(file_paths)

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

            Ranktable, EXAMtable, evaluation_Table, time1 = classical(spectrum, indexList[i], Ranktable, EXAMtable, evaluation_Table, total_transitions, faultpos)

        for i in range(len(scoreFiles)):
            print(scoreFiles[i], "---------------------")
            path = root + '\\' + scoreFiles[i]
            scoredata = pd.read_csv(path, sep='\t', header=None)

            '''transitionNum: 
            class2_mut-21; ATM_mut-30; Network_mut-17; INRES_mut-18; OLSR_mut -23; InFlight_mut -32; SIP_mut -57; 
            MLS_mut -81; RM1_mut-114; RM2_mut-224   
            '''
            total_transitions = 224                        # !!!!!
            # 使用正则表达式匹配数字
            match = re.search(r'T(\d+)', scoreFiles[i])
            faultPos = match.group(1)
            # print(faultPos)

            Ranktable, EXAMtable, evaluation_Table, time2 = combineFormulas(scoredata, indexList[i], Ranktable, EXAMtable, evaluation_Table, total_transitions, int(faultPos))

        median_values = EXAMtable.median()
        mean_values = EXAMtable.mean()
        std_dev_values = EXAMtable.std()

        evaluation_Table.loc['median_Examscore(%)'] = median_values
        evaluation_Table.loc['mean_Examscore(%)'] = mean_values
        evaluation_Table.loc['sd_Examscore(%)'] = std_dev_values

        mean_Examscore_Table.loc[k] = mean_values
        sd_Examscore_Table.loc[k] = std_dev_values

    file_name1 = 'Greatest_RM2_mean.csv'                                                      # !!!!
    mean_Examscore_Table.to_csv(file_name1, mode='w', header=True, sep=',')
    file_name2 = 'Greatest_RM2_sd.csv'                                                        # !!!!
    sd_Examscore_Table.to_csv(file_name2, mode='w', sep=',')

    mean_means = mean_Examscore_Table.mean()
    mean_sd = sd_Examscore_Table.mean()

    print("mean_mean：", mean_means)
    print("mean_sd：", mean_sd)

