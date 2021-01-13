import os
import sys
import linecache
import shutil

class gen_composite:
    def gen_part(self, path, thick, seq):
       print("Generating composite part")
       fname = "part_composite.k"
       name = os.path.join(path,fname)
       fo = open(name,"w")
       fo.write("*PART_COMPOSITE")
       fo.write("\n")
       fo.write("$#                                                                         title")
       fo.write("\n")
       fo.write("                                                                                ")
       fo.write("\n")
       fo.write("$#     pid    elform      shrf      nloc     marea      hgid    adpopt  ithelfrm")
       fo.write("\n")
       fo.write("         4        16    0.8333       0.0       0.0         0         0         0")
       fo.write("\n")
       fo.write("$#    mid1    thick1        b1     tmid1      mid2    thick2        b2     tmid2")
       fo.write("\n")
       n_layers = len(seq)
       for lay in range(n_layers):
           fo.write(f'         3     {thick:.3f}')
           if seq[lay] == 0:
               fo.write("       0.0")
           else:
                fo.write(f'      {seq[lay]:.1f}')
           fo.write("         0")
           if lay % 2 != 0 and lay !=0 and lay !=n_layers-1:
                fo.write("\n")
           else:
                continue
    def gen_mat(self,path,ro, e_axial, e_trans,pr_axial, pr_trans, g_in, g_out,shear_str_in,ten_str_axial,ten_str_trans,comp_str_trans):
          print("Generating mat composite")
          fname = "mat_composite.k"
          name = os.path.join(path,fname)
          fo = open(name,"w")
          fo.write("*MAT_COMPOSITE_DAMAGE_TITLE")
          fo.write("\n")
          fo.write("mat_composite")
          fo.write("\n")
          fo.write("$#     mid        ro        ea        eb        ec      prba      prca      prcb")
          fo.write("\n")
          fo.write("         3       ")
          fo.write(f'{ro:.1f}')
          fo.write(f'{e_axial:.5f}')
          fo.write("E11")
          fo.write(f'{e_trans:.5f}')
          fo.write("E11")
          fo.write(f'{e_trans:.5f}')
          fo.write("E11       ")
          fo.write(f'{pr_axial:.1f}')
          fo.write(f'       {pr_trans:.1f}')
          fo.write(f'       {pr_trans:.1f}')
          fo.write("\n")
          fo.write("$#     gab       gbc       gca     kfail      aopt      macf    atrack      ")
          fo.write("\n")
          fo.write(f'{g_in:.5f}')
          fo.write("E11")
          fo.write(f'{g_out:.5f}')
          fo.write("E11")
          fo.write(f'{g_out:.5f}')
          fo.write("E11")
          fo.write("       0.0       2.0         1         0")
          fo.write("\n")
          fo.write("$#      xp        yp        zp        a1        a2        a3  ")
          fo.write("\n")
          fo.write("       0.0       0.0       0.0       1.0       0.0       0.0")
          fo.write("\n")
          fo.write("$#      v1        v2        v3        d1        d2        d3      beta    ")
          fo.write("\n")
          fo.write("       0.0       0.0       0.0       1.0       0.0       0.0       0.0")
          fo.write("\n")
          fo.write("$#      sc        xt        yt        yc      alph        sn       syz       szx")
          fo.write("\n")
          fo.write(f'{shear_str_in:.6f}')
          fo.write("E8")
          fo.write(f'{ten_str_axial:.6f}')
          fo.write("E9")
          fo.write(f'{ten_str_trans:.6f}')
          fo.write("E9")
          fo.write(f'{comp_str_trans:.6f}')
          fo.write("E9")
          fo.write("       0.0       0.0       0.0       0.0")


'''driver code
pth_x = sys.path[0]
fld = "out_temp"
pth = os.path.join(pth_x,fld)
os.mkdir(pth,0o666)
for i in range(0,2):
     folder_th = "thck_"+str(i) 
     thkns = [4.2,5.6]
     pth_1 = os.path.join(pth,folder_th)
     os.mkdir(pth_1,0o666)
     for j in range(0,2):
          fldr = "seq_"+str(j)
          pth_2 = os.path.join(pth_1,fldr)
          os.mkdir(pth_2,0o666)
          sq = [[0,45,90,90,45,0],[45,90,0,0,90,45]]
          gen_composite.gen_part("",pth_2,thkns[i],sq[j])

'''

