from mut import load_efsm_mutation
from efsm.Mutation.utility import read_conf_m
from efsm.EFSMparser.load import LoadEFSM


if __name__ == "__main__":

    for iteration in range(1, 200+1):

        SPEC_FILE = read_conf_m()
        l = LoadEFSM()
        efsm_obj = l.load_efsm(SPEC_FILE)       # ！！！
        load_efsm_mutation(iteration, SPEC_FILE, efsm_obj)
