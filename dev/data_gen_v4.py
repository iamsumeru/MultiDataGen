# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 08:47:46 2020

@author: Sumeru Nayak
"""

import os
import linecache
import shutil
class modify_input:
    # def __init__(self,target_value,ind):
    #     self.target_value = target_value
    #     self.ind = ind
    def modify_file(self,target_value,ind):
        input_dir = "E:/Analyses/FSI/ML_data/working/test/1"#"E:/Analyses/FSI/new/coating_variation/8_python/output/"
        coat_params = ["t","E"]#,"s"]
        subs_params = ["t","E","s"]
        super_params = coat_params + subs_params
        #Set search keywords from .k file
        lookup_c_params = ["shell_coat","coat_mat"]#,"coat_mat"]
        lookup_s_params = ["shell_section","*MAT_COMPOSITE_DAMAGE_TITLE","*MAT_COMPOSITE_DAMAGE_TITLE"]
        super_lookup_params = lookup_c_params + lookup_s_params
        #Set relative positions wrt keywords from .k file
        rel_position_c = [4,2]#,2]
        rel_position_s =[4,3,11]
        super_rel_position = rel_position_c + rel_position_s
        file_in = "main"
        path_in_t = os.path.join(input_dir,file_in) 
        sz = len(super_params)
        num_t_l = []
        line_mod_l = []
        for t in range(sz):
            with open(path_in_t) as myFile:
                for num, line in enumerate(myFile, 1):
                    if super_lookup_params[t] in line:
                        num_t = num
            num_t = num_t + super_rel_position[t]
            num_t_l.append(num_t)
            print("list:")
            print(num_t_l)
            string_mod = linecache.getline(path_in_t,num_t_l[t])
            identify_value = string_mod
            list_values = identify_value.split()
            param_index = t
            if (param_index <3 and super_params[param_index] == "t"):
                tv = target_value[param_index]
                line_mod = string_mod.replace(str(list_values[0]),str(tv))
            elif (param_index <3 and super_params[param_index] == "E"):
                tv = "1.5"+str('%0.6f'%((target_value[param_index]/1e10)))+"E10"
                line_mod = string_mod.replace(str(list_values[1]),str(tv))
            elif (param_index <3 and super_params[param_index] == "s"):
                tv = target_value[param_index]
                line_mod = string_mod.replace(str(list_values[-1]),str(tv))
            elif (param_index >2 and super_params[param_index] == "t"):
                tv = target_value[param_index]
                line_mod = string_mod.replace(str(list_values[0]),str(tv))
            elif (param_index >2 and super_params[param_index] == "E"):
                target_value_t1 = "2.0"+str('%0.6f'%((target_value[param_index]/1e10)))+"E11"
                target_value_t2 = str('%0.6f'%((target_value[param_index]*(2.6/2.9)/1e10)))+"E11"
                tv =  target_value_t1 + target_value_t2 + target_value_t2
                line_mod = string_mod.replace(str(list_values[1]),str(tv))
            elif (param_index >2 and super_params[param_index] == "s"):
                target_value_t1 = str('%0.6f'%((target_value[param_index]/1e9)*(6/5.31)))+"E8"
                target_value_t2 = str('%0.6f'%((target_value[param_index]/1e9)))+"E9"
                #target_value_t3 = str(round((target_value/1e9)*(5.31/5.31)),2)+"0000E9"
                target_value_t4 = str('%0.6f'%((target_value[param_index]/1e9)*(5.1/5.31)))+"E9"
                tv = target_value_t1 + target_value_t2 + target_value_t2 + target_value_t4
                line_mod = string_mod.replace(str(list_values[0]),str(tv))
            line_mod_l.append(line_mod)
            
        path_out = "E:/Analyses/FSI/ML_data/working/test/1/output_generated_inputs"#E:/Analyses/FSI/ML_data/code_generator/"
        name_out = "temp" + str(ind)
        name = os.path.join(path_out,name_out)
        index = 0
        with open(path_in_t) as f:
            with open(name, "w") as f1:
                for line in f:
                    index += 1
                    if index == num_t_l[0]:
                        f1.write(line_mod_l[0])
                        print("replaced line at "+str(num_t_l[0])+" with "+line_mod_l[0])
                        continue
                    if index == num_t_l[1]:
                        f1.write(line_mod_l[1])
                        print("replaced line at "+str(num_t_l[1])+" with "+line_mod_l[1])
                        continue
                    if index == num_t_l[2]:
                        f1.write(line_mod_l[2])
                        print("replaced line at "+str(num_t_l[2])+" with "+line_mod_l[2])
                        continue
                    if index == num_t_l[3]:
                        f1.write(line_mod_l[3])
                        print("replaced line at "+str(num_t_l[3])+" with "+line_mod_l[3])
                        continue
                    if index == num_t_l[4]:
                        f1.write(line_mod_l[4])
                        print("replaced line at "+str(num_t_l[4])+" with "+line_mod_l[4])
                        continue
                    # if index == num_t_l[5]:
                    #     f1.write(line_mod_l[5])
                    #     print("replaced line at"+str(num_t_l[5])+"with"+line_mod_l[5])
                    #     continue
                    
                    f1.write(line)
                
coat_params = ["t","E"]#,"s"]
subs_params = ["t","E","s"]
super_params = coat_params + subs_params
params_c_ini = [1.2,25e9]#,25e6]
params_c_fin = [1.9,35e9]#,35e6]
data_points = 2
temp = len(coat_params)
super_list_c = [[0 for x in range(data_points)] for y in range (temp)]
#Populate coating list
for i in range(temp):
    for j in range(0,data_points):
        temp_val = round ((params_c_ini[i]-j*((params_c_ini[i]-params_c_fin[i])/(data_points-1))),6)
        super_list_c [i][j] = temp_val
print("##########Coating parameters generated#############\n")
print("########Setting up substrate parameters############\n")      
global params_s_ini 
params_s_ini = [1.2,25e9,25e6]
params_s_fin = [1.9,35e9,35e6]
data_points = 2
temp = len(subs_params)
super_list_s = [[0 for x in range(data_points)] for y in range (temp)]
#Populate substrate list
for i in range(temp):
    for j in range(0,data_points):
        temp_val = round ((params_s_ini[i]-j*((params_s_ini[i]-params_s_fin[i])/(data_points-1))),6)
        super_list_s [i][j] = temp_val
for i in range(temp):
    super_list_c.append(super_list_s[i])
temp = len(coat_params) + len(subs_params)      
super_matrix =[[0 for x in range(data_points)] for y in range (temp)]       
print("########Transferring to super matrix#############\n")
for i in range (temp):
    for j in range (data_points):
        super_matrix [i][j]= super_list_c[i][j] 
print("##########All parameters assembled###############\n")  
print("##########Starting file generation###############\n")
#File generation for every cell combination in super matrix
# super_matrix = []
# data_points =3
# data=0
# list_dp = []
# indx = 0
# ob_list = []
# for a in range(data_points):
# 	for b in range(data_points):
# 		for c in range(data_points):
# 			for d in range(data_points):
# 				for e in range(data_points):
# # 					for f in range(data_points):
# 						
# 						data = super_matrix[0][a]
# 						list_dp.append(data)
# 						data = super_matrix[1][b]
# 						list_dp.append(data)
# 						data = super_matrix[2][c]
# 						list_dp.append(data)
# 						data = super_matrix[3][d]
# 						list_dp.append(data)
# 						data = super_matrix[4][e]
# 						list_dp.append(data)
# # 						data = super_matrix[5][f]
# # 						list_dp.append(data)
#                         modify_file(list_dp,ind)

data = 0
list_dp = []
indx = 0
data_points = 2
for a in range(data_points):
    for b in range(data_points):
        for c in range(data_points):
            for d in range(data_points):
                for e in range(data_points):
                    data = super_matrix[0][a]
                    list_dp.append(data)
                    data = super_matrix[1][b]
                    list_dp.append(data)
                    data = super_matrix[2][c]
                    list_dp.append(data)
                    data = super_matrix[3][d]
                    list_dp.append(data)
                    data = super_matrix[4][e]
                    list_dp.append(data)
                    ob = modify_input()
                    ob.modify_file(list_dp,indx)
                    indx += 1                    
                    

# temp_tar =[1.2,25e9,1.5,26e9,36e8]
#ob = modify_input()
# ob = modify_input()
# ob_list.append(ob)
# ob_list[indx].modify(list_dp,indx)
# indx += 1
#modify_file(list_dp,indx)
# Function to rename multiple files
def main():
   i = 0
   mode = 0o666
   path="E:/Analyses/FSI/ML_data/working/test/1/output_generated_inputs/"
   for filename in os.listdir(path):
      #Create directory with filename
      dir_name = path + filename +"x"
      os.mkdir(dir_name,mode)
      #Move filename to directory and rename
      start_loc = path + filename
      end_loc = dir_name +"/"+ filename + ".k"
      shutil.move(start_loc,end_loc)
      slrm_file = dir_name + "/" + filename + ".slurm"
      fo = open(slrm_file,"w+")
      fo.write("#!/bin/bash")
      fo.write("\n")
      fo.write("#SBATCH --cpus-per-task=8")
      fo.write("\n")
      fo.write("#SBATCH --mem=1g")
      fo.write("\n")
      fo.write("module load ls-dyna")
      fo.write("\n")
      fo.write("INPUT_FILE=\"$1\"")
      fo.write("\n")
      path_HPC = "/data/lamci/sumeru/Dyna_UNDEX/" + filename +"x"
      fo.write("cd ")
      fo.write(path_HPC)
      fo.write("\n")
      fo.write("mpirun ls-dyna_smp_d_r1010_x64_redhat5_ifort160 i=\"${INPUT_FILE}\" memory=625m")
      fo.close()
      
      i += 1
# Driver Code
if __name__ == '__main__':
   # Calling main() function
   main()