# coding=utf-8
from efsm.inputGenerationImprove.RL_brain import DuelingDQN
from efsm.inputGenerationImprove.env_efsm import EFSM
import numpy as np
import os

dir_name = os.path.dirname(__file__)


class IPS_Generation(object):
    def __init__(self,modelName):
        self.modelName = modelName
        self.outDetail = False # 输出明细
        self.env = EFSM(1,60,self.modelName)
        self.agent = DuelingDQN(self.env.n_actions, self.env.n_features,
                        learning_rate=0.01,
                        reward_decay=0.9,
                        e_greedy=0.9,
                        replace_target_iter=100,
                        memory_size=1000
                        )
        self.modelPath = os.path.join(dir_name, 'models/'+modelName+'/net.ckpt')
        self.IPS = self.env.efsm_obj.cur_sc.input_params


    def generate(self, transition, context_variables_arr):
        self.agent.restore_RL(self.modelPath)
        self.env.t_re_covered = np.array([transition])
        self.env.iniInputVars()  # 如何设定初始值
        self.env.ini_context_by_outer(context_variables_arr)
        observation = self.env.construct_state()
        self.IPS = self.env.efsm_obj.cur_sc.input_params
        limit = 500
        if self.env.t_execute('t'+str(transition)):
            if self.outDetail == True:
                print('skip')
            return self.IPS
        else:
            while limit:
                limit -= 1
                if self.outDetail == True:
                    print('generating')
                    print(limit)
                    print(self.env.efsm_obj.cur_sc.input_params)
                    print(self.env.efsm_obj.cur_sc.context_vars)
                action = self.agent.choose_action(observation)
                observation_, reward, done = self.env.step(action)
                observation_ = self.env.construct_state()
                if done:
                    self.IPS = self.env.efsm_obj.cur_sc.input_params
                    return self.IPS

                observation = observation_

        return None


