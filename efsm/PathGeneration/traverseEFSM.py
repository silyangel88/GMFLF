# coding=utf-8
import queue
import copy
import random
from efsm.inputGenerationImprove.IPSG import IPS_Generation
from efsm.PathGeneration.utility import write_to_csv, blank_line, read_conf_C, read_int_conf_by_key


class Generation(object):
    def __init__(self, _efsm):
        self.epoch = read_int_conf_by_key('max_generation_count', 'mgc')
        self.max_level = 30
        self.model_name = _efsm.model_name
        self.inpParam_in_inpEvent = _efsm.get_inpParam_in_inpEvent()
        self.C = read_conf_C()
        self.IPSG = IPS_Generation(self.model_name)

    def _update_input_by_ips(self, cur_sc, cur_transition_name, efsm):
        if cur_transition_name in efsm.get_inpParam_in_inpEvent():
            _cur_trans_num = int(cur_transition_name[1:])
            context_vars = cur_sc.get_cur_context()
            inp_params_val = cur_sc.get_cur_input_params()
            input_params = self.IPSG.generate(_cur_trans_num, context_vars)
            if input_params:
                cur_sc.set_cur_input_params(input_params)
                return True
            else:
                return False
            #print(input_params)
        else:
            return True

    def _dfs_traverse(self, efsm, target_coverage, ts_count):
        print("-----------start-DFS------------{}-----".format(ts_count))
        print("====================coverage================")
        sc_stack = []
        test_case_pool = []
        sc = efsm.get_cur_sc()
        sc_stack.append(sc)
        flag_first = True
        while len(sc_stack):
            top_sc = sc_stack.pop()
            _is_finded = self._random_coverage(target_coverage, top_sc.input_pool)
            if _is_finded:
                print("-----------end--------------{}----\n".format(ts_count))
                ts_count = ts_count - 1

                return top_sc
            cur_state = top_sc.get_cur_state()
            if cur_state == efsm.get_init_state():
                efsm.init_sc_val(top_sc)
            _transitionList = efsm.get_next_trans(cur_state, list_flag=True)
            _transitionList = copy.deepcopy(_transitionList)
            if not _transitionList:
                continue
            _trans_size = len(_transitionList)
            while _trans_size:
                _trans_size = _trans_size - 1
                _cur_transition = random.choice(_transitionList)
                _transitionList.remove(_cur_transition)
                if _cur_transition:
                    _tmpsc = copy.deepcopy(top_sc)
                    update_input_flag = self._update_input_by_ips(_tmpsc, _cur_transition.trans_name, efsm)
                    if not update_input_flag:
                        continue
                    if not efsm.is_feasible(_cur_transition, _tmpsc):
                        continue
                    efsm.execute(_cur_transition, _tmpsc)
                    context_vars = _tmpsc.get_cur_context()
                    inp_params_val = _tmpsc.get_cur_input_params()
                    output_event = efsm.update_transition_output(_cur_transition, context_vars, inp_params_val)
                    input_event = _cur_transition.get_inp_event()
                    _tmpsc.update_sc(_cur_transition.t_state, context_vars, inp_params_val,
                                     _cur_transition.trans_name, output_event, input_event)
                    sc_stack.append(_tmpsc)
                    break

    def _bfs_traverse(self, efsm, target_coverage):
        threshold = 6
        _path = None
        print("-----------start-BFS------------{}-----".format(self.epoch))
        print("====================coverage================")
        _is_finded = False
        _cur_level = 0
        find_size = 0
        _collection = set()

        sc = efsm.get_cur_sc()
        sc_queue = queue.Queue()
        sc_queue.put(sc)

        while not sc_queue.empty() and _cur_level <= self.max_level and find_size < threshold and not _is_finded:
            que_length = len(sc_queue.queue)

            _tmp_sc_queue = copy.deepcopy(sc_queue.queue)
            _tmp_list = []
            _is_finded = False
            if self.C == "all_transition":
                _collection = set()

            while len(_tmp_sc_queue) and not _is_finded:
                _ts = _tmp_sc_queue.pop()
                _tmp_list.append(_ts)
                # judge coverage
                if self.C == "all_state":
                    _collection = _collection.union(_ts.get_cur_state().split())
                    if len(_collection) >= len(target_coverage):
                        _is_finded = self._all_state_coverage(target_coverage, _collection)
                elif self.C == "all_transition":
                    _collection = _collection.union(set(_ts.transition_path))
                    if len(_collection) >= len(target_coverage):
                        _is_finded = self._all_transition_coverage(target_coverage, _collection)
                elif self.C == "random":
                    _collection = _ts.transition_path
                    _is_finded = self._random_coverage(target_coverage, _collection)
                    if _is_finded:
                        while len(_tmp_sc_queue):
                            _ts = _tmp_sc_queue.pop()
                            _tmp_list.append(_ts)
                if _is_finded:
                    find_size += 1
                    print("-----------end--------------{}----\n".format(self.epoch))
                    self.epoch = self.epoch - 1
                    return _tmp_list

            while que_length > 0 and find_size < threshold and not _is_finded:
                que_length -= 1
                top_sc = sc_queue.get()
                cur_state = top_sc.get_cur_state()
                if cur_state == 's1':
                    efsm.init_sc_val(top_sc)
                _transitionList = efsm.get_next_trans(cur_state, list_flag=True)
                _transitionList = copy.deepcopy(_transitionList)
                if not _transitionList:
                    continue
                _trans_size = len(_transitionList)

                while _trans_size:
                    _trans_size = _trans_size - 1
                    if _is_finded:
                        break
                    _cur_transition = random.choice(_transitionList)
                    _transitionList.remove(_cur_transition)
                    if _cur_transition:
                        # if top_sc.transition_path and _cur_transition.trans_name == top_sc.transition_path[-1]:
                        #     continue

                        _tmpsc = copy.deepcopy(top_sc)

                        update_input_flag = self._update_input_by_ips(_tmpsc, _cur_transition.trans_name, efsm)
                        if not update_input_flag:
                            continue
                        if not efsm.is_feasible(_cur_transition, _tmpsc):
                            continue
                        efsm.execute(_cur_transition, _tmpsc)
                        context_vars = _tmpsc.get_cur_context()
                        inp_params_val = _tmpsc.get_cur_input_params()
                        output_event = efsm.update_transition_output(_cur_transition, context_vars, inp_params_val)
                        input_event = _cur_transition.get_inp_event()
                        _tmpsc.update_sc(_cur_transition.t_state, context_vars, inp_params_val,
                                         _cur_transition.trans_name, output_event, input_event)
                        # _cur_transition.set_sc(_tmpsc)
                        sc_queue.put(_tmpsc)
            _cur_level += 1

        print("-----------end--------------{}----\n".format(self.epoch))
        self.epoch = self.epoch - 1
        return None

    def _all_state_coverage(self, target, current):
        target_state = set(target)
        current_state = set(current)
        if target_state >= current_state:
            return True
        else:
            return False

    def _all_transition_coverage(self, target, current):
        target_path = set(target)
        current_path = set(current)
        if target_path >= current_path:
            return True
        else:
            return False

    def _random_coverage(self, max_len, current):
        if len(current) >= max_len:
            return True
        else:
            return False

    def _traverse(self, efsm_t):
        if self.C == "all_state":
            target_coverage = efsm_t.states_table
        elif self.C == "all_transition":
            target_coverage = efsm_t.trans_list
        elif self.C == "random":
            target_coverage = random.randint(int(len(efsm_t.trans_list) * 0.1), int(len(efsm_t.trans_list) * 0.2))
        test_suite_list = []

        _efsm_t = copy.deepcopy(efsm_t)
        while self.epoch:
            _sc_pool = []
            if self.C == "random":
                _random_count = 250
                while _random_count:

                    target_coverage = random.randint(int(len(efsm_t.trans_list) * 0.1),
                                                     int(len(efsm_t.trans_list) * 0.2))
                    print('trace_length: '+ str(target_coverage))
                    _tc = self._dfs_traverse(_efsm_t, target_coverage, _random_count)       # DFS
                    if _tc:
                        _sc_pool.append(_tc)
                        _random_count -= 1
                self.epoch -= 1
            else:
                _sc_pool = self._bfs_traverse(_efsm_t, target_coverage)                     # BFS
            if len(_sc_pool):
                _test_suite = []
                for sc in _sc_pool:
                    ts = {}
                    _context = sc.context_pool
                    _input = sc.input_pool
                    _state = sc.state_pool
                    _path = sc.transition_path
                    _output = sc.output_pool
                    _input_event = sc.input_event_pool
                    _trace = []
                    _sc = []
                    for ind in range(len(_state)):
                        _tmp_sc = []
                        _tmp_sc.append(_state[ind])
                        for key, val in _context[ind].items():
                            _tmp_sc.append(val)
                        for key, val in _input[ind].items():
                            _tmp_sc.append(val)
                        _sc.append(tuple(_tmp_sc))

                    for ind in range(len(_path)):
                        _tmp_trace = []
                        for j in range(ind+1):
                            _tmp_trace.append(_path[j])
                        _trace.append(_tmp_trace)
                    _test_suite.append(sc.transition_path)

                    ts.__setitem__('context', _context)
                    ts.__setitem__('input', _input)
                    ts.__setitem__('path', _path)
                    ts.__setitem__('sc', _sc)
                    ts.__setitem__('trace', _trace)
                    ts.__setitem__('output', _output)
                    ts.__setitem__('input_event', _input_event)

                    write_to_csv(ts, target_coverage, self.model_name)

                print("one test suite write csv.......")
                blank_line(self.model_name)
                test_suite_list.append(_test_suite)
        return test_suite_list

    def run(self, efsm):
        return self._traverse(efsm)
