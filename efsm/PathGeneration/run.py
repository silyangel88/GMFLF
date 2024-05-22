# coding=utf-8
from efsm.EFSMparser.load import LoadEFSM
from efsm.PathGeneration.traverseEFSM import Generation as G2
from efsm.PathGeneration.utility import read_conf_m



if __name__ == "__main__":
    SPEC_FILE = read_conf_m()
    l = LoadEFSM()
    efsm_obj = l.load_efsm(SPEC_FILE)
    #efsm_obj.get_guard_content('t2')

    g = G2(efsm_obj)
    g.run(efsm_obj)
