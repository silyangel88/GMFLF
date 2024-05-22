import copy
import pandas as pd
import numpy as np
from efsm.EFSMparser.load import LoadEFSM
from efsm.spectrumGeneration.utility import read_csv_all_test_suite, all_path

if __name__ == '__main__':

    MUT_files = all_path(r'/Mutation/try')
    file_path = '/PathGeneration/modelTrace/modelTrace_MLS(250)_random.csv'
    test_suite, num_cases = read_csv_all_test_suite(file_path)             # test suite

    record = pd.DataFrame(np.zeros([0, 3]))
    record.columns = ['File', 'total failed', 'rate(failed / total)']

    for SPEC_FILE in MUT_files:
        print(SPEC_FILE, "------------------------------")
        l = LoadEFSM()

        '''dataframe'''
        testcase_index = []
        trace_list = []
        flag_list = []
        failed_totalCount = 0
        No_index = 0

        for index_ts, test_cases in enumerate(test_suite):

            failed_count = 0
            print("This testsuite has total testcases: ", len(test_cases))
            print(".....Checking.....")

            for index_tc, tc in enumerate(test_cases):

                print("tc", index_tc, ".................")
                No_index += 1
                efsm_obj = l.load_efsm(SPEC_FILE)

                flag_failed = False
                test_cases_trace = []

                for single_tc in tc:
                    error_transition_name = ''
                    output_event_runtime = ''

                    cur_sc_obj = efsm_obj.get_cur_sc()
                    cur_state = cur_sc_obj.get_cur_state()

                    input_event = single_tc.get('input_event')
                    output_event = single_tc.get('output_event')
                    input_variable = single_tc.get('input_val')

                    _transitionList = efsm_obj.get_next_trans(cur_state, list_flag=True)
                    _transitionList = copy.deepcopy(_transitionList)

                    for index_tran, cur_transition in enumerate(_transitionList):
                        transition_input_event = cur_transition.get_inp_event()
                        transition_trace = cur_transition.get_trans_name()

                        if transition_input_event != input_event:
                            if index_tran == len(_transitionList) - 1:
                                flag_failed = True
                                break
                            continue

                        cur_sc_obj.update_sc_input_params(input_variable)
                        if not efsm_obj.is_feasible(cur_transition, cur_sc_obj):
                            if index_tran == len(_transitionList) - 1:
                                flag_failed = True
                                break
                            continue

                        efsm_obj.execute(cur_transition, cur_sc_obj)
                        context_vars = cur_sc_obj.get_cur_context()
                        inp_params_val = cur_sc_obj.get_cur_input_params()
                        output_event_runtime = efsm_obj.update_transition_output(cur_transition, context_vars, inp_params_val)
                        cur_sc_obj.update_sc(cur_transition.t_state, context_vars, inp_params_val,cur_transition.trans_name, output_event)

                        if output_event_runtime != output_event:
                            flag_failed = True
                            error_transition_name = cur_transition.get_trans_name()
                            test_cases_trace.append(error_transition_name)
                            break
                        else:
                            test_cases_trace.append(transition_trace)
                            break

                    if flag_failed:
                        print('output error in ', error_transition_name)
                        break

                if flag_failed:
                    failed_count += 1
                    print('test case', No_index, 'failed.')
                    # print("-------------------------------------------")
                    flag_list.append('Failed')
                else:
                    flag_list.append('Passed')

                '''插入数据表'''
                testcase_index.append(No_index)
                trace_list.append(test_cases_trace)

            print(".....Done.....")
            # print("failed_count: {0}\n".format(failed_count))
            failed_totalCount += failed_count

        data = {'testcase_index': testcase_index, 'trace': trace_list, 'Passed/Failed': flag_list}
        df = pd.DataFrame(data)
        file_name = r'D:\\pythonProject\efsm\spectrumGeneration\temp_trace\traceInfo_{0}.csv'.format(SPEC_FILE)
        df.to_csv(file_name, mode='w', header=True, index=False, sep=',')

        print("total failed: ", failed_totalCount)
        print("rate : failed / total = ", failed_totalCount / num_cases)
        file_name = r'D:\pythonProject\efsm\spectrumGeneration\MLS(250)\rate.csv'
        record['File'] = [SPEC_FILE]
        record['total failed'] = [failed_totalCount]
        record['rate(failed / total)'] = [failed_totalCount / num_cases]
        record.to_csv(file_name, mode='a', header=False, index=False, sep=',')





