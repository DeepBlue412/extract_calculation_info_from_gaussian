
# coding: utf-8
#!/usr/bin/python
# Author : DeepBlue


import linecache
import re
import pandas as pd
import os

def get_line_context(file_path,linenumber):
    return linecache.getline(file_path, linenumber).strip()


def extract(filename):
    
    file = open(filename,'r')
    
    #to get molecule type
    molecule_type = get_line_context(filename,3)
    if molecule_type.startswith("Output="):
        molecule_type = molecule_type[len("Output="):].strip().split("-")
    molecule_type = molecule_type[0]

    if molecule_type == "Y6":
        molecule_type = "Y6 monomer"
    if molecule_type == "Rubrene":
        molecule_type = "Rubrene monomer" 
        
#     print(filename + ':molecule type get!')

    #to get route section information
    route_section_raw = get_line_context(filename,86)
    route_section = route_section_raw.strip("Output=").split()

    DF_BS = route_section[1]
    DF_BS = DF_BS.split("/")
    density_functional = DF_BS[0]
    bassis_set = DF_BS[1]

    if 'TDA' in route_section_raw:
        method = "TDDFT"
        TDA    = "Y"
        pattern = re.compile(r"TDA\(([^)]+)\)")
        TD_option = pattern.findall(route_section_raw)
    elif 'TD' in route_section_raw:
        method = "TDDFT"
        TDA    = "N"    
        pattern = re.compile(r"TD\(([^)]+)\)")
        TD_option = pattern.findall(route_section_raw)
    else:
        print("error")

    if 'OPT' in route_section_raw or 'opt' in route_section_raw:
        energy_type = "vertical excitation"
    else: 
        energy_type = "vertical absorbtion"
    
    if 'SCRF' in route_section_raw:
        PCM = "Y"
        pattern = re.compile(r"SCRF\(([^)]+)\)")
        PCM_option = pattern.findall(route_section_raw)
    else:
        PCM = "N"
        PCM_option = "N/A"
        
#     print(filename + ':route section information get!')
        
    #to get calculation results:
    with open(filename,'r') as fr:
        lines = fr.readlines()

    i = 0
    j = 0
    j_trigger = 0
    k = 0
    k_trigger = 0
    success = 0

    initial_structure = "N/A"

    T = ['N/A'] * 10
    f_T = ['N/A'] * 10
    S = ['N/A'] * 10
    f_S = ['N/A'] * 10
    

    if '50-50' in route_section_raw:
        n = 10
    else:
        n = 5

    for line in lines:
        if 'nprocshared' in line:
            cpu_number = line.split("=")[1].strip()

        if '%mem=' in line:
            memory = line.split("=")[1].strip()

        if 'Elapsed time:' in line:
            time = line[len(" Elapsed time:       "):].strip()
            time = time.replace("  "," ")
            time = time.replace(".","")

        if '-0.71178  -4.76978   0.09042' in line:
            initial_structure = 'reopt by pvdz'
        if '-0.70811  -4.75989   0.08759' in line:
            initial_structure = 'reopt by pvtz'
        if '1.49619  -1.94589  -0.4480' in line:
            initial_structure = 'from Han&Yi'


        for i in range(0,10):
            if 'Excited State' in line and str(i) + ':' in line:


                if 'Triplet' in line:
                    T[j] = line.split()[4]+'eV'
                    f_T[j] = line.split()[8]
                    f_T[j] = f_T[j][len("f="):]
                    j_trigger = j_trigger + 1
                if 'Singlet' in line:
                    S[k] = line.split()[4]+'eV'
                    f_S[k] = line.split()[8]
                    f_S[k] = f_S[k][len("f="):]
                    k_trigger = k_trigger + 1
    

            if j_trigger != 0:
                j = j + 1
                j_trigger = 0
            if k_trigger != 0:
                k = k + 1
                k_trigger = 0      

            if 'Excited State   ' + str(i) + ':' in line and  i == n:  # reset the j and k for next cycle of gaussian calculation
                j = 0
                k = 0 
        
        if 'Normal termination of Gaussian' in line:
            success = 1
                
#     print(filename + ':calculation results get!')
    
        

                
    #write them into csv            
    Additional = 'N/A'

    dataframe = pd.DataFrame({'molecule_type':molecule_type,'initial_structure':initial_structure,'energy_type':energy_type,'density_functional':density_functional,'bassis_set':bassis_set,'method':method,'TDA':TDA,'TD_option':TD_option,'PCM':PCM,'PCM_option':PCM_option,'cpu_number':cpu_number,'memory':memory,'time':time,'S1':S[0],'f_S1':f_S[0],'S2':S[1],'f_S2':f_S[1],'S3':S[2],'f_S3':f_S[2],'S4':S[3],'f_S4':f_S[3],'S5':S[4],'f_S5':f_S[4],'T1':T[0],'f_T1':f_T[0],'T2':T[1],'f_T2':f_T[1],'T3':T[2],'f_T3':f_T[2],'T4':T[3],'f_T4':f_T[3],'T5':T[4],'f_T5':f_T[4],'Additional':Additional})

    with open("result_list.txt","a+") as rl:
        datarl = rl.read()                             # I don't know why a+ cannot really read...
    with open("result_list.txt","r") as rl:         # avoid duplicates
        datarl = rl.read()
    with open("result_list.txt","a+") as rl:         
        if success == 1:
            if (filename in datarl) == False: 
                rl.write(str(filename)+'\n')
                if os.path.exists(r'./calculation_result.csv') == True:
                    dataframe.to_csv("calculation_result.csv",mode = 'a',sep = ',',header = False, index = False)
                    print(filename + ':Completion of writing to csv!')
                else:
                    dataframe.to_csv("calculation_result.csv",sep = ',',index = False)
                    print(filename + ':Completion of writing to csv!')
            else:
                print(filename + ":this result has already been there")
        else:
            print(filename + ":this result has mistake...")
                
        
    


print("please type the path of result directory")
path = input()
#path = "/rds/general/user/zl2122/home/UpConversion/0004-TDDFT/S0_to_S1_PCM/results"



for filename in os.listdir(path):
       if '.log' in filename : 
            extract(path +'/'+ filename)



#sort csv
data = pd.read_csv("calculation_result.csv")
data =data.sort_values(by = ['molecule_type','energy_type','density_functional','bassis_set','method','TDA','PCM','PCM_option','TD_option','initial_structure'])
data.to_csv("calculation_result.csv",sep = ',',index = False)  
print('Completion of csv sorting!')


