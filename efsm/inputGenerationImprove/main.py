#coding=utf-8
from efsm.inputGenerationImprove.IPSG import IPS_Generation
from efsm.EFSMparser.load import LoadEFSM

if __name__ == '__main__':
    l = LoadEFSM()
    scp = l.load_efsm('Network')
    ips = IPS_Generation('Network')
    print(ips.generate(2, scp.cur_sc.context_vars))
    print(ips.generate(4, scp.cur_sc.context_vars))