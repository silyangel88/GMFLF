from efsm.EFSMparser.load import LoadEFSM
import random
import numpy as np

if __name__ == '__main__':
    efsm_obj = LoadEFSM().load_efsm('SCP')
    for item in efsm_obj.inp_params.items():
        item[1]['value'] = random.randint(0,200)
    efsm_obj.inp_params['optional']['value'] = False

    _input_params = {}
    for key, value in efsm_obj.inp_params.items():
        _input_params.__setitem__(key, value['value'])

    temp = []
    for item in efsm_obj.inp_params.items():
        temp.append(item[1]['value'])
    v_input = np.array(temp)
    temp_context = []
    for item in efsm_obj.context_vars.items():
        temp_context.append(item[1]['value'])
    v_context = np.array(temp_context)
    concerned_input_params = efsm_obj.get_inp_params_by_trans_name('t10')
    if efsm_obj.inp_params.items()[2][0] in concerned_input_params:
        print('yes')
    cur_transition = efsm_obj.trans_name_map['t7']
    _context_vars = {}
    for key, value in efsm_obj.context_vars.items():
        _context_vars.__setitem__(key, value['value'])
    efsm_obj.cur_sc.update_sc(efsm_obj.cur_sc.cur_state, _context_vars,
                                   _input_params, 't7')
    sc = efsm_obj.get_cur_sc()
    done = efsm_obj.is_feasible(cur_transition, sc)
    print(efsm_obj.cur_sc.input_params['optional'])
    print('ff')