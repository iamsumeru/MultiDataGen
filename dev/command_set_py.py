import os
class run_aba:
    def gen_6(self,case):
        path = os.getcwd()
        folder="asset"
        path_f = os.path.join(path,folder)
        if case==1:
            subfolder = "digimat_uni_1"
            generator = "uni_1"
        elif case==2:
            subfolder = "digimat_uni_2"
            generator = "uni_1"
        elif case==3:
            subfolder = "digimat_uni_3"
            generator = "uni_1"
        elif case==4:
            subfolder = "digimat_sh_12"
            generator = "uni_1"
        elif case==5:
            subfolder = "digimat_sh_13"
            generator = "uni_1"
        elif case==6:
            subfolder = "digimat_sh_23"
            generator = "uni_1"
        path_sf = os.path.join(path_f,subfolder)
        script_f = "aba_scripts"
        dir = os.path.join(path_sf,script_f)
        os.chdir(dir)
        #c1="abaqus cae noGUI=job_uni_1_Analysis_uni_1_mdbGenerator.py"
        c1 = "abaqus cae noGUI=job_"+generator+"_Analaysis_"+generator+"_mdbGenerator.py"
        #c2="abaqus job=Job_Analysis_uni_1.inp"
        c2="abaqus job=Job_Analysis_"+generator+".inp"
        c3="abaqus cae noGUI=abq_post_process.py"
        #os.system(c0)
        #os.system(c1)
        #os.system(c2)
        #os.system(c3)