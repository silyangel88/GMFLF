# coding=utf-8
import pandas as pd
import csv
import os


def read_csv_all_test_suite(file_path):
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = root_path + file_path
    data = []
    import ast
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)

        test_suite = []
        test_case = []
        tc_visited = set()
        num_cases = 0
        for row in reader:
            t = dict(row)
            if t.get('index'):
                t.update(index=int(t.get('index')))
                t.update(trace=ast.literal_eval(t.get('trace')))
                t.update(input_val=ast.literal_eval(t.get('input_val')))
                if t.get('index') in tc_visited:
                    test_suite.append(test_case)
                    tc_visited = set()
                    test_case = []
                test_case.append(t)
                tc_visited.add(t.get('index'))
            else:
                test_suite.append(test_case)
                data.append(test_suite)
                print("a test suite...num_testcases：", len(test_suite))
                num_cases += len(test_suite)
                test_suite = []
                test_case = []
                tc_visited = set()

    return data, num_cases


def all_path(dirname):
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = root_path + dirname
    result = []

    for maindir, subdir, file_name_list in os.walk(file_path):
        for filename in file_name_list:

            last_dot_index = filename.rfind('.')
            result_name = filename[:last_dot_index]
            result.append(result_name)

    return result


def blank_line(f_name):
    dict1 = {'score_list': [''], 'test_suite': [''], 'sd': ['']}
    df = pd.DataFrame(dict1)
    df.to_csv(f_name, mode='a', header=False, index=False)

