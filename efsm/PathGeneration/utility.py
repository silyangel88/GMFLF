# coding=utf-8
import pandas as pd
import configparser
import os
import csv

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

def write_to_csv(ts, target_trans, model_name):
    target_path = []
    path = []
    c_val = []
    i_val = []
    sc_val = []
    trace_val = []
    output_val = []
    index_val = []
    input_event_val = []
    if ts:
        for ind in range(len(ts['path'])):
            path.append(ts['path'][ind])
            c_val.append(ts['context'][ind])
            target_path.append(target_trans)
            i_val.append(ts['input'][ind])
            sc_val.append(ts['sc'][ind])
            trace_val.append(ts['trace'][ind])
            output_val.append(ts['output'][ind])
            input_event_val.append(ts['input_event'][ind])
            index_val.append(ind)

        dict_sc = {'index': index_val, 'trace': trace_val, 'input_val': i_val, 'output_event': output_val, 'input_event': input_event_val }
        df = pd.DataFrame(dict_sc)
        coverage_config = read_conf_C()

        file_name = 'modelTrace_{0}_{1}.csv'.format(model_name, coverage_config)            # !!!!

        if not os.path.exists(file_name):
            df.to_csv(file_name, mode='a', header=True, index=False)
        else:
            df.to_csv(file_name, mode='a', header=False, index=False)


def blank_line(model_name):
    dict_sc = {'index': ['']}
    df = pd.DataFrame(dict_sc)
    coverage_config = read_conf_C()
    # 插入空白行  保存路径
    file_name = 'modelTrace_{0}_{1}.csv'.format(model_name, coverage_config)
    # 保存 dataframe
    df.to_csv(file_name, mode='a', header=False, index=False, sep=',')


def read_int_conf_by_key(section, option):
    conf = configparser.ConfigParser()
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    conf.read(root_path + '/PathGeneration/config.conf', 'utf8')
    V = conf.getint(section, option)
    return V


def read_conf_C():
    conf = configparser.ConfigParser()
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    conf.read(root_path + '/PathGeneration/config.conf', 'utf8')
    C = conf.get('coverage_criterion', 'C')                                      # [coverage_criterion]  C = random
    return C


def read_conf_m():
    conf = configparser.ConfigParser()
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    conf.read(root_path + '/PathGeneration/config.conf', 'utf8')                                # LOAD model_name
    m = conf.get('model_name', 'm')
    return m



if __name__ == "__main__":
    print(read_conf_m())



