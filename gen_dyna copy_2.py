from dev.gen_composite import gen_composite
from dev.gen_coat import gen_coat
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
    print("Generating all possible combinations of layups")
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
        print("Generating part composite")
        print("Generating material composite")
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
#Utility function for mat composite generation
def shear_stren(sig_m): 
    sc = 74/70*sig_m
    return sc
def calc_density(d_m):
    Vf_f = 0.6
    Vf_m = 1-Vf_f
    d_f = 2.49
    m_f = d_f*Vf_f
    m_m = d_m*Vf_m
    m_net = m_f+m_m
    d = m_net
    return d
#Query total dirs, subdirs and files
def query_folders(path_temp):
    folders = files = 0
    for _, dirnames, filenames in os.walk(path_temp_out):
        folders += len(dirnames)
        files += len(filenames)
#Query dirs immediately in path
def query_number_subfolder(path_temp):
    que = len(next(os.walk(path_temp))[1])
    return que
def query_list_subdirs(path_temp):
    q = [f.path.split("\\")[-1] for f in os.scandir(path_temp) if f.is_dir()]
    return q

#Utility function for combining files
def gen_list(n):
    q=[]
    for i in range(n):
        q.append(i)
    return q

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
    #Extract all matrix properties from input file matrix_sets.txt
    folder_input = "input"
    path_input_1 = os.path.join(path,folder_input)
    fname_input = "matrix_sets.txt"
    path_input = os.path.join(path_input_1,fname_input)
    fo = open(path_input,"r")
    lines = fo.readlines()
    val_name = []
    val = [] #List of E for matrices
    val_ro =[] #List of ro for matrices
    val_Gm = [] #List of shear modulus for matrices
    val_nu_m = [] #List of nu_m for matrices
    val_xc_m = [] #List of compressive strength for matrices
    val_xt_m = [] #List of tensile strength for matrices
    val_sx_m = [] #List of shear strength for matrices
    
    for i_val in range (int(len(lines))):
        #Extract matrix properties from .txt
        if lines[i_val].split(" ")[0] == 'Name':
            val_name.append(lines[i_val].split(" ")[1])
        elif lines[i_val].split(" ")[0] == 'ro':
            val_ro.append(float(lines[i_val].split(" ")[1]))
        elif lines[i_val].split(" ")[0] == 'Em':
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
            
    #Shut this line off for real values from .txt
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
            #print(str(val[jind]))
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
            print("Computing composite properties from micromechancis")
            for load in range(0,6):
               #print(load)
                load_case = stiffness.split()[load]
                lc = load_case.replace("],","")
                lc_1 = lc.replace("[[","")
                lc_2 = lc_1.replace("\'","")
                lc_3 = lc_2.replace("[","")
                lc_sp =[float(i) for i in (lc_3.split(","))]
               #print(lc_sp)
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
            Xt_trans = 0.6*Xt
            sc = shear_stren(val_sx_m[j])
            ro = calc_density(val_ro[j])
            mat_comp_out = "out_temp"
            mat_comp_dir = "mat_composite"
            mat_comp_folder = val_name[j]
            mat_comp_path = os.path.join(path, mat_comp_out, mat_comp_dir, mat_comp_folder)
            if not os.path.isdir(mat_comp_path):
                os.mkdir(mat_comp_path,mode)
            gen_composite.gen_mat("",mat_comp_path,ro,E1,E2,nu12_21,nu31_32,G12,G23,sc,Xt,Xt_trans,Xc)
            
    #Extract all matrix properties from input file coat_sets.txt
    folder_input_coat = "input"
    path_input_1_coat = os.path.join(path,folder_input_coat)
    fname_input_coat = "coat_sets.txt"
    path_input_coat = os.path.join(path_input_1_coat,fname_input_coat)
    fo = open(path_input_coat,"r")
    lines = fo.readlines()
    val_name_coat = []
    val_coat = [] #List of E for coat
    val_ro_coat = [] #List of ro for coat
    val_pr_coat = []
    print("Reading data from user input files")
    for i_val in range (int(len(lines))):
        #Extract coat properties from .txt
        
        if lines[i_val].split(" ")[0] == 'Name':
            val_name_coat.append(lines[i_val].split(" ")[1])
        elif lines[i_val].split(" ")[0] == 'ro':
            val_ro_coat.append(float(lines[i_val].split(" ")[1]))
        elif lines[i_val].split(" ")[0] == 'E':
            val_coat.append(float(lines[i_val].split(" ")[1]))
        elif lines[i_val].split(" ")[0] == 'pr':
            val_pr_coat.append(float(lines[i_val].split(" ")[1]))
    #mat_coat generation
    print("Generating mat_coat ")
    sub_foldr_mat_coat = "mat_coat"
    dest_temp_mat_coat =os.path.join(path,folder,sub_foldr_mat_coat)
    if not os.path.isdir(dest_temp_mat_coat):
        os.mkdir(dest_temp_mat_coat,mode)
    for j in range(0,len(val_coat)):
        mat_coat_out = "out_temp"
        mat_coat_dir = "mat_coat"
        mat_coat_folder = val_name[j]
        mat_coat_path = os.path.join(path, mat_coat_out, mat_coat_dir, mat_coat_folder)
        if not os.path.isdir(mat_coat_path):
            os.mkdir(mat_coat_path,mode)
        gen_coat.gen_mat("",mat_coat_path,val_ro_coat[j],val_coat[j],val_pr_coat[j])
    
    #section coat generation
    print("Generating section coat")
    sub_foldr_sec_coat = "section_coat"
    dest_temp_sec_coat =os.path.join(path,folder,sub_foldr_sec_coat)
    if not os.path.isdir(dest_temp_sec_coat):
        os.mkdir(dest_temp_sec_coat,mode)
    thck_coat = [1.48,2.51,3.67,4.89]
    for j in range(0,len(thck_coat)):
        sec_coat_out = "out_temp"
        sec_coat_dir = "section_coat"
        sec_coat_folder = "th_"+str(thck_coat[j])
        sec_coat_path = os.path.join(path, sec_coat_out, sec_coat_dir, sec_coat_folder)
        if not os.path.isdir(sec_coat_path):
            os.mkdir(sec_coat_path,mode)
        gen_coat.gen_section("",sec_coat_path,thck_coat[j])
    #Query number of temp_output files
    sub_out_temp = "out_temp"
    path_temp_out = os.path.join(path,sub_out_temp)
    var_sets = query_number_subfolder(path_temp_out)
    #p = [x[0] for x in os.walk(path_temp_out)]
    var = query_list_subdirs(path_temp_out)
    count_vars = []
    dict_count = {}.fromkeys(var,0)
    count_seq = []
    var_var_list = []
    #Extract number of data points of every variable
    for i in range(var_sets):
        if var[i] == 'part_composite':
            folder_var = var[i]
            path_var = os.path.join(path_temp_out,folder_var)
            var_var_sets = query_number_subfolder(path_var)
            var_var = query_list_subdirs(path_var)
            count_vars.append(var_var_sets)
            var_var_list.append(var_var)
            dict_count.update(part_composite = var_var_sets)
           
            for j in range(var_var_sets):
                folder_var_var = var_var[j]
                path_var_var = os.path.join(path_var,folder_var_var)
                var_var_var_sets = query_number_subfolder(path_var_var)
                var_var_var = query_list_subdirs(path_var_var)
                count_seq.append(var_var_var)
        else:
            folder_var = var[i]
            path_var = os.path.join(path_temp_out,folder_var)
            var_var_sets = query_number_subfolder(path_var)
            var_var = query_list_subdirs(path_var)
            var_var_list.append(var_var)
            count_vars.append(var_var_sets)
            if var[i] == 'mat_coat':
                dict_count.update(mat_coat = var_var_sets)
            elif var[i] == 'section_coat':
                dict_count.update(section_coat = var_var_sets)
            elif var[i] == 'mat_composite':
                dict_count.update(mat_composite = var_var_sets)
    
    folder_dyna_out = "output"
    sub_fldr_dyna_out = "dyna_cyl"
    path_dyna_out = os.path.join(path,folder_dyna_out,sub_fldr_dyna_out)
    if not os.path.isdir(path_dyna_out):
        os.mkdir(path_dyna_out,mode)    
    #combine, pick and place
    # for i in range(len(count_vars)):#iterate over every variable set
    #     dir = "out_temp"
    #     folder = var[i]
    #     path_fldr = os.path.join(path,dir,folder)
    #     sub_dir_list = query_list_subdirs(path_fldr)
    #     for j in range(count_vars[i]):#Navigate to folder to copy source
    #         sub_dir = sub_dir_list[j]
    #         path_sub_dir = os.path.join(path_fldr,sub_dir)
    #         dest_folder = 
    #Generate possible number of combinations
    print("Combining temporary output files")
    all_list = []
    for p in range(len(count_vars)):
        list_head = gen_list(count_vars[p])
        all_list.extend([list_head]) 
        res_comb = list(itertools.product(*all_list))
    q_set = []    
    for i in range(len(res_comb)):
        dir = "output"
        sub_dir = "dyna_cyl"
        dirname = str(res_comb[i])
        path_dyna_comb = os.path.join(path,dir,sub_dir,dirname)
        if not os.path.isdir(path_dyna_comb):
            os.mkdir(path_dyna_comb,mode)
        #Copying main.k from asset to folder
        asset_main = "asset"
        foldr_main = "dyna_cyl"
        fnam_main = "main.k"
        path_main_src = os.path.join(path,asset_main,foldr_main,fnam_main)
        path_main_dest = os.path.join(path_dyna_comb,fnam_main)
        shutil.copy(path_main_src,path_main_dest)
        for j in range(len(count_vars)):
            fldr = "out_temp"
            dir = var[j]
            if var[j] == 'part_composite':
                for k in range(len(var_var_list[j])):
                    sub_dir_1 = var_var_list[j][k]
                    #print(sub_dir_1)
                    #print (i)
                    #print(j)
                    temp_path = os.path.join(path,fldr,dir,sub_dir_1)
                    q = query_list_subdirs(temp_path)
                    q_set.append(q)
                    if j == 0:
                        sub_foldr = q[1]
                    elif j == 1:
                        sub_foldr = q[1]
                    elif j == 2:
                        sub_foldr = q[7]
                    fnam = var[j] + ".k"
                    temp_path_2 = os.path.join(temp_path,sub_foldr,fnam)
                    path_dest = os.path.join(path_dyna_comb,fnam)
                    shutil.copy(temp_path_2,path_dest)
                    
                
            else:
                sub_dir = var_var_list[j][j]
                fnam = var[j] + ".k"
                path_src = os.path.join(path,fldr,dir,sub_dir,fnam)
                path_dest = os.path.join(path_dyna_comb,fnam)
                shutil.copy(path_src,path_dest)
                #print("Copying from "+path_src+" to "+path_dest)
                
        
    

        
        
        
        
        
            

    
        
    
if __name__ == '__main__':
    # Calling main() function
    main()
