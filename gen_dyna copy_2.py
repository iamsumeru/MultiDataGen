from dev.gen_composite import gen_composite
from src.command_set_py import run_ana_RVE
import os
import linecache
import sys
import shutil
import itertools
import numpy as np
import math
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
            
#Utility function for mat composite generation
def compr_stren(Em,nu_m,Gm):
    Ef1 = 73.1 #GPa for glass
    #Em = 2.89 #val(j)GPa for epoxy
    #Gm = 1.07 #GPa/shear modulus for matrix
    nu_f12 = 0.22
    #nu_m = 0.35
    rf = 6e-6
    eta = 1.98
    Vf = 0.6
    pi = 22/7
    expr_1 = pi*math.sqrt(pi)*eta*rf
    expr_2 = 3*(Em/Ef1)
    expr_3= ((Vf*(Em/Ef1))+1-Vf)
    expr_4 = (1+(Vf*nu_f12)+(nu_m*(1-Vf)))
    expr_5 = expr_2*expr_3*expr_4
    expr = expr_1/expr_5
    expr_6 = (Vf+((Em/Ef1)*(1-Vf)))
    expr_7 = Gm*expr_6
    Xc = expr_7*((2*(1+nu_m)*math.sqrt(expr))+1)*1000#MPa
    return Xc
#Utility function for mat composite generation
def ten_stren(sig_m):
    Ef = 76#GPa
    d = 13#microns
    Vf = 0.567
    beta = 6.34
    gamma = 3.927
    L0 = 24#mm
    sig_0 = 1150#MPa
    tau = 42#MPa
    lbda = 0
    sig_f = 1560#MPa
    expr_1 = (2*L0*tau)/(d*sig_0)
    exp_1 = 1/(beta+1)
    sig_c = sig_0*math.pow(expr_1,exp_1)
    sig_c_bar = sig_c/Vf
    Lt = (d*sig_f)/(4*tau)
    poly_a = 3.613e-9
    poly_b = -2.63e-5
    poly_c = 0.903
    poly_1 = poly_a*sig_c_bar*sig_c_bar + poly_b*sig_c_bar + poly_c
    Ac = math.exp(poly_1)
    expr_2 = Ac*L0
    expr_3 = 1-math.exp(-2*Lt*Ac)
    expr_4 = 2*Lt*Ac
    expr_6 = (-1)*L0*Ac
    expr_5 = Ac*Lt*math.exp(expr_6)
    Xt_Turon = Vf*math.pow(expr_2,(1/beta))*sig_0*((expr_3/expr_4)+expr_5)*1000
    return Xt_Turon
    
     
    
    

#def main():
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
#Extract all matrix properties from input file matrix_sets.txt
folder_input = "input"
path_input_1 = os.path.join(path,folder_input)
fname_input = "matrix_sets.txt"
path_input = os.path.join(path_input_1,fname_input)
fo = open(path_input,"r")
lines = fo.readlines()
val = [] #List of E for matrices
val_Gm = [] #List of shear modulus for matrices
val_nu_m = [] #List of nu_m for matrices
val_xc_m = [] #List of compressive strength for matrices
val_xt_m = [] #List of tensile strength for matrices
val_sx_m = [] #List of shear strength for matrices

for i_val in range (int(len(lines))):
    #Extract matrix properties from .txt
    if lines[i_val].split(" ")[0] == 'Em':
        val.append(float(lines[i_val].split(" ")[1]))
    elif lines[i_val].split(" ")[0]== "Gm":
        val_Gm.append(float(lines[i_val].split(" ")[1]))
    elif lines[i_val].split(" ")[0]== "nu_m":
        val_nu_m.append(float(lines[i_val].split(" ")[1]))
    elif lines[i_val].split(" ")[0]== "xc_m":
        val_xc_m.append(float(lines[i_val].split(" ")[1]))
    elif lines[i_val].split(" ")[0]== "xt_m":
        val_xt_m.append(float(lines[i_val].split(" ")[1]))
    elif lines[i_val].split(" ")[0]== "sx_m":
        val_sx_m.append(float(lines[i_val].split(" ")[1]))
        
#Shut this line off for real values
val = [4000,5000,6000,8000]
elas_mat = []
# Run for every matrix identified by its E value
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
#Read every RVE_data for elas matrix from micromechanics simulations
for j in range(0,len(val)):
        print(str(val[jind]))
        identifier_value = "_E_"+str(val[jind])
        folder_dest_1 = "output"
        folder_name = "temp_RVE_"+str(identifier_value)
        folder_dest = os.path.join(path,folder_dest_1,folder_name)
        name_out = "Elas_mat_RVE_"+str(identifier_value)+".txt"
        name=os.path.join(folder_dest,name_out)
        with open (name) as f_stiff:
            stiffness = f_stiff.read()
        stiff_mat_lc = []
        load_case = []
        #Extract elasticity matrix from RVE .txt
        for load in range(0,6):
            print(load)
            load_case = stiffness.split()[load]
            lc = load_case.replace("],","")
            lc_1 = lc.replace("[[","")
            lc_2 = lc_1.replace("\'","")
            lc_3 = lc_2.replace("[","")
            lc_sp =[float(i) for i in (lc_3.split(","))]
            print(lc_sp)
            stiff_mat_lc.append(lc_sp)
        #Generate stiffness and compliance matrices
        stiff_mat = np.array(stiff_mat_lc)
        compl_mat = np.linalg.inv(stiff_mat)
        #Transverse isotropic material properties
        E1 = 1/compl_mat[0][0]
        E2 = 1/compl_mat[1][1]
        E3 = 1/compl_mat[2][2]
        G13 = 0.5/compl_mat[3][3]
        G23 = 0.5/compl_mat[4][4]
        G12 = 0.5/compl_mat[5][5]
        nu12_21 = compl_mat[0][1]*E1*(-1)
        nu31_32 = compl_mat[1][2]*E3*(-1)
        nu13_23 = compl_mat[2][0]*E1*(-1)
        #Use Xu model for compressive strength
        Xc = compr_stren(val[j], val_nu_m[j], val_Gm[j])
        #Use Turon model for tensile strength
        Xt = ten_stren(val_xt_m[j])
        
        
        
        

            

    
        
    
# if __name__ == '__main__':
#     # Calling main() function
#     main()

