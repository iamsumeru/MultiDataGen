import os
import sys
import linecache
import shutil

class gen_coat:
    def gen_section(self, path, th):
       fname = "section_coat.k"
       name = os.path.join(path,fname)
       fo = open(name,"w")
       fo.write("*SECTION_SHELL_TITLE")
       fo.write("\n")
       fo.write("shell_coat")
       fo.write("\n")
       fo.write("$#   secid    elform      shrf       nip     propt   qr/irid     icomp     setyp")
       fo.write("\n")
       fo.write("         5         2       1.0         2       1.0         0         0         1")
       fo.write("\n")
       fo.write("$#      t1        t2        t3        t4      nloc     marea      idof    edgset")
       fo.write("\n")
       fo.write("      ")
       fo.write(f'{th:.2f}')
       fo.write("      ")
       fo.write(f'{th:.2f}')
       fo.write("      ")
       fo.write(f'{th:.2f}')
       fo.write("      ")
       fo.write(f'{th:.2f}')
       fo.write("       0.0       0.0       0.0         0")
    def gen_mat(self, path, ro, e, pr):
       fname = "mat_coat.k"
       name = os.path.join(path,fname)
       fo = open(name,"w") 
       fo.write("*MAT_ELASTIC_TITLE")
       fo.write("\n")
       fo.write("coat_mat")
       fo.write("\n")
       fo.write("$#     mid        ro         e        pr        da        db  not used        ")
       fo.write("\n")
       fo.write("         5       ")
       fo.write(f'{ro:0.1f}')
       fo.write(f'{e:0.5f}')
       fo.write("E10       ")
       fo.write(f'{pr:0.1f}')
       fo.write("       0.0       0.0       0.0      ")