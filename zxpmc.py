#!/usr/bin/python
import os
import sys
import time

'''
event_config.txt format:
core:evtsel_l1i_access:0x430300
uncore:evtsel_bus_clk:0x430d00
'''


IA32_MSR_PERF_GLOBAL_CTRL  = 0x38f
IA32_MSR_PERF_GLOBAL_STATUS  = 0x38e
IA32_MSR_PERF_GLOBAL_OVF_CTRL  = 0x390
'''
EVTSEL 
[7:0] event
[11:8] unit
[15:12] counter index 
[16] user
[17] os
[18] edge
[19] resrved
[20] overflow PMI
[21] reserved
[22] enable
[23] inverbit
[26:24] cmask
[27] inter except
[63:28] reserved
'''
IA32_MSR_PERFEVTSEL0  = 0x186
IA32_MSR_PERFEVTSEL1  = 0x187
IA32_MSR_PERFEVTSEL2  = 0x188
IA32_MSR_PERFEVTSEL3  = 0x189

'''
PMC 
[47:0] value   
[63:48] reserve
'''
IA32_MSR_PERF_PMC0  = 0xc1
IA32_MSR_PERF_PMC1  = 0xc2
IA32_MSR_PERF_PMC2  = 0xc3
IA32_MSR_PERF_PMC3  = 0xc4

IA32_MSR_PERF_FIXED_CTR_CTRL = 0x38d
IA32_MSR_PERF_FIXED_CTR0 = 0x309
IA32_MSR_PERF_FIXED_CTR1  = 0x30a
IA32_MSR_PERF_FIXED_CTR2 = 0x30b

IA32_MSR_UNCORE_PERF_GLOBAL_CTRL = 0x391
IA32_MSR_UNCORE_PERF_GLOBAL_STATUS = 0x392
IA32_MSR_UNCORE_GLOBAL_OVF_CTRL = 0x393
IA32_MSR_UNCORE_FIXED_CTR_CTRL = 0x395
IA32_MSR_UNCORE_FIXED_CTR0 = 0x394
IA32_MSR_UNCORE_PERFEVTSEL0 = 0x3c0
IA32_MSR_UNCORE_PERFEVTSEL1 = 0x3c1
IA32_MSR_UNCORE_PERFEVTSEL2 = 0x3c2
IA32_MSR_UNCORE_PERFEVTSEL3 = 0x3c3 
IA32_MSR_UNCORE_PERFEVTSEL4 = 0x3c4 # no work
IA32_MSR_UNCORE_PERFEVTSEL5 = 0x3c5
IA32_MSR_UNCORE_PERFEVTSEL6 = 0x3c6
IA32_MSR_UNCORE_PERFEVTSEL7 = 0x3c7
IA32_MSR_UNCORE_PMC0 = 0x3b0
IA32_MSR_UNCORE_PMC1 = 0x3b1
IA32_MSR_UNCORE_PMC2 = 0x3b2
IA32_MSR_UNCORE_PMC3 = 0x3b3
IA32_MSR_UNCORE_PMC4 = 0x3b4
IA32_MSR_UNCORE_PMC5 = 0x3b5
IA32_MSR_UNCORE_PMC6 = 0x3b6
IA32_MSR_UNCORE_PMC7 = 0x3b7

'''
event
'''

infilename = "event_config.txt"
core_event_config_dic = {}
uncore_event_config_dic = {}
event_result_dic = {}
os.system("sudo modprobe msr")
os.system("gcc zxpower.c -o aa")
loopcount = 0
samplecount = int(sys.argv[1])
'''
change scale
'''
# base = [0,1,2,3,4,5,6,7,8,9,A,B,C,D,E,F]
base = [str(x) for x in range(10)] + [chr(x) for x in range(ord('A'),ord('A')+6)]
def bin2dec(string_corepmcnum):
    return str(int(string_corepmcnum,2))
def hex2dec(string_corepmcnum):
    return str(int(string_corepmcnum.upper(),16))
