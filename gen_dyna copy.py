from dev.gen_composite import gen_composite
from src.command_set_py import run_ana_RVE
import os
import linecache
import sys
import shutil
import itertools
#import numpy
#utility function: part_composite generation
def gen_sequence(n_layers):
    #gen_lay = int(n_layers/2)
    list_1 = [0,90,45]
    all_list = []
    all_list.extend([list_1 for i in range(n_layers)]) 
    res = list(itertools.product(*all_list))
    return res
#utility function: part_composite generation 
def substrate(self,n_layers,path):
    thickness_composite = []
    ctr = 0
    
    for k in range(4,n_layers,2):
        print ("Target Layers: ")
        print(k)
        thick = 0.0285*k
        thickness_composite.append(thick)
        filter_seq = []
        sequence_final =[]
        sequence = []
        sequence = gen_sequence(k)
        print("Generating all possible sequences")
        #print("sequence from function")
        #print(len(sequence))
        #print(sequence)
            
        i = 0
        for seq in sequence:
            res = all(ele == seq[0] for ele in seq)
            if(res):
                sequence.pop(i)
            i=i+1
        
        #k1 = 0
        print("Filtering probable sequences")
        print("first pass")
        #print(len(sequence))
        #print(sequence)
        
        '''
        for seq in sequence:
            seq_sort = sorted(seq)
            
            df_list = []
            freq = 0
            
            for i in range(0,len(seq_sort)-1):
                tmp = seq_sort[i+1]-seq_sort[i]
                
                df_list.append(tmp)
            
            freq = df_list.count(0)
            
            if freq == 2:
                
                filter_seq.append(sequence[k1])
    
            k1 = k1+1
        
        print("Filter sequence")
        print((len(filter_seq)))
        print(filter_seq)
        '''
        for j in range(len(sequence)):
            filter_seq.append(sequence[j])
        #check if anti-symmetric
        print("second pass")
        count_asymm = 0
        for filtr in filter_seq:
            y =filtr[::-1]
            if y == filtr:
                sequence_final.append(filtr)
                count_asymm = count_asymm+1
                
        #Check if symmetric
        count_symm = 0
        for filtr in filter_seq:
            half_1 = filtr[:len(filtr)//2]
            half_2 = filtr[len(filtr)//2:]
            if half_1 == half_2:
                sequence_final.append(filtr)
                count_symm = count_symm +1
        #print("thickness_array")
        #print(thickness_composite)
        print("Final stack")
        print(len(sequence_final))
        print("combinations")
        print(sequence_final)
        #for th in range(len(thickness_composite)):
        fldr = "thck_"+"{:.3f}".format(thickness_composite[ctr])
        pth = os.path.join(path,fldr)
        if not os.path.isdir(pth):
            os.mkdir(pth,0o666)
            for gen in range(len(sequence_final)):
                folder = "seq_"+str(sequence_final[gen])
                dest = os.path.join(pth,folder)
                if os.path.isdir(dest):
                    continue
                else:
                    os.mkdir(dest,0o666)
                    print("thck")
                    print(thickness_composite[ctr])
                    print("sequence")
                    print(sequence_final[gen])
                    gen_composite.gen_part("",dest,thickness_composite[ctr],sequence_final[gen])
            ctr = ctr+1
            
    
def main():
    path = sys.path[0]
    if not path.startswith('C'):
        print("The application is located in")
        print(path)
    else:
        print("Path has been reset manually")
        path = "e:/Analyses/FSI/app/"
    mode = 0o666
    folder = "out_temp"
    #part_composite generation
    sub_foldr_part_composite = "part_composite"
    dest_temp_part_composite =os.path.join(path,folder,sub_foldr_part_composite)
    if not os.path.isdir(dest_temp_part_composite):
        os.mkdir(dest_temp_part_composite,mode)
    nth_layers = 1#11
    substrate("",nth_layers,dest_temp_part_composite)
    #mat_composite generation
    #create folder
    sub_foldr_mat_composite = "mat_composite"
    dest_temp_mat_composite =os.path.join(path,folder,sub_foldr_mat_composite)
    if not os.path.isdir(dest_temp_mat_composite):
        os.mkdir(dest_temp_mat_composite,mode)
    #input matrix values
    print("Running micromechanics")
    val = [4000,5000,6000,8000]
    elas_mat = []
    for jind in range(len(val)):
        identifier_value = "_E_"+str(val[jind])
        print("Output/RVE_"+identifier_value)
        print("...Running...")
        RVE_folder = "output"
        path_RVE_1 = os.path.join(path,RVE_folder)
        dir_RVE = "temp_RVE_"+identifier_value
        path_RVE = os.path.join(path_RVE_1,dir_RVE)
        while not os.path.isdir(path_RVE):
            for ind in range(1,7):
                run_ana_RVE.modify_inp("",ind,path,identifier_value,val[jind])
                run_ana_RVE.gen_out_RVE("",ind,path,identifier_value)
                elas_mat_line = run_ana_RVE.combine_RVE("",ind,path,identifier_value)
                elas_mat.append(elas_mat_line)
            folder_dest_1 = "output"
            folder_name = "temp_RVE_"+str(identifier_value)
            folder_dest = os.path.join(path,folder_dest_1,folder_name)
            name_out = "Elas_mat_RVE_"+str(identifier_value)+".txt"
            name=os.path.join(folder_dest,name_out)
            fo = open(name,"w")
            fo.write(str(elas_mat))
            fo.write("\n")
            fo.close()
        print("Data generated for RVE_"+identifier_value)
    #Read every RVE_data
    for j in range(len(val)):
            identifier_value = "_E_"+str(val[jind])
            folder_dest_1 = "output"
            folder_name = "temp_RVE_"+str(identifier_value)
            folder_dest = os.path.join(path,folder_dest_1,folder_name)
            name_out = "Elas_mat_RVE_"+str(identifier_value)+".txt"
            name=os.path.join(folder_dest,name_out)
            with open (name) as f_stiff:
                stiffness = f_stiff.read()
            print(stiffness)
            stiffness.split("],",6)
            print(stiffness[5])

        
        
    
if __name__ == '__main__':
    # Calling main() function
    main()

