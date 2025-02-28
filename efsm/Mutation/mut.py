# coding=utf-8
import random
import os
from efsm.Mutation.utility import read_json_file, write_json_file
from efsm.Mutation.operator_replace import Operator


dir_name = os.path.dirname(os.getcwd())
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_efsm_mutation(iteration, specification_name, efsm_obj=None, mutation_type='DecisionMUT'):
    json_name = 'Specification/{0}.json'.format(specification_name)
    file_name = os.path.join(root_path, json_name)

    t_list = read_json_file(file_name)
    op = Operator(efsm_obj)

    operations = ["guardMut", "actionMut"]
    while True:
        flag = False

        indices = [0, 8, 10, 11, 25, 26, 20, 68, 50, 40, 75]                 # index list
        T_index = random.choice(indices)
        random_T = t_list[T_index]

        guard = random_T.get('guard')
        action = random_T.get('action')

        if guard == '' and action == '':
            continue

        elif guard != '' and action != '':
            selected_operation = random.choice(operations)
            if selected_operation == "guardMut":
                guard, flag = op.mutate(guard)
                t_list[T_index]['guard'] = guard
            else:
                action, flag = op.mutate(action)
                t_list[T_index]['action'] = action

        elif guard != '':
            guard, flag = op.mutate(guard)
            t_list[T_index]['guard'] = guard

        elif action != '':
            action, flag = op.mutate(action)
            t_list[T_index]['action'] = action

        if flag:
            break

    faultTransition = T_index + 1
    # faultTransition = T_index               # class2   !!!!
    mut_name = 'Mutation/try/{0}Mut{1}_T{2}.json'.format(specification_name, iteration, faultTransition)

    file_name = os.path.join(dir_name, mut_name)
    write_json_file(file_name, t_list)


