# coding=utf-8
import time
from efsm.inputGenerationImprove.RL_brain import DuelingDQN
from efsm.inputGenerationImprove.env_efsm import EFSM
import os

dir_name = os.path.dirname(__file__)

outDetail = True #输出明细

def training_model(MaxEpisode,trainBudget, trainSet,modelPath,fromModel,saveModel):
    if (fromModel):
        RL.restore_RL(modelPath)
        print('restore the model')
    print('training...')
    i_max_T = len(trainSet)
    episode = 0
    episode_step_arr = []
    averaged_reward = [] #用于记录一个episode里的平均reward，数组长度等于初始化不满足谓词条件的episode数，小于或等于MaxEpisode
    start_time = time.time()
    while episode < MaxEpisode:
        step = 0
        reward_sum = 0 #由于初始化就满足谓词条件的情况没有reward统计，所以averaged_reward的数量小于maxEpisode
        v_i = episode % i_max_T
        t = trainSet[v_i]
        episode_step = 0
        # initial observation
        observation = env.resetT(t)
        success = 'yes'

        if env.t_execute(t):
            episode_step = episode_step + 1

            if outDetail:
                print("===================2. episode:%s,episode_step:%s,tran:%s===================" % (episode,episode_step, t))
                print(env.efsm_obj.cur_sc.input_params)
                print(env.efsm_obj.cur_sc.context_vars)
        else:
            while True:
                episode_step = episode_step + 1
                if outDetail:
                    print("===================2. episode:%s,episode_step:%s,tran:%s===================" % (episode,episode_step, t))
                    print(env.efsm_obj.cur_sc.input_params)
                    print(env.efsm_obj.cur_sc.context_vars)
                # RL choose action based on observation
                print('observation:%s'%(observation))
                action = RL.choose_action(observation)

                # RL take action and get next observation and reward
                observation_, reward, done = env.step(action)
                reward_sum += reward
                print("action:%s->reward:%s"%(action,reward))

                observation_ = env.construct_state()
                RL.store_transition(observation, action, reward, observation_)
                step += 1

                if (step > 20) and (step % 1 == 0):
                    RL.learn()
                # swap observation
                observation = observation_
                if episode_step > trainBudget:
                    done = True
                    success = 'no'
                # break while loop when end of this episode
                if done:
                    break

                # print("episode:%s,step:%s,action:%s,optional:%s,Num:%s,block:%s,counter:%s,input:%s,number:%s" % (episode, step, action,env.g_optional,env.g_NUM,env.g_block,env.g_counter,env.g_input,env.g_number))
            if success == 'yes':
                averaged_reward.append(reward_sum/episode_step)
                episode_step_arr.append(episode_step)
        print("episode:%s finish,step:%s, T%s, success:%s"%(episode+1,episode_step,t,success))

        episode += 1

    print('training over')
    if (saveModel):
        RL.save_RL(modelPath)
        print('save the net to ',modelPath)


if __name__ == "__main__":
    modelName = 'INRES'
    env = EFSM(0,5,modelName)
    RL = DuelingDQN(env.n_actions, env.n_features,
                      learning_rate=0.01,
                      reward_decay=0.9,
                      e_greedy=0.9,
                      replace_target_iter=100,
                      memory_size=1000,
                      # output_graph=True
                      )
    modelPath_Dueling = os.path.join(dir_name, 'models/'+modelName+'/net.ckpt')
    training_model(10000, 10000, env.trainSet,modelPath_Dueling,False,True)