from src.command_set_py import run_ana_RVE
import sys
import os
path=sys.path[0]
val = [4000,5000,6000,8000]
elas_mat = []
for jind in range(0,2):
    identifier_value = jind + 123
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
