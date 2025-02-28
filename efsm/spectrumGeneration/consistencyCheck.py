import copy
import time
import pandas as pd
import numpy as np
import os
import gc
from efsm.EFSMparser.load import LoadEFSM
from efsm.spectrumGeneration.utility import read_csv_all_test_suite, all_path


if __name__ == '__main__':
    start_time = time.time()

    MUT_files = all_path(r'/Mutation/RM2_MUT')                               # !!!
    file_path = '/PathGeneration/modelTrace/modelTrace_RM2(250)_random.csv'       # !!!
    test_suite, num_cases = read_csv_all_test_suite(file_path)

    record = pd.DataFrame(np.zeros([0, 3]))
    record.columns = ['File', 'total failed', 'rate(failed / total)']

    for SPEC_FILE in MUT_files:
        print(SPEC_FILE, "------------------------------")
        # l = LoadEFSM()

        '''dataframe'''
        failed_totalCount = 0

        file_name = r'D:\pythonProject\efsm\spectrumGeneration\temp_trace\traceInfo_{0}.csv'.format(SPEC_FILE)

        if not os.path.exists(file_name):
            df_init = pd.DataFrame(columns=['testcase_index', 'trace', 'Passed/Failed'])
            df_init.to_csv(file_name, mode='w', header=True, index=False, sep=',')

        for index_ts, test_cases in enumerate(test_suite):

            failed_count = 0
            print("This testsuite has total testcases: ", len(test_cases))
            print(".....Checking.....")

            start, end = 1, 250
            No_index = start
            for index_tc, tc in enumerate(test_cases[start-1:end], start=start):

                print("tc", index_tc, ".................")
                No_index += 1

                l = LoadEFSM()
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
                        context_vars = cur_sc_obj.get_cur_context().copy()
                        inp_params_val = cur_sc_obj.get_cur_input_params().copy()
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
                    flag_result = 'Failed'
                else:
                    flag_result = 'Passed'

                df_new = pd.DataFrame(
                    {'testcase_index': [No_index-1], 'trace': [test_cases_trace], 'Passed/Failed': [flag_result]})
                df_new.to_csv(file_name, mode='a', header=False, index=False, sep=',')

            print(".....Done.....")
            # print("failed_count: {0}\n".format(failed_count))
            failed_totalCount += failed_count

        print("total failed: ", failed_totalCount)
        print("rate : failed / total = ", failed_totalCount / num_cases)
        file_name = r'D:\pythonProject\efsm\spectrumGeneration\RM2(250)\rate.csv'        # !!!
        record['File'] = [SPEC_FILE]
        record['total failed'] = [failed_totalCount]
        record['rate(failed / total)'] = [failed_totalCount / num_cases]
        record.to_csv(file_name, mode='a', header=False, index=False, sep=',')

        end_time = time.time()
        elapsed_time = (end_time - start_time) / 60
        print(f"current_total_runtime: {elapsed_time:.6f} mins\n")





