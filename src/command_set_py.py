import sys
import os
import shutil
import os.path
import time

class run_ana_RVE:
    def modify_inp(self,case,path,identify,value):
        folder_src = "asset"
        folder_dest_1 = "output"
        folder_name = "temp_RVE_"+str(identify)
        folder_dest = os.path.join(path,folder_dest_1,folder_name)
        if not os.path.isdir(folder_dest):
            mode = 0o666
            os.mkdir(folder_dest,mode)
        path_f_src = os.path.join(path,folder_src)
        path_f_dest = os.path.join(path,folder_dest)
        if case==1:
            subfolder = "digimat_uni_1"
            generator = "uni_1"
        elif case==2:
            subfolder = "digimat_uni_2"
            generator = "uni_2"
        elif case==3:
            subfolder = "digimat_uni_3"
            generator = "uni_3"
        elif case==4:
            subfolder = "digimat_sh_12"
            generator = "sh_12"
        elif case==5:
            subfolder = "digimat_sh_13"
            generator = "sh_13"
        elif case==6:
            subfolder = "digimat_sh_23"
            generator = "sh_23"
        path_sf_src = os.path.join(path_f_src,subfolder)
        script_f_src = "aba_scripts"
        dir_src = os.path.join(path_sf_src,script_f_src)
        path_sf_dest = os.path.join(path_f_dest,subfolder)
        script_f_dest = "aba_scripts"
        dir_dest = os.path.join(path_sf_dest,script_f_dest)
        dir_dest = shutil.copytree(dir_src, dir_dest)  
        os.chdir(dir_dest)
        file_generator_name="Job_"+generator+"_Analysis_"+generator+"_mdbGenerator.py"
        file_generator_rename = "Copy_"+file_generator_name
        os.rename(file_generator_name,file_generator_rename)
        index = 0
        line_mod = "    currentMat.Elastic(type = ISOTROPIC,temperatureDependency=OFF, table=[("+str(value)+",0.35)])"
        with open(file_generator_rename) as f:
            with open(file_generator_name, "w") as f1:
                for line in f:
                    index += 1
                    if index == 199:
                        f1.write(line_mod+'\n')
                        continue
                    f1.write(line)
                

    def gen_out_RVE(self,case,path,identify):
        folder="output"
        print("Case")
        path_f_temp = os.path.join(path,folder)
        folder_name = "temp_RVE_"+str(identify)
        path_f = os.path.join(path_f_temp,folder_name)
        if case==1:
            subfolder = "digimat_uni_1"
            generator = "uni_1"
        elif case==2:
            subfolder = "digimat_uni_2"
            generator = "uni_2"
        elif case==3:
            subfolder = "digimat_uni_3"
            generator = "uni_3"
        elif case==4:
            subfolder = "digimat_sh_12"
            generator = "sh_12"
        elif case==5:
            subfolder = "digimat_sh_13"
            generator = "sh_13"
        elif case==6:
            subfolder = "digimat_sh_23"
            generator = "sh_23"
        print(generator)
        path_sf = os.path.join(path_f,subfolder)
        script_f = "aba_scripts"
        dir = os.path.join(path_sf,script_f)
        os.chdir(dir)
        c1 = "abaqus cae noGUI=Job_"+generator+"_Analysis_"+generator+"_mdbGenerator.py"
        fname_exist_inp = "Job_Analysis_"+generator+".inp"
        fname_exist_odb = "Job_Analysis_"+generator+".odb"
        c2="abaqus job=Job_Analysis_"+generator+".inp"
        c3="abaqus cae noGUI=abq_post_process.py"
        print("Generating ABAQUS inp")
        os.system(c1)
        
        while not os.path.exists(fname_exist_inp):
            time.sleep(1)
        byte_inp = os.stat(fname_exist_inp).st_size
        if byte_inp > 3000000:
            print("Submitting ABAQUS inp")
            os.system(c2)
        else:
            print("Waiting for "+fname_exist_inp)
            time.sleep(1)


        
        while not os.path.exists(fname_exist_odb):
            time.sleep(1)
        
        if os.path.exists(fname_exist_odb):
            
            while True:
                byte_odb = os.stat(fname_exist_odb).st_size
                print("Waiting for"+fname_exist_odb)
                print((byte_odb))
                time.sleep(5)
                if byte_odb > 15000000:
                    print("Running ABAQUS post-processor")
                    os.system(c3)
                    break
        
        
    def combine_RVE(self,case,path,identify):
        folder="output"
        path_f_temp = os.path.join(path,folder)
        folder_name = "temp_RVE_"+str(identify)
        path_f = os.path.join(path_f_temp,folder_name)
        if case==1:
            subfolder = "digimat_uni_1"
            generator = "uni_1"
        elif case==2:
            subfolder = "digimat_uni_2"
            generator = "uni_2"
        elif case==3:
            subfolder = "digimat_uni_3"
            generator = "uni_3"
        elif case==4:
            subfolder = "digimat_sh_12"
            generator = "sh_12"
        elif case==5:
            subfolder = "digimat_sh_13"
            generator = "sh_13"
        elif case==6:
            subfolder = "digimat_sh_23"
            generator = "sh_23"
        path_sf = os.path.join(path_f,subfolder)
        script_f = "aba_scripts"
        dir = os.path.join(path_sf,script_f)
        filename = "results_"+generator+".txt"
        file_out = os.path.join(dir,filename)
        my_data = []
        if os.path.isfile(file_out):
            with open(file_out,'r') as file:
                data = file.read()
            my_data.append(data)
            return my_data
            #print(file_out)
            #print(data)
        else:
            print("Waiting to combine")
            time.sleep(1)

    
 
