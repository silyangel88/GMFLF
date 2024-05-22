import numpy as np
import pandas as pd
import os
import re

''' 
生成 RankLib 格式文件 , 测试命令文件
1、 修改 transitioncount 
2、 trainTxt() faultpos参数判断   (i + 1) == faultpos transition从1开始，不包含class2
3、 数据文件路径 TrainFiles TestFiles
4、 修改formulaset
5、 文件保存位置更改
6、 命令修改和保存位置修改
'''


''' 读取文件夹文件列表 '''
def all_path(file_path):

    result = []  # 所有的文件

    for maindir, subdir, file_name_list in os.walk(file_path):
        for filename in file_name_list:
            result.append(filename)
    # print(result)
    return result


''' 读取单个怀疑度表 '''
def readCSV(csvFile):

    dataset = pd.read_csv(csvFile)
    dataset = dataset.values          # dataframe 转 ndarray
    dataset = dataset[:, 1:]          # 使用切片来删除第一列
    # dataset = dataset[:, :dim]            # 取前xx列
    # print(dataset)
    return dataset


def combineColumn(formulaset, dataset, transitioncount):
    """ 抽取指定列 formulaset下标是从1开始"""
    matrix = np.zeros([transitioncount, len(formulaset)])
    for i in range(len(formulaset)):
        index = formulaset[i] - 1           # formulaset 公式下标是从1开始
        matrix[:, i] = dataset[:, index]

    # 数据0-1标准化
    matrix = pd.DataFrame(matrix)
    matrix = matrix.apply(lambda x: (x - np.min(x)) / (np.max(x) - np.min(x)))
    # print(matrix)
    return matrix.values


def faultPos(csvFile):
    """ 获取文件名字符串中的错误位置 """
    # 使用正则表达式匹配数字
    match = re.search(r'T(\d+)', csvFile)
    faultPos = match.group(1)         # group(1) 来获取捕获的数字部分
    return int(faultPos)


def trainTxt(formulaset, TrainRoot, dataFiles, transitioncount):
    strText = []

    id = 1
    for csvFile in dataFiles:

        faultpos = faultPos(csvFile)
        filename = TrainRoot + '\\' + csvFile
        dataset = readCSV(filename)
        matrix = combineColumn(formulaset, dataset, transitioncount)

        for i in range(transitioncount):
            # 开头id
            strline = ''
            # if i == faultpos:
            if (i + 1) == faultpos:             # (i + 1) == faultpos transition从1开始，不包含class2  !!!
                strline += "1 qid:" + str(id)          # 错误语句标注1
            else:
                strline += "0 qid:" + str(id)

            for j in range(len(formulaset)):
                strline += " " + str(formulaset[j]) + ":"
                strline += format(matrix[i, j], '6f')                 # 格式化，到六位小数

            strText.append(strline)

        id += 1

    # 指定文件名和打开模式（'w' 表示写入模式，如果文件不存在将创建文件，如果文件已存在将覆盖内容）
    file_name = r"D:\桌面资料\学习资料\研究生\pythonProject\RandomForest\class2(250)\KWOA_RN\KWOA_train_class2.txt"                # 保存路径！！！！

    # 打开文件并写入多行文字
    with open(file_name, 'w', encoding='utf-8') as file:
        for line in strText:
            file.write(line + '\n')
    print(f"已成功写入Train文件: {file_name}")

    return 0


def TestTxt(formulaset, TestRoot, Files, transitioncount):

    cmdText = []
    id = 1

    for File in Files:
        strText = []
        filename = TestRoot + '\\' + File
        dataset = readCSV(filename)
        matrix = combineColumn(formulaset, dataset, transitioncount)

        for i in range(transitioncount):
            # 开头id
            strline = "0 qid:" + str(id)

            for j in range(len(formulaset)):
                strline += " " + str(formulaset[j]) + ":"
                strline += format(matrix[i, j], '6f')                 # 格式化，到六位小数

            strText.append(strline)

        # 使用正则表达式提取中间部分
        match = re.search(r'_(.*?)\.', File)
        result_name = match.group(1)

        # 指定文件名和打开模式（'w' 表示写入模式，如果文件不存在将创建文件，如果文件已存在将覆盖内容）
        file_name = r'D:\桌面资料\学习资料\研究生\pythonProject\RandomForest\class2(250)\KWOA_RN\KWOA_test_{0}.txt'.format(result_name)    # 保存路径！！！！

        # 命令
        cmdline = 'java -jar bin/RankLib.jar -load RQ3_KWOA_RN_modelclass2.txt -rank Test/KWOA_test_{0}.txt -score ScoreFile/KWOA_ScoreFile_{0}.txt'.format(result_name)    # 保存路径！！！！
        cmdText.append(cmdline)

        # 打开文件并写入多行文字
        with open(file_name, 'w', encoding='utf-8') as file:
            for line in strText:
                file.write(line + '\n')
        print(f"已成功写入Test文件: {file_name}")

    # 保存命令
    cmdName = r'D:\桌面资料\学习资料\研究生\pythonProject\RandomForest\class2(250)\KWOA_RN\cmd.txt'
    with open(cmdName, 'w', encoding='utf-8') as file:
        for line in cmdText:
            file.write(line + '\n')
    print(f"已成功写入测试命令文件: {cmdName}")

    return 0


if __name__ == "__main__":

    formulaset = [24, 5, 1247, 1526, 1011, 8, 9]               # 公式集  ！！！！
    # formulaset = [1, 2, 3, 4, 5, 6, 7]      # 最大SBFL公式！！！
    '''transitionNum: 
     class2_mut-21; ATM_mut-30; Network_mut-17; INRES_mut-18; OLSR_mut -23; InFlight_mut -32; SIP_mut -57; MLS_mut -81
    '''
    transitioncount = 21                                            # 修改transition数  ！！！！

    ''' Train文件 '''
    print("生成Train文件")
    TrainRoot = r"D:\桌面资料\学习资料\研究生\pythonProject\WOA_modelSpectrum\class2(250)\TrainSusp"
    # TrainRoot = r"D:\桌面资料\学习资料\研究生\pythonProject\WOA_modelSpectrum\InFlight(250)\MaximalSusp"   # 最大SBFL公式！！！
    dataFiles = all_path(TrainRoot)
    trainTxt(formulaset, TrainRoot, dataFiles, transitioncount)

    ''' Test文件 '''
    print("生成Test文件和测试命令文件")
    TestRoot = r'D:\桌面资料\学习资料\研究生\pythonProject\WOA_modelSpectrum\class2(250)\TestSusp'
    # TestRoot = r'D:\桌面资料\学习资料\研究生\pythonProject\WOA_modelSpectrum\InFlight(250)\MaximalSusp_Test'   # 最大SBFL公式！！！
    Files = all_path(TestRoot)
    TestTxt(formulaset, TestRoot, Files, transitioncount)