def dec2bin(string_corepmcnum):
    corepmcnum = int(string_corepmcnum)
    mid = []
    while True:
        if corepmcnum == 0: break
        corepmcnum,rem = divmod(corepmcnum,2)
        mid.append(base[rem])
    return ''.join([str(x) for x in mid[::-1]])

def ExecCmdGetTernal(cmd):
    r = os.popen(cmd)
    text = r.read()
    r.close()
    return text

def RdmsrCmd(cpu, reg):
    if cpu == -1:
        cmd = "sudo rdmsr -a {}".format(reg)
    else:
        cmd = "sudo rdmsr -p {} {}".format(cpu,reg)
    result = ExecCmdGetTernal(cmd)
    return result

def WrmsrCmd(cpu,reg,hi,low):
    if cpu == -1:
        cmd = "sudo wrmsr -a {} {} {}".format(reg,hi,low)
    else:
        cmd = "sudo wrmsr -p {} {} {} {}".format(cpu,reg,hi,low)
    ExecCmdGetTernal(cmd)

def GetEventConfig():
    with open(infilename, "r") as file_read:
        while True:
            strline = file_read.readline()
            if not strline:
                break
            strtemp = strline.strip("\n").split(":")
            if strtemp[0]:
                if strtemp[0] == "core":
                    core_event_config_dic[strtemp[1]] = strtemp[2] 
                elif strtemp[0] == "uncore":
                    uncore_event_config_dic[strtemp[1]] = strtemp[2]
                else:
                    pass                                                                                                                                                                                                                                                                         

