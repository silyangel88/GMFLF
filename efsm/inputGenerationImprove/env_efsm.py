# coding=utf-8
import sys
sys.path.append("/pzj/project/py/efsm/")

from efsm.EFSMparser.load import LoadEFSM

import numpy as np
import random

class EFSM(object):
    def __init__( self, iMin, iMax, modelName):
        self.efsm_obj = LoadEFSM().load_efsm(modelName)
        self.trainSet = self.efsm_obj.trans_guard_list
        self.n_actions = 2 * len(self.efsm_obj.inp_params)
        self.iMin = iMin
        self.iMax = iMax
        self.modelName = modelName
        self.multi_index=np.zeros(self.n_actions,dtype=np.int)

        self.t_re_covered = np.zeros(1,dtype=np.int)
        self.v_input = np.zeros(len(self.efsm_obj.inp_params),dtype=np.int)
        self.v_context = np.zeros(len(self.efsm_obj.context_vars),dtype=np.int)
        self.t_sequence_covered = np.zeros(80,dtype=np.int)
        self.s = np.concatenate((self.t_re_covered,self.compute_distance(self.t_re_covered[0])))
        self.n_features = len(self.s)
        self.initGuardsDetail()

        self.rewardList = []

    def resetT(self,T):
        self.iniInputVars()
        T = int(T[1:])
        self.t_re_covered = np.array([T])

        # 无法通用的地方1： 用于在训练单个变迁时初始化上下文变量的值 使其能够满足变迁条件
        # 解决办法:除非另设一个方法判断变迁的可执行性（不包括上下文变量的数据流判断）
        if self.modelName == 'INRES':
            if T == 16 or T == 17 or T == 4:
                self.efsm_obj.cur_sc.context_vars['counter'] = 4
            elif T == 10 or T == 3 or T == 14 or T == 11:
                self.efsm_obj.cur_sc.context_vars['counter'] = random.randint(0, 3)
            else:
                self.efsm_obj.cur_sc.context_vars['counter'] = random.randint(self.iMin, self.iMax)
            if T == 9:
                self.efsm_obj.cur_sc.context_vars['input'] = True
            else:
                _bool_var = random.randint(0, 1)
                if _bool_var == 0:
                    self.efsm_obj.cur_sc.context_vars['input'] = False
                else:
                    self.efsm_obj.cur_sc.context_vars['input'] = True

        _input_params_arr = []
        for key,value in self.efsm_obj.cur_sc.input_params.items():
            _input_params_arr.append(value)
        self.v_input = np.array(_input_params_arr)
        _context_vars_arr = []
        for key,value in self.efsm_obj.cur_sc.context_vars.items():
            _context_vars_arr.append(value)
        self.v_context = np.array(_context_vars_arr)
        self.t_sequence_covered = np.zeros(80, dtype=np.int)
        self.s = np.concatenate((self.t_re_covered, self.compute_distance(self.t_re_covered[0])))
        return self.s

    def iniInputVars(self):
        self.multi_index = np.zeros(self.n_actions, dtype=np.int)
        # 无法通用的地方2： 用于对输入变量中的布尔值初始化
        # 解决办法：能够给出输入变量的类型
        if self.modelName == 'INRES':
            for key,value in self.efsm_obj.cur_sc.input_params.items():
                if key == 'optional' or key == 'block':
                    _bool_var = random.randint(0, 1)
                    if _bool_var == 0:
                        self.efsm_obj.cur_sc.input_params.__setitem__(key, False)
                    else:
                        self.efsm_obj.cur_sc.input_params.__setitem__(key, True)
                else:
                    self.efsm_obj.cur_sc.input_params.__setitem__(key, random.randint(self.iMin,self.iMax))

    def ini_context_by_outer(self,context_var):
        _context_vars_arr = []
        for key,value in context_var.items():
            _context_vars_arr.append(value)
        self.v_context = np.array(_context_vars_arr)
        # _context_vars_arr = []
        # context_var_list = list(self.efsm_obj.cur_sc.context_vars)
        # for index in range(len(context_var)):
        #     self.efsm_obj.cur_sc.context_vars.__setitem__(context_var_list[index], context_var[index])
        #     _context_vars_arr.append(context_var[index])
        # self.v_context = np.array(_context_vars_arr)

    def initGuardsDetail(self):
        self.guardsDetail = []
        for tran_n in self.efsm_obj.trans_guard_list:
            self.guardsDetail.append(self.efsm_obj.get_guard_content(tran_n))
        return 0

    def compute_distance(self,tran_n):
        tran_n = 't'+str(tran_n)
        _input_params = {}
        for key, value in self.efsm_obj.cur_sc.input_params.items():
            if type(value) is bool:
                if value:
                    _input_params.__setitem__(key, 1)
                else:
                    _input_params.__setitem__(key, 0)
            else:
                _input_params.__setitem__(key, value)
        _context_vars = {}
        for key, value in self.efsm_obj.cur_sc.context_vars.items():
            if type(value) is bool:
                if value:
                    _context_vars.__setitem__(key, 1)
                else:
                    _context_vars.__setitem__(key, 0)
            else:
                _context_vars.__setitem__(key, value)

        # 无法通用的地方3： deviation的计算
        # 解决办法：
        # 循环原子表达式:
            # concerned_input_params 移到左边表达式
            # concerned_context_variables 和 常数 移到右边表达式
            # 计算右边表达式的值right_val
            # 如果是第一个原子表达式：
                # d[indexOf(concerned_input_params)]=right_val/len(concerned_input_params)
            # 否则：
                # 讲表达式连接符为AND的表达式移到前面，OR的移到后面
                # 表达式连接符如果是AND:
                    # d[indexOf(concerned_input_params)]=MAX(d[indexOf(concerned_input_params)]，right_val/len(concerned_input_params))
                # 表达式连接符如果是OR:
                    # d[indexOf(concerned_input_params)]=MIN(d[indexOf(concerned_input_params)]，right_val/len(concerned_input_params))
        # 有可能有的模型是从t0开始的啊
        d_arr = np.zeros(len(self.efsm_obj.inp_params), dtype=np.int)
        if tran_n not in self.efsm_obj.trans_guard_list:
            return d_arr
        else:
            guards_op = self.efsm_obj.get_guard_content(tran_n)
            guards = guards_op['atomicGuards']
            ops = guards_op['atomicOP']
            d_arr_matrix = [[0 for _ in range(len(d_arr))] for _ in range(len(guards))]
            for index in range(len(guards)):
                guard = guards[index]
                # if index == 0:
                left_=[]
                right_=[]
                left_val = 0
                right_val = 0
                for lt in guard['left']:
                    if lt['type']=='input':
                        left_.append(lt)
                        if lt['sign']=='+':
                            left_val+=_input_params[lt['name']]
                        elif lt['sign']=='-':
                            left_val-=_input_params[lt['name']]
                    else:
                        right_.append(lt)
                        if lt['sign']=='+':
                            if lt['type']=='context':
                                right_val+=_context_vars[lt['name']]
                            elif lt['type']=='constant':
                                if lt['name']==False:
                                    right_val +=0
                                elif lt['name']==True:
                                    right_val+=1
                                else:
                                    right_val+=lt['name']
                        elif lt['sign']=='-':
                            if lt['type'] == 'context':
                                right_val -= _context_vars[lt['name']]
                            elif lt['type'] == 'constant':
                                if lt['name'] == False:
                                    right_val -= 0
                                elif lt['name'] == True:
                                    right_val -= 1
                                else:
                                    right_val -= lt['name']
                for rt in guard['right']:
                    if rt['type']=='input':
                        left_.append(rt)
                        if rt['sign']=='+':
                            left_val+=_input_params[rt['name']]
                        elif rt['sign']=='-':
                            left_val-=_input_params[rt['name']]
                    else:
                        right_.append(rt)
                        if rt['sign']=='+':
                            if rt['type']=='context':
                                right_val+=_context_vars[rt['name']]
                            elif rt['type']=='constant':
                                if rt['name']==False:
                                    right_val +=0
                                elif rt['name']==True:
                                    right_val+=1
                                else:
                                    right_val+=rt['name']
                        elif rt['sign']=='-':
                            if rt['type'] == 'context':
                                right_val -= _context_vars[rt['name']]
                            elif rt['type'] == 'constant':
                                if rt['name'] == False:
                                    right_val -= 0
                                elif rt['name'] == True:
                                    right_val -= 1
                                else:
                                    right_val -= rt['name']
                if guard['op']=='=' or guard['op']=='>=' or guard['op']=='<=':
                    d_total = right_val-left_val
                elif guard['op']=='>':
                    d_total = right_val+1-left_val
                elif guard['op']=="<":
                    d_total = right_val-1-left_val
                elif guard['op']=='<>':
                    d_total = 0 if right_val!=left_val else 1
                _input_params_list = list(_input_params)
                for left_obj in left_:
                    d_arr_matrix[index][_input_params_list.index(left_obj['name'])]=d_total/len(left_)
            d_arr = d_arr_matrix[0]
            for op_index in range(len(ops)):
                if ops[op_index]=='&&':
                    for d_index in range(len(d_arr)):
                        d_arr_matrix[op_index][d_index]=\
                            d_arr_matrix[op_index][d_index] if abs(d_arr_matrix[op_index][d_index])>abs(d_arr_matrix[op_index+1][d_index]) else d_arr_matrix[op_index+1][d_index]
                        d_arr_matrix[op_index+1][d_index]=d_arr_matrix[op_index][d_index]
                        d_arr[d_index]= d_arr[d_index] if abs(d_arr[d_index]) > abs(d_arr_matrix[op_index+1][d_index]) else d_arr_matrix[op_index+1][d_index]
            for op_index in range(len(ops)):
                if ops[op_index]=='||':
                    for d_index in range(len(d_arr)):
                        d_arr[d_index] = \
                            d_arr_matrix[op_index][d_index] if (abs(d_arr_matrix[op_index][d_index]) <= abs(d_arr[d_index]) and d_arr_matrix[op_index][d_index]!=0) else d_arr[d_index]
                        d_arr[d_index]= \
                            d_arr[d_index] if (abs(d_arr[d_index])<abs(d_arr_matrix[op_index+1][d_index]) and d_arr[d_index]!=0) else d_arr_matrix[op_index+1][d_index]
            return d_arr

    def construct_state(self):
        _input_params_arr = []
        for key,value in self.efsm_obj.cur_sc.input_params.items():
            _input_params_arr.append(value)
        self.v_input = np.array(_input_params_arr)
        _context_vars_arr = []
        for key,value in self.efsm_obj.cur_sc.context_vars.items():
            _context_vars_arr.append(value)
        self.v_context = np.array(_context_vars_arr)
        self.s = np.concatenate((self.t_re_covered,self.compute_distance(self.t_re_covered[0])))
        return self.s

    def step(self, action):
        now_action_i = action
        v_i = int(now_action_i/2)
        t = self.t_re_covered[0]
        done = False
        concerned_input_params = self.efsm_obj.get_inp_params_by_trans_name('t'+str(t))
        _input_params_list = list(self.efsm_obj.inp_params)
        if _input_params_list[v_i] in concerned_input_params:
            done, reward = self.compute_reward3(t, now_action_i)
        else:
            reward = -len(self.s)

        s_ = self.construct_state()
        return s_, reward, done


    def compute_reward3(self, t, now_action_i):# f(x-1)-f(x)

        old_fit = self.t_fitness(t)
        v_i = int(now_action_i / 2)
        _input_params_list = list(self.efsm_obj.cur_sc.input_params)
        cur_param_val = self.efsm_obj.cur_sc.input_params[_input_params_list[v_i]]
        origin_val = cur_param_val
        if now_action_i % 2 == 0:
            if type(cur_param_val) is bool:
                cur_param_val = True
                self.efsm_obj.cur_sc.input_params.__setitem__(_input_params_list[v_i],
                                                              cur_param_val)
                new_fit = self.t_fitness(t)
            else:
                if cur_param_val == 0 or self.multi_index[now_action_i] == 1:
                    cur_param_val += 1
                else:
                    cur_param_val = cur_param_val * 2
                self.efsm_obj.cur_sc.input_params.__setitem__(_input_params_list[v_i],
                                                              cur_param_val)
                new_fit = self.t_fitness(t)
                if new_fit > old_fit:
                    self.multi_index[now_action_i] = 1
                    cur_param_val = origin_val + 1
                    self.efsm_obj.cur_sc.input_params.__setitem__(_input_params_list[v_i],
                                                                  cur_param_val)
                    new_fit = self.t_fitness(t)
        else:
            if type(cur_param_val) is bool:
                cur_param_val = False
                self.efsm_obj.cur_sc.input_params.__setitem__(_input_params_list[v_i],
                                                              cur_param_val)
                new_fit = self.t_fitness(t)
            else:
                if cur_param_val == 0 or self.multi_index[now_action_i]==1:
                    cur_param_val -= 1
                else:
                    cur_param_val = random.randint(cur_param_val // 2,cur_param_val // 2+1)
                self.efsm_obj.cur_sc.input_params.__setitem__(_input_params_list[v_i],
                                                              cur_param_val)
                new_fit = self.t_fitness(t)
                if new_fit > old_fit:
                    self.multi_index[now_action_i] = 1
                    cur_param_val = origin_val - 1
                    self.efsm_obj.cur_sc.input_params.__setitem__(_input_params_list[v_i],
                                                                  cur_param_val)
                    new_fit = self.t_fitness(t)

        # self.efsm_obj.cur_sc.input_params.items()[v_i][1] = cur_param_val

        zero_count = 0
        for ii in range(1, len(self.s)):
            if self.s[ii] == 0:
                zero_count += 1
        if new_fit > old_fit:
            ft = -1-(len(self.s)-1-zero_count)
        elif new_fit == old_fit:
            ft = 0
        else:
            ft = 1 + zero_count

        self.rewardList.append(ft)

        if self.t_execute('t'+str(t)):
            done = True
        else:
            done = False

        return done, ft


    def t_execute(self,tran_n):
        _input_params = {}
        for key, value in self.efsm_obj.cur_sc.input_params.items():
            _input_params.__setitem__(key, value)
        _context_vars = {}
        for key, value in self.efsm_obj.cur_sc.context_vars.items():
            _context_vars.__setitem__(key, value)
        self.efsm_obj.cur_sc.update_sc(self.efsm_obj.cur_sc.cur_state,_context_vars,_input_params,tran_n)
        cur_transition = self.efsm_obj.trans_name_map[tran_n]
        done = self.efsm_obj.is_feasible(cur_transition,self.efsm_obj.get_cur_sc())
        return done

    #a归一化函数
    def norm(self,originReward):
        # if originReward != 0:
        #     normReward = 1-1/(math.pow(1.05,originReward))
        # else:
        #     normReward = originReward
        # self.rewardList.append(originReward)
        # return normReward
        return originReward

    def plotReward(self):#display the originial rewards
        import matplotlib.pyplot as plt
        plt.plot(np.arange(len(self.rewardList)), self.rewardList)
        plt.ylabel('rewards')
        plt.xlabel('steps')
        plt.show()


    def t_fitness(self, tran_n): #只需判断 条件中包含输入变量的情况
        tran_n = 't'+str(tran_n)
        _input_params = {}
        for key, value in self.efsm_obj.cur_sc.input_params.items():
            if type(value) is bool:
                if value:
                    _input_params.__setitem__(key, 1)
                else:
                    _input_params.__setitem__(key, 0)
            else:
                _input_params.__setitem__(key, value)
        _context_vars = {}
        for key, value in self.efsm_obj.cur_sc.context_vars.items():
            if type(value) is bool:
                if value:
                    _context_vars.__setitem__(key, 1)
                else:
                    _context_vars.__setitem__(key, 0)
            else:
                _context_vars.__setitem__(key, value)
        # 无法通用的地方4： fitness的计算
        # 将每个表达式的输入变量移至左边，上下文变量和常数移至右边，fitness = abs（右边值-左边值）+1
        # and连接取和
        # or连接取min
        # op为≠或者右边变量中有布尔值，则另外考虑
        if tran_n not in self.efsm_obj.trans_guard_list:
            return 0
        else:
            guards_op = self.efsm_obj.get_guard_content(tran_n)
            guards = guards_op['atomicGuards']
            ops = guards_op['atomicOP']
            fit_arr = [0 for _ in range(len(guards))]
            for index in range(len(guards)):
                guard = guards[index]
                # if index == 0:
                left_=[]
                right_=[]
                left_val = 0
                right_val = 0
                for lt in guard['left']:
                    if lt['type']=='input':
                        left_.append(lt)
                        if lt['sign']=='+':
                            left_val+=_input_params[lt['name']]
                        elif lt['sign']=='-':
                            left_val-=_input_params[lt['name']]
                    else:
                        right_.append(lt)
                        if lt['sign']=='+':
                            if lt['type']=='context':
                                right_val+=_context_vars[lt['name']]
                            elif lt['type']=='constant':
                                if lt['name']==False:
                                    right_val +=0
                                elif lt['name']==True:
                                    right_val+=1
                                else:
                                    right_val+=lt['name']
                        elif lt['sign']=='-':
                            if lt['type'] == 'context':
                                right_val -= _context_vars[lt['name']]
                            elif lt['type'] == 'constant':
                                if lt['name'] == False:
                                    right_val -= 0
                                elif lt['name'] == True:
                                    right_val -= 1
                                else:
                                    right_val -= lt['name']
                for rt in guard['right']:
                    if rt['type']=='input':
                        left_.append(rt)
                        if rt['sign']=='+':
                            left_val+=_input_params[rt['name']]
                        elif rt['sign']=='-':
                            left_val-=_input_params[rt['name']]
                    else:
                        right_.append(rt)
                        if rt['sign']=='+':
                            if rt['type']=='context':
                                right_val+=_context_vars[rt['name']]
                            elif rt['type']=='constant':
                                if rt['name']==False:
                                    right_val +=0
                                elif rt['name']==True:
                                    right_val+=1
                                else:
                                    right_val+=rt['name']
                        elif rt['sign']=='-':
                            if rt['type'] == 'context':
                                right_val -= _context_vars[rt['name']]
                            elif rt['type'] == 'constant':
                                if rt['name'] == False:
                                    right_val -= 0
                                elif rt['name'] == True:
                                    right_val -= 1
                                else:
                                    right_val -= rt['name']
                if guard['op']=='<>':
                    fit_val = 0 if right_val!=left_val else 1
                else:
                    fit_val = abs(right_val-left_val)+1 if right_val-left_val!=0 else 0
                if len(left_)!=0:
                    fit_arr[index] = fit_val
                _input_params_list = list(_input_params)
            fit_total = fit_arr[0]
            for op_index in range(len(ops)):
                if ops[op_index]=='&&':
                    fit_arr[op_index] = fit_arr[op_index+1] =fit_arr[op_index]+fit_arr[op_index+1]
                if op_index!=0:
                    fit_total = fit_total+fit_arr[op_index]
            for op_index in range(len(ops)):
                if ops[op_index]=='||':
                    fit_total = min(fit_total,fit_arr[op_index])
                    fit_total = min(fit_total, fit_arr[op_index+1])
            return fit_total
