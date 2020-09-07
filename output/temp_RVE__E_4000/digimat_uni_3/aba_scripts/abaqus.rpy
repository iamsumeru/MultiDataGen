# -*- coding: mbcs -*-
#
# Abaqus/CAE Release 6.14-1 replay file
# Internal Version: 2014_06_04-18.11.02 134264
# Run by admin on Mon Aug 31 22:47:30 2020
#

# from driverUtils import executeOnCaeGraphicsStartup
# executeOnCaeGraphicsStartup()
#: Executing "onCaeGraphicsStartup()" in the site directory ...
from abaqus import *
from abaqusConstants import *
session.Viewport(name='Viewport: 1', origin=(1.32552, 1.32407), width=195.117, 
    height=131.348)
session.viewports['Viewport: 1'].makeCurrent()
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()
execfile('abq_post_process.py', __main__.__dict__)
#: path for file is
#: e:\Analyses\FSI\app\output\temp_RVE__E_4000\digimat_uni_3\aba_scripts\Job_Analysis_uni_3.odb
#: Model: e:/Analyses/FSI/app/output/temp_RVE__E_4000/digimat_uni_3/aba_scripts/Job_Analysis_uni_3.odb
#: Number of Assemblies:         1
#: Number of Assembly instances: 0
#: Number of Part instances:     1
#: Number of Meshes:             1
#: Number of Element Sets:       53
#: Number of Node Sets:          71
#: Number of Steps:              1
#: Number of nodes 
#: 27841
#: Number of elements 
#: 34843
#: element0 at ip 0 Sxx 5.26867
#: e volume 1.7565991584e-05
#: element1 at ip 0 Sxx 15.9327
#: e volume 1.55154975801e-05
print 'RT script done'
#: RT script done