def ProcessNoFixedPMC():
    corekeylist = core_event_config_dic.keys()
    uncorekeylist = uncore_event_config_dic.keys()
    core_event_config_keys_list = []
    uncore_event_config_keys_list = []
    # group by 4
    for i in range(0,len(corekeylist),4):
        core_event_config_keys_list.append(corekeylist[i:i+4])
    for i in range(0,len(uncorekeylist),4):
        uncore_event_config_keys_list.append(uncorekeylist[i:i+4])

    core_uncore_maxlen = 0
    if len(core_event_config_keys_list) >= len(uncore_event_config_keys_list):
        core_uncore_maxlen = len(core_event_config_keys_list)
    else:
        core_uncore_maxlen = len(uncore_event_config_keys_list)
    
    # core sel config, chx002 support 4 pmcs
    core_event_key_sel0 = ""
    core_event_key_sel1 = ""
    core_event_key_sel2 = ""
    core_event_key_sel3 = ""
    # uncore sel config, chx002 support 4 pmcs 
    uncore_event_key_sel0 = ""
    uncore_event_key_sel1 = ""
    uncore_event_key_sel2 = ""
    uncore_event_key_sel3 = ""
    # assign need sample events to four core pmc msrs or four uncore pmc msrs  
    for i in range(0,core_uncore_maxlen):
        core_event_key_sel0 = ""
        core_event_key_sel1 = ""
        core_event_key_sel2 = ""
        core_event_key_sel3 = ""
        uncore_event_key_sel0 = ""
        uncore_event_key_sel1 = ""
        uncore_event_key_sel2 = ""
        uncore_event_key_sel3 = ""  
        # core     
        try:
            if core_event_config_keys_list[i]:
                try:
                    if core_event_config_keys_list[i][0]:
                        core_event_key_sel0 = core_event_config_keys_list[i][0]
                except:
                    core_event_key_sel0 = ""
                    pass

                try:
                    if core_event_config_keys_list[i][1]:
                        core_event_key_sel1 = core_event_config_keys_list[i][1]
                except:
                    core_event_key_sel1 = ""
                    pass

                try:
                    if core_event_config_keys_list[i][2]:
                        core_event_key_sel2 = core_event_config_keys_list[i][2]
                except:
                    core_event_key_sel2 = ""
                    pass

                try:
                    if core_event_config_keys_list[i][3]:
                        core_event_key_sel3 = core_event_config_keys_list[i][3]
                except:
                    core_event_key_sel3 = ""
                    pass
        except:
            core_event_key_sel0 = ""
            core_event_key_sel1 = ""
            core_event_key_sel2 = ""
            core_event_key_sel3 = ""
            pass
        # uncore
        try:
            if uncore_event_config_keys_list[i]:
                try:
                    if uncore_event_config_keys_list[i][0]:
                        uncore_event_key_sel0 = uncore_event_config_keys_list[i][0]
                except:
                    uncore_event_key_sel0 = ""
                    pass

                try:
                    if uncore_event_config_keys_list[i][1]:
                        uncore_event_key_sel1 = uncore_event_config_keys_list[i][1]
                except:
                    uncore_event_key_sel1 = ""
                    pass

                try:
                    if uncore_event_config_keys_list[i][2]:
                        uncore_event_key_sel2 = uncore_event_config_keys_list[i][2]
                except:
                    uncore_event_key_sel2 = ""
                    pass

                try:
                    if uncore_event_config_keys_list[i][3]:
                        uncore_event_key_sel3 = uncore_event_config_keys_list[i][3]
                except:
                    uncore_event_key_sel3 = ""
                    pass
        except:
            uncore_event_key_sel0 = ""
            uncore_event_key_sel1 = ""
            uncore_event_key_sel2 = ""
            uncore_event_key_sel3 = ""
            pass
        ## disable pmc
        # core
        WrmsrCmd(-1,IA32_MSR_PERFEVTSEL0,0x0,0x0)
        WrmsrCmd(-1,IA32_MSR_PERFEVTSEL1,0x0,0x0)
        WrmsrCmd(-1,IA32_MSR_PERFEVTSEL2,0x0,0x0)
        WrmsrCmd(-1,IA32_MSR_PERFEVTSEL3,0x0,0x0)
        # uncore
        WrmsrCmd(-1,IA32_MSR_UNCORE_PERFEVTSEL0,0x0,0x0)
        WrmsrCmd(-1,IA32_MSR_UNCORE_PERFEVTSEL1,0x0,0x0)
        WrmsrCmd(-1,IA32_MSR_UNCORE_PERFEVTSEL2,0x0,0x0)
        WrmsrCmd(-1,IA32_MSR_UNCORE_PERFEVTSEL3,0x0,0x0)
        ## enable pmc
        # core
        if core_event_key_sel0 != "":
            WrmsrCmd(-1,IA32_MSR_PERFEVTSEL0,0x0,core_event_config_dic[core_event_key_sel0])
        if core_event_key_sel1 != "":
            WrmsrCmd(-1,IA32_MSR_PERFEVTSEL1,0x0,core_event_config_dic[core_event_key_sel1])
        if core_event_key_sel2 != "":
            WrmsrCmd(-1,IA32_MSR_PERFEVTSEL2,0x0,core_event_config_dic[core_event_key_sel2])
        if core_event_key_sel3 != "":
            WrmsrCmd(-1,IA32_MSR_PERFEVTSEL3,0x0,core_event_config_dic[core_event_key_sel3])
        # uncore
        if uncore_event_key_sel0 != "":
            WrmsrCmd(-1,IA32_MSR_UNCORE_PERFEVTSEL0,0x0,uncore_event_config_dic[uncore_event_key_sel0])
        if uncore_event_key_sel1 != "":
            WrmsrCmd(-1,IA32_MSR_UNCORE_PERFEVTSEL1,0x0,uncore_event_config_dic[uncore_event_key_sel1])
        if uncore_event_key_sel2 != "":
            WrmsrCmd(-1,IA32_MSR_UNCORE_PERFEVTSEL2,0x0,uncore_event_config_dic[uncore_event_key_sel2])
        if uncore_event_key_sel3 != "":
            WrmsrCmd(-1,IA32_MSR_UNCORE_PERFEVTSEL3,0x0,uncore_event_config_dic[uncore_event_key_sel3])

        ## pmc counter clear 0
        # core
        WrmsrCmd(-1,IA32_MSR_PERF_PMC0,0x0,0x0)
        WrmsrCmd(-1,IA32_MSR_PERF_PMC1,0x0,0x0)
        WrmsrCmd(-1,IA32_MSR_PERF_PMC2,0x0,0x0)
        WrmsrCmd(-1,IA32_MSR_PERF_PMC3,0x0,0x0)
        # uncore
        WrmsrCmd(-1,IA32_MSR_UNCORE_PMC0,0x0,0x0)
        WrmsrCmd(-1,IA32_MSR_UNCORE_PMC1,0x0,0x0)
        WrmsrCmd(-1,IA32_MSR_UNCORE_PMC2,0x0,0x0)
        WrmsrCmd(-1,IA32_MSR_UNCORE_PMC3,0x0,0x0)

        ## set sample time 
        time.sleep(0.2)

        ## get pmc conter
        # core
        if core_event_key_sel0 != "":
            event_result_dic[core_event_key_sel0] = RdmsrCmd(-1, IA32_MSR_PERF_PMC0)
        if core_event_key_sel1 != "":
            event_result_dic[core_event_key_sel1] = RdmsrCmd(-1, IA32_MSR_PERF_PMC1)
        if core_event_key_sel2 != "":
            event_result_dic[core_event_key_sel2] = RdmsrCmd(-1, IA32_MSR_PERF_PMC2)
        if core_event_key_sel3 != "":
            event_result_dic[core_event_key_sel3] = RdmsrCmd(-1, IA32_MSR_PERF_PMC3)
        # uncore
        if uncore_event_key_sel0 != "":
            event_result_dic[uncore_event_key_sel0] = RdmsrCmd(-1, IA32_MSR_UNCORE_PMC0) 
        if uncore_event_key_sel1 != "":
            event_result_dic[uncore_event_key_sel1] = RdmsrCmd(-1, IA32_MSR_UNCORE_PMC1)
        if uncore_event_key_sel2 != "":
            event_result_dic[uncore_event_key_sel2] = RdmsrCmd(-1, IA32_MSR_UNCORE_PMC2)
        if uncore_event_key_sel3 != "":
            event_result_dic[uncore_event_key_sel3] = RdmsrCmd(-1, IA32_MSR_UNCORE_PMC3)                   

        ## disable pmc
        # core
        WrmsrCmd(-1,IA32_MSR_PERFEVTSEL0,0x0,0x0)
        WrmsrCmd(-1,IA32_MSR_PERFEVTSEL1,0x0,0x0)
        WrmsrCmd(-1,IA32_MSR_PERFEVTSEL2,0x0,0x0)
        WrmsrCmd(-1,IA32_MSR_PERFEVTSEL3,0x0,0x0)
        # uncore
        WrmsrCmd(-1,IA32_MSR_UNCORE_PERFEVTSEL0,0x0,0x0)
        WrmsrCmd(-1,IA32_MSR_UNCORE_PERFEVTSEL1,0x0,0x0)
        WrmsrCmd(-1,IA32_MSR_UNCORE_PERFEVTSEL2,0x0,0x0)
        WrmsrCmd(-1,IA32_MSR_UNCORE_PERFEVTSEL3,0x0,0x0)


def SavePMCResultToTxt():
    outfilename = "pmcout%d.txt"%(loopcount)
    os.system("{} {}".format("rm -rf", outfilename))
    with open(outfilename, 'a+') as file_write:
        for pmckey, pmcvalue in event_result_dic.items():
            pmclist = pmcvalue.strip("\n").split("\n")
            decvalue = 0
            for item in pmclist:
                decvalue = decvalue + int(hex2dec(item))
            #print(pmclist)
            #print(pmckey + ":" + str(decvalue))
            file_write.write(pmckey + ":" + str(decvalue) + "\n")

def SavePOWERResultToTxt():
    outfilename = "powerout%d.txt"%(loopcount)
    os.system("{} {}".format("rm -rf", outfilename))
    powerresult = ExecCmdGetTernal("sudo ./aa")
    with open(outfilename, 'a+') as file_write:
        file_write.write(powerresult + "\n")   

if __name__ == '__main__':
    GetEventConfig()
    while loopcount < samplecount:
        ProcessNoFixedPMC()
        SavePMCResultToTxt()
        SavePOWERResultToTxt()
        loopcount = loopcount + 1
