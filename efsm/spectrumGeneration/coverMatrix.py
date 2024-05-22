import os
import numpy as np
import pandas as pd
import re


def get_info(moedel_name, i):
    if moedel_name == "class2_mut":
        index_trace = ['t0', 't1', 't2', 't3', 't4', 't5', 't6', 't7', 't8', 't9', 't10', 't11', 't12', 't13', 't14', 't15',
                       't16', 't17', 't18', 't19', 't20']
        index_transition = ['T0', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10', 'T11', 'T12', 'T13', 'T14',
                            'T15', 'T16', 'T17', 'T18', 'T19', 'T20']
    else:
        index_trace = ['t' + str(j) for j in range(1, i + 1)]
        index_transition = ['T' + str(j) for j in range(1, i + 1)]

    return index_trace, index_transition


def all_path(dirname):
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = root_path + dirname
    result = []  # 所有的文件

    for maindir, subdir, file_name_list in os.walk(file_path):
        for filename in file_name_list:
            result.append(filename)
    # print(result)
    return result


def read_trace(root_path, file_path):

    filepath = root_path + '\\' + file_path
    data = pd.read_csv(filepath)

    list = data['Passed/Failed'].values.tolist()
    failed_count = 0
    testcase_count = len(list)
    for item in list:
        if item == 'Failed':
            failed_count += 1
    passed_count = testcase_count - failed_count

    print("testcase_count:{0}, failed_count:{1}, passed_count:{2}".format(testcase_count, failed_count, passed_count))
    return data, testcase_count, failed_count, passed_count


if __name__ == '__main__':
    traceInfo_files = all_path(r'/spectrumGeneration/MLS(250)/Trace')
    root_path = r'D:\pythonProject\efsm\spectrumGeneration\MLS(250)\Trace'
    print(traceInfo_files)

    '''transitionNum: 
     SCP_mut-8; ATM_mut-30; Network_mut-17; INRES_mut-18; OLSR_mut -23 InFlight_mut -32 SIP_mut -57 MLS_mut -81
     '''
    moedel_name = 'MLS_mut'
    transitionNum = 81                  # !!!
    index_trace, index_transition = get_info(moedel_name, transitionNum)

    for filename in traceInfo_files:
        print(filename, "---------------------------------------")
        data, testcase_count, failed_count, passed_count = read_trace(root_path, filename)

        match = re.search(r'T(\d+)', filename)
        error_transition = match.group(1)

        df_Passed = pd.DataFrame(data=None, index=index_transition)
        df_Failed = pd.DataFrame(data=None, index=index_transition)

        trace_visited = set()
        for i in range(testcase_count):
            trace_list = eval(data['trace'].iloc[i])
            execute = pd.DataFrame(data=np.zeros(len(index_trace)), index=index_trace)
            for single_trace in trace_list:
                if single_trace in trace_visited:
                    continue
                else:
                    trace_visited.add(single_trace)
                    execute.loc[single_trace] = 1

            flag_Failed = data['Passed/Failed'].iloc[i]
            column_name = "tc"+ str(i + 1)
            if flag_Failed == 'Failed':
                df_Failed[column_name] = execute[0].values.tolist()
            else:
                df_Passed[column_name] = execute[0].values.tolist()

            trace_visited = set()

        size = len(index_transition) * 4
        spectrum = np.zeros(size).reshape(len(index_transition),4)
        df_spectrum = pd.DataFrame(data=spectrum, columns=['EP', 'EF', 'NP', 'NF'], index=index_transition)
        Failed_matrix = df_Failed.values
        Passed_matrix = df_Passed.values

        temp = np.ones(len(index_transition))
        EP = np.sum(Passed_matrix, axis=1)
        df_spectrum['EP'] = EP
        EF = np.sum(Failed_matrix, axis=1)
        df_spectrum['EF'] = EF
        NP = temp * passed_count - EP
        df_spectrum['NP'] = NP
        NF = temp * failed_count - EF
        df_spectrum['NF'] = NF
        print(df_spectrum)

        error_t = pd.DataFrame(data=[''])
        error_t[0] = error_transition

        match = re.search(r'_(.*?)\.', filename)
        result_name = match.group(1)
        file_name = r'D:\pythonProject\efsm\spectrumGeneration\temp_spectrum\spectrum_{0}.csv'.format(result_name)

        error_t.to_csv(file_name, mode='w', header=False, index=False, sep=',')
        df_spectrum.to_csv(file_name, mode='a', header=False, index=False, sep=',')







