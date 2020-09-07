# Get ABAQUS interface
from abaqus import *
from abaqusConstants import *
import section
import regionToolset
import displayGroupMdbToolset as dgm
import part
import material
import assembly
import step
import interaction
import load
import mesh
import optimization
import job
import sketch
import visualization
import xyPlot
import displayGroupOdbToolset as dgo
import connectorBehavior
#openMdb(pathName='E:/Analyses/FSI/ML_data/working/test/2/digimat/aba_scripts/uni_1/Analysis_uni_1.cae')
#session.viewports['Viewport: 1'].setValues(displayedObject=None)
#a = mdb.models['Analysis_uni_1'].rootAssembly
#session.viewports['Viewport: 1'].setValues(displayedObject=a)
#session.viewports['Viewport: 1'].assemblyDisplay.setValues(optimizationTasks=OFF, geometricRestrictions=OFF, stopConditions=OFF)
#session.mdbData.summary()
# Open the odb
path = os.getcwd()
file="Job_Analysis_uni_1.odb"
file_odb=os.path.join(path,file)
print("path for file is")
print(file_odb)
myOdb = session.openOdb(name=file_odb)
#myOdb = session.openOdb(name='E:/Analyses/FSI/ML_data/working/test/2/digimat/aba_scripts/uni_1/Job_Analysis_uni_1.odb')
session.viewports['Viewport: 1'].setValues(displayedObject=myOdb)
# Get the frame repository for the step, find number of frames (starts at frame 0)
myframes = myOdb.steps['Step-1'].frames[1]
#numFrames = len(frames)
# Isolate the instance, get the number of nodes and elements
myInstance = myOdb.rootAssembly.instances['PART-1-1']
#myInstance = a.instances['MatrixInst']
numNodes = len(myInstance.nodes)
print("Number of nodes ")
print(numNodes)
numElements = len(myInstance.elements)
print("Number of elements ")
print(numElements)
sum_xx_mult = 0
sum_yy_mult = 0
sum_zz_mult = 0
sum_xy_mult = 0
sum_xz_mult = 0
sum_yz_mult = 0
sum_vol = 0
for el in range(0,2):
    # Isolate current and previous element's stress field
    Stress=myOdb.steps['Step-1'].frames[1].fieldOutputs['S'].getSubset(region=myInstance.elements[el],position=CENTROID).values
    Evol=myOdb.steps['Step-1'].frames[1].fieldOutputs['EVOL'].getSubset(region=myInstance.elements[el]).values
    sz_evol = len(Evol)
    sz_Stress = len(Stress)
    for ip in range(0,sz_Stress):
        Sxx = Stress[ip].data[0]
        print ("element"+str(el)+" at ip "+str(ip)+" Sxx "+str(Sxx))
        evolume = Evol[ip].data
        print("e volume "+str(evolume))
        sum_xx_mult = sum_xx_mult + Sxx*evolume
        sum_vol = sum_vol + evolume
        Syy = Stress[ip].data[1]
        sum_yy_mult = sum_yy_mult + Syy*evolume
        Szz = Stress[ip].data[2]
        sum_zz_mult = sum_zz_mult + Szz*evolume
        Sxy = Stress[ip].data[3]
        sum_xy_mult = sum_xy_mult + Sxy*evolume
        Sxz = Stress[ip].data[4]
        sum_xz_mult = sum_xz_mult + Sxz*evolume
        Syz = Stress[ip].data[5]
        sum_yz_mult = sum_yz_mult + Syz*evolume
fo = open('results_uni_1.txt','w+')
Modulus_xx = sum_xx_mult/sum_vol
Modulus_yy = sum_yy_mult/sum_vol
Modulus_zz = sum_zz_mult/sum_vol
Modulus_xy = sum_xy_mult/sum_vol
Modulus_xz = sum_xz_mult/sum_vol
Modulus_yz = sum_yz_mult/sum_vol
print "Generating results for uni_1"
fo.write(str(Modulus_xx)+","+str(Modulus_yy)+","+str(Modulus_zz)+","+str(Modulus_xy)+","+str(Modulus_xz)+","+str(Modulus_yz))
fo.close()
myOdb.close()