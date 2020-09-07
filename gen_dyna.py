from dev.gen_composite import gen_composite
import os
import linecache
import sys
import shutil
import itertools

def gen_sequence(n_layers):
    gen_lay = int(n_layers/2)
    list_1 = [0,90,45]
    all_list = []
    all_list.extend([list_1 for i in range(n_layers)]) 
    print(all_list)
    res = list(itertools.product(*all_list))
    return res
    
'''    
def choose(n,k):
    if k==0:
        return 1
    elif n<k:
        return 0
    else:
        return choose(n-1,k-1)+choose(n-1,k)
'''
def substrate(self,n_layers,path):
    thickness_composite = []
    for k in range(4,n_layers,2):
        thick = 0.0285*k
        thickness_composite.append(thick)
        sequence = gen_sequence(k)
        # print("initial sequence")
        # print(len(sequence))
        # print(sequence)
        #Filtering sequence: removing identical valued lists
    
        i = 0
        for seq in sequence:
            res = all(ele == seq[0] for ele in seq)
            if(res):
                # print("popping")
                # print(i)
                sequence.pop(i)
            i=i+1
        # print("First seq")
        # print(len(sequence))
        # print(sequence)
        #Filtering sequence: removing >50% identical valued lists
        k1 = 0
        filter_seq = []
        
        for seq in sequence:
            seq_sort = sorted(seq)
            #print("seq_sort")
            #print(seq_sort)
            df_list = []
            freq = 0
            
            for i in range(0,len(seq_sort)-1):
                tmp = seq_sort[i+1]-seq_sort[i]
                #print(tmp)
                df_list.append(tmp)
            #print("df")
            #print(df_list)
            freq = df_list.count(0)
            # print("freqeucny")
            # print(freq)
            if freq == 2:
                # print("adding")
                # print(k)
                filter_seq.append(sequence[k1])
    
            k1 = k1+1
            #print("current k value")
            #print(k)
        # print("generated filtered")
        # print(len(filter_seq))
        # print(filter_seq)
        #check if anti-symmetric
        sequence_final =[]
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
    for th in range(len(thickness_composite)):
        fldr = "thck_"+str(th)
        pth = os.path.join(path,fldr)
        os.mkdir(pth,0o666)
        for gen in range(len(sequence_final)):
            folder = "seq_"+str(gen)
            dest = os.path.join(pth,folder)
            os.mkdir(dest,0o666)
            print("thck")
            print(thickness_composite[th])
            print("sequence")
            print(sequence_final[gen])
            gen_composite.gen_part("",dest,thickness_composite[th],sequence_final[gen])
            
        #Check arrangement in filtered
        # k = 0
        # filter_arrange = []
        
        # for seq in filter_seq:
        #     sz = len(seq)
        #     halv = int(sz/2)
        #     print(halv)
        #     #res_1 = any(i==j for i,j in zip(seq[:halv-1],seq[halv-1:sz-1]))
        #     #res_2 = any(i==j for i,j in zip(seq[halv:],seq[halv+1:]))
        #     res_1 = any(seq[i]==seq[i+1] for i in range(halv-1))
        #     if res_1:
        #         print("satisfy res 1")
        #         print(filter_seq[k])
        #     res_2 = any(seq[i]==seq[i+1] for i in range(halv,sz-1))
            
        #     if (res_1 == False and res_2 == False):
        #         pass
        #     else:
        #         filter_arrange.append(sequence[k])
        #     k = k+1
        # print("filter")
        # print(len(filter_arrange))
        # print(filter_arrange)
        # for filtr in filter_arrange:
        #     res_1 = any(filtr[i]==filtr[i+1] for i in range(1))
        #     print(res_1)
    
    
        
        # ran = len(seq)
        # count_res_1 = 0
        # count_res_2 = 0
        # res_1 = all(ele == seq[3] for ele in seq[0:2])
        # if (res_1):
        #     count_res_1 += 1
        # res_2 = all(ele == seq[0] for ele in seq[1:3])
        # if(res_2):
        #     count_res_2 += 1
        # if(count_res_1 >1 or count_res_2 >1):
        #     print("popping")
        #     print(k)
        #     sequence.pop(k)
        # k=k+1
        
        # print("final sequence")
        # print(len(sequence_final))
        # print(sequence_final)
    

    #gen_composite.gen_part("",dest,thickness_composite[0],seq)
    




def main():
    path = sys.path[0]
    mode = 0o666
    folder = "out_temp"
    dest_temp =os.path.join(path,folder)
    os.mkdir(dest_temp,mode)
    nth_layers = 7
    substrate("",nth_layers,dest_temp)
    
if __name__ == '__main__':
    # Calling main() function
    main()

