#Digimat Version 2017.0
#Revision : svn-r17131
from abaqusConstants import *
from caeModules import *
import abaqus
import material
import sketch
import part
import assembly
import section
import mesh
import regionToolset
import gc
import os
import sys
import shutil, osutils
import zipfile


def getPyScriptPath():
    pyName = abaqus.getCurrentScriptPath()
    print pyName
    return os.path.dirname(pyName)


def getPyScriptName():
    pyName = abaqus.getCurrentScriptPath()
    pyName = pyName.replace('/','\\')
    toReturn = pyName[pyName.rfind('\\')+1:pyName.rfind('.py')]
    return toReturn


def merge(seq):
    merged = []
    for s in seq:
        for x in s:
            merged.append(x)
    return merged
def equals(a,b):
    tol = 5e-5*(abs(a)+abs(b))/2
    if(abs(a-b)<=tol):
        return 1
    else:
        return 0
def distance(x1,y1,z1,x2,y2,z2):
    dist = sqrt((x1-x2)**2+(y1-y2)**2+(z1-z2)**2)
    return dist

def findVertex(vert,x,y,z):
    toReturn = vert[0]
    minDist = distance(toReturn.pointOn[0][0],toReturn.pointOn[0][1],toReturn.pointOn[0][2],x,y,z)
    for v in vert:
        newDist = distance(v.pointOn[0][0],v.pointOn[0][1],v.pointOn[0][2],x,y,z)
        if(newDist<minDist and (equals(v.pointOn[0][0],x) or equals(v.pointOn[0][1],y) or equals(v.pointOn[0][2],z))):
            minDist = newDist
            toReturn = v
    return toReturn
def findVertex3(myAssembly,x,y,z):
    for inst in myAssembly.instances.values():
        vert = inst.vertices
        if(len(vert)>0):
            v = vert.findAt((x,y,z),)
            if(v!=None):
                return v
    return None
def getValue(f,x):
    if(len(f[0])==0):
        return 0
    if(f[0][0]==x):
        return f[1][0]
    for i in range(len(f[0])):
        if(f[0][i]>=x):
            val = f[1][i-1] + ((x-f[0][i-1])/(f[0][i]-f[0][i-1])) * (f[1][i]-f[1][i-1])
            return val
def functionAdd(f1,f2):
    toReturn=[[],[]]
    if(len(f1[0])==0):
        toReturn[0]=f2[0]
    elif(len(f2[0])==0):
        toReturn[0]=f1[0]
    else:
        j = 0
        i = 0
        tmp = 0.
        while (i < len(f1[0])):
            if(j>=len(f2[0]) or (f1[0][i]<=f2[0][j])):
                tmp=f1[0][i]
                i = i+1
            else:
                tmp=f2[0][j]
                j = j+1
            if(len(toReturn[0])==0):
                toReturn[0].append(tmp)
            else:
                if(toReturn[0][len(toReturn[0])-1]!=tmp):
                    toReturn[0].append(tmp)
        for i in range(len(toReturn[0])):
            toReturn[1].append(getValue(f1,toReturn[0][i])+getValue(f2,toReturn[0][i]))
    return toReturn
def functionMult(a,f1):
    toReturn=[[],[]]
    toReturn[0]=f1[0]
    for i in f1[1]:
        toReturn[1].append(a*i)
    return toReturn
def getFuncData(f):
    toReturn=[]
    for i in range(len(f[0])):
        toReturn.append([f[0][i],f[1][i]])
    return toReturn
def equalCentroid(a,b,tol):
    if(distSq(a[0],a[1],a[2],b[0],b[1],b[2])<tol):
        return 1
    else:
        return 0
def distSq(x1,y1,z1,x2,y2,z2):
    dist = (x1-x2)**2+(y1-y2)**2+(z1-z2)**2
    return dist
def findVertex2(vert,x,y,z):
    for v in vert:
        if(equals(v.pointOn[0][0],x) and equals(v.pointOn[0][1],y) and equals(v.pointOn[0][2],z)):
            return v
    return None
def isFaceExternal(face,sizeRVE):
    currentCentroid=face.getCentroid()
    if(equals(currentCentroid[0][0],sizeRVE[0]) or equals(currentCentroid[0][1],sizeRVE[1]) or equals(currentCentroid[0][2],sizeRVE[2]) or equals(currentCentroid[0][0],0) or equals(currentCentroid[0][1],0) or equals(currentCentroid[0][2],0)):
        return 1
    else:
        return 0
def getConnectedFaces(instance,face,treatedFaces,connectedFaces,sizeRVE):
    if(not treatedFaces[face.index]):
        if(isFaceExternal(face,sizeRVE)):
            treatedFaces[face.index]=1
            return 0
        faceEdges = face.getEdges()
        connectedFaces.append(face.index);
        treatedFaces[face.index]=1
        for e in faceEdges:
            currentEdge = instance.edges[e]
            connectedFacesId=currentEdge.getFaces();
            for conId in connectedFacesId:
                if(not treatedFaces[conId]):
                    getConnectedFaces(instance,instance.faces[conId],treatedFaces,connectedFaces,sizeRVE)
def getSurfaceCentroid(surface,sizeRVE):
    myFaces = surface.faces
    centroid = [0.,0.,0.]
    totalSize = 0
    for f in myFaces:
        if(not isFaceExternal(f,sizeRVE)):
            s = f.getSize(printResults=False)
            c = f.getCentroid()
            totalSize = totalSize+s
            for i in range(3):
                centroid[i] = centroid[i]+s*c[0][i]
    for i in range(3):
        centroid[i] = centroid[i]/totalSize
    return centroid
def getSurfaceArea(surface,sizeRVE):
    myFaces = surface.faces
    totalSize=0
    for f in myFaces:
        s = f.getSize(printResults=False)
        if(not isFaceExternal(f,sizeRVE)):
            totalSize = totalSize + s
    return totalSize
def isEdgeOnBoundary(edgeId,instance,sizeRVE):
    edge = instance.edges[edgeId]
    try:
        edge.getCurvature(parameter=0.5)
    except:
        tmpVert = edge.getVertices()
        if(len(tmpVert)<2):
            return 0
        v1 = instance.vertices[tmpVert[0]].pointOn[0]
        v2 = instance.vertices[tmpVert[1]].pointOn[0]
        nb = 0
        for i in range(3):
            if(equals(v1[i],v2[i]) and (equals(v1[i],0) or equals(v1[i],sizeRVE[i]))):
                nb = nb+1
        if(nb>=2):
            return 1
        else:
            return 0
    else:
        return 0
def main():
    pyPath = getPyScriptPath()


    if(pyPath==''):
        raise AbaqusException, 'abaqus replay file not found'
    os.chdir(pyPath)
    mdb = Mdb(pathName=pyPath+'/Analysis_sh_23.cae')
    myModel = mdb.Model(name='Analysis_sh_23')
    myAssembly = myModel.rootAssembly
    mappedMeshFlag = 1
    currentMat = myModel.Material(name='matrix')
    currentMat.Density(table=((1100,),))
    currentMat.Elastic(type = ISOTROPIC,temperatureDependency=OFF, table=[(5000,0.35)])
    myModel.HomogeneousSolidSection(name='matrix_Section',material='matrix')
    currentMat = myModel.Material(name='CF')
    currentMat.Density(table=((1800,),))
    currentMat.Elastic(type = ENGINEERING_CONSTANTS,temperatureDependency=OFF, table=[(15000,15000,230000,0.2,0.00456522,0.00456522,6250,15000,15000)])
    myModel.HomogeneousSolidSection(name='CF_Section',material='CF')
    matrixFilePath = []
    phaseIsCoating = {}
    phaseUse3DCohesive = {}
    sizeCube = []
    phaseUse3DCohesive['Phase2']=0
    zf = zipfile.ZipFile(pyPath+'/'+getPyScriptName()+'_geomData.zip','r')
    listOfFiles = zf.namelist()
    for f in listOfFiles:
        tmpF = open(pyPath+'/'+f,'wb')
        bytes = zf.read(f)
        tmpF.write(bytes)
        tmpF.close()
    inst=[]
    partNames={}
    print 'Importing matrix phase 1\n'
    myAcis = mdb.openParasolid(pyPath+'/Job_sh_23_Analysis_sh_23_Phase1_uncut.xmt_txt',topology=SOLID)
    if(myAcis.numberOfParts>1):
        inst2=[]
        for j in range(1,myAcis.numberOfParts+1):
            myName = 'Job_sh_23_Analysis_sh_23_Pha~1_'+str(j)
            myModel.PartFromGeometryFile(myName,myAcis,THREE_D,DEFORMABLE_BODY,scale=0.001)
            instanceName = myName
            tmpInst = myAssembly.Instance(name=instanceName,part=myModel.parts[myName],autoOffset=OFF,dependent=ON)
            inst2.append(tmpInst)
        matrixInst = myAssembly.InstanceFromBooleanMerge(name='Job_sh_23_Analysis_sh_23_Pha~1',instances=inst2,keepIntersections=OFF,originalInstances=SUPRESS,domain=GEOMETRY)
    else:
        myName='Job_sh_23_Analysis_sh_23_Pha~1'
        myModel.PartFromGeometryFile(myName,myAcis,THREE_D,DEFORMABLE_BODY,scale=0.001)
        instanceName = myName
        matrixPart = myModel.parts[myName]
        matrixInst = myAssembly.Instance(name=instanceName,part=matrixPart,autoOffset=OFF,dependent=ON)
    matrixSet=0
    myAttributes = matrixPart.queryAttributes()
    if(myAttributes['numCells']==0 and myAttributes['numWireEdges']>0):
        matrixSet = matrixPart.Set(name='SetJob_sh_23_Analysis_sh_23_Pha~1',edges=matrixPart.edges)
    else:
        matrixSet = matrixPart.Set(name='SetJob_sh_23_Analysis_sh_23_Pha~1',cells=matrixPart.cells)    
    inst.append(matrixInst)
    if(len(inst)>1):
        matrixInst = myAssembly.InstanceFromBooleanMerge(name='Matrix',instances=inst,keepIntersections=ON,originalInstances=SUPPRESS, domain=GEOMETRY)
        matrixPart = myModel.parts['Matrix']
    else:
        matrixInst = inst[0]
        matrixPart = myModel.Part(name='Matrix',objectToCopy=myModel.parts['Job_sh_23_Analysis_sh_23_Pha~1'])
    matrixSet = matrixPart.Set(name='SetMatrix',cells=matrixPart.cells)
    dict = matrixPart.queryGeometry()
    sizeCube.append(dict['boundingBox'][1][0])
    sizeCube.append(dict['boundingBox'][1][1])
    sizeCube.append(dict['boundingBox'][1][2])
    inst=[]
    numberOfInclusionPerPhase=[]
    partNames['Phase2']=[]
    myAcisIncl = mdb.openParasolid(pyPath+'/Job_sh_23_Analysis_sh_23_Phase2.xmt_txt',topology=SOLID)
    print 'Importing phase 1\n'
    print myAcisIncl.numberOfParts
    numberOfInclusionPerPhase.append(myAcisIncl.numberOfParts)
    for j in range(1,myAcisIncl.numberOfParts+1):
        print 'Importing inclusion '+str(j)+' in phase Phase2\n'
        myName = 'Phase2_'+str(j)
        print myName
        partNames['Phase2'].append(myName)
        myModel.PartFromGeometryFile(str(myName),myAcisIncl,THREE_D,DEFORMABLE_BODY,bodyNum=j,scale=0.001)
        instanceName = 'Phase2_'+str(j)
        p = myModel.parts['Phase2_'+str(j)]
        currentSet=0
        myAttributes = p.queryAttributes()
        if(myAttributes['numCells']==0 and myAttributes['numWireEdges']>0):
            currentSet = p.Set(name='SetPhase2_'+str(j),edges=p.edges)
        else:
            currentSet = p.Set(name='SetPhase2_'+str(j),cells=p.cells)
        myAssembly.Instance(name=instanceName,part=myModel.parts['Phase2_'+str(j)],autoOffset=OFF,dependent=ON)
        inst.append(myAssembly.instances[instanceName])
    if(len(inst)>1):
        phasePartInst = myAssembly.InstanceFromBooleanMerge(name='Phase2',instances=inst,keepIntersections=ON,originalInstances=SUPPRESS, domain=GEOMETRY)
    else:
        myModel.Part(name='Phase2',objectToCopy=myModel.parts['Phase2_'+str(j)])
    phasePart = myModel.parts['Phase2']
    phaseSet=0
    myAttributes = phasePart.queryAttributes()
    if(myAttributes['numCells']==0 and myAttributes['numWireEdges']>0):
        phaseSet = phasePart.Set(name='SetPhase2',edges=phasePart.edges)    
    else:
        phaseSet = phasePart.Set(name='SetPhase2',cells=phasePart.cells)    
    inst=[]
    myAssembly.deleteAllFeatures()
    for f in listOfFiles:
        os.remove(pyPath+'/'+f)
    inst=[]
    myAssembly.Instance(name='Phase2',part=myModel.parts['Phase2'],autoOffset=OFF,dependent=ON)
    matrixInst = myAssembly.Instance(name='MatrixInst',part=matrixPart,autoOffset=OFF,dependent=ON)
    inst = []
    if(len(inst)>0):
        myAssembly.InstanceFromBooleanCut(name='matrixVoidsCut',instanceToBeCut=matrixInst,cuttingInstances=inst)
        matrixPart = myModel.parts['matrixVoidsCut']
        matrixInst = myAssembly.instances['matrixVoidsCut-1']
        matrixSet = matrixPart.Set(name='SetMatrix',cells=matrixPart.cells)
    else:
        matrixPart = myModel.Part(name='matrixVoidsCut',objectToCopy=matrixPart)
    inst = []
    instIncl = []
    myAssembly.deleteAllFeatures()
    matrixInst = myAssembly.Instance(name='MatrixInst',part=myModel.parts['matrixVoidsCut'],autoOffset=OFF,dependent=ON)
    myAssembly.Instance(name='Phase2',part=myModel.parts['Phase2'],autoOffset=OFF,dependent=ON)
    instIncl.append(myAssembly.instances['Phase2'])
    if len(instIncl)>0:
        matrixInstCut = myAssembly.InstanceFromBooleanCut(name='matrixCut',instanceToBeCut=matrixInst,cuttingInstances=instIncl)
        matrixPart = myModel.parts['matrixCut']
    else:
        matrixPart = myModel.Part(name='matrixCut',objectToCopy=matrixPart)
    myAssembly.deleteAllFeatures()
    matrixInst = myAssembly.Instance(name='MatrixInst',part=myModel.parts['matrixCut'],autoOffset=OFF,dependent=ON)
    inclSurf = {}
    inclSurfArea = {}
    inclSurfCentroid = {}
    inclSurfInstName = {}
    inclSurf['Phase2']=[]
    inclSurfArea['Phase2']=[]
    inclSurfCentroid['Phase2']=[]
    inclSurfInstName['Phase2']=[]
    for j in range(len(partNames['Phase2'])):
        myAssembly.Instance(name=partNames['Phase2'][j],part=myModel.parts[partNames['Phase2'][j]],autoOffset=OFF,dependent=ON)
    currentInclCells=[]
    for j in range(len(partNames['Phase2'])):
        currentInst = myAssembly.instances[partNames['Phase2'][j]]
        cells = currentInst.cells
        name='Surf_'+partNames['Phase2'][j]
        surfFaces=[]
        surfFacesId = cells[0].getFaces()
        for tmpId in surfFacesId:
            if(not isFaceExternal(currentInst.faces[tmpId],sizeCube)):
                surfFaces.append(currentInst.faces[tmpId:tmpId+1])
        s = myAssembly.Surface(side1Faces=surfFaces,name=name)
        inclSurf['Phase2'].append(s)
        inclSurfArea['Phase2'].append(getSurfaceArea(s,sizeCube))
        inclSurfCentroid['Phase2'].append(getSurfaceCentroid(s,sizeCube))
        inclSurfInstName['Phase2'].append(currentInst.name)
    #create the surfaces on the matrix phase
    matrixSurf = []
    matrixSurfArea = []
    matrixSurfCentroid = []
    matrixFaces = myAssembly.instances['MatrixInst'].faces
    treatedFaces = []
    for i in range(len(matrixFaces)):
        treatedFaces.append(0)
    i=0
    surfCounter = 0
    for f in matrixFaces:
        connectedFaces=[]
        getConnectedFaces(myAssembly.instances['MatrixInst'],f,treatedFaces,connectedFaces,sizeCube)
        if(len(connectedFaces)>0):
            surfCounter = surfCounter+1
            surf=[]
            for id in connectedFaces:
                surf.append(matrixFaces[id:id+1])
            name = 'Matrix_'+str(surfCounter)
            s = myAssembly.Surface(side1Faces=surf,name=name)
            matrixSurf.append(s)
            matrixSurfArea.append(getSurfaceArea(s,sizeCube))
            matrixSurfCentroid.append(getSurfaceCentroid(s,sizeCube))
    totalContactCount = 1
    for i in range(len(inclSurf['Phase2'])):
        s = inclSurf['Phase2'][i]
        c = inclSurfCentroid['Phase2'][i]
        area = inclSurfArea['Phase2'][i]
        for j in range(len(matrixSurf)):
            c2 = matrixSurfCentroid[j]
            area2 = matrixSurfArea[j]
            s2 = matrixSurf[j]
            if(equalCentroid(c,c2,0.0001)==1 and equals(area,area2)==1):
                myModel.Tie(name='Tie'+str(totalContactCount),master=s2,slave=s,positionToleranceMethod=COMPUTED,adjust=ON,thickness=ON,constraintEnforcement=SURFACE_TO_SURFACE)
                totalContactCount = totalContactCount + 1
                break
    continueFlag=YES
    currentInclPhaseCells=[]
    for j in range(len(partNames['Phase2'])):
        currentInst = myAssembly.instances[partNames['Phase2'][j]]
        cells = currentInst.cells
        currentInclPhaseCells.append(cells[0:len(cells)])
    myAssembly.Set(name='Phase2',cells=currentInclPhaseCells)
    if(continueFlag==NO):
        mdb.saveAs(pathName=pyPath+'/Analysis_sh_23.cae')
        return 0;
    tmpPart = myModel.parts['Phase2_1']
    tmpPart.DatumCsysByThreePoints(name='Phase2_1CSYS',coordSysType=CARTESIAN,origin=(0,0,0),point1=(3.7494e-033,6.12323e-017,-1),point2=(-1,6.12323e-017,0))
    a = tmpPart.datums.keys()[len(tmpPart.datums.keys())-1]
    region = tmpPart.sets['SetPhase2_1']
    tmpPart.MaterialOrientation(region=region, orientationType=SYSTEM, localCsys=tmpPart.datums[a])
    for j in range(len(partNames['Phase2'])):
        region = myModel.parts[partNames['Phase2'][j]].sets['Set'+partNames['Phase2'][j]]
        myModel.parts[partNames['Phase2'][j]].SectionAssignment(region=region,sectionName='CF_Section', offset=0.0)
    region = myModel.parts['matrixCut'].sets['SetJob_sh_23_Analysis_sh_23_Pha~1']
    myModel.parts['matrixCut'].SectionAssignment(region=region,sectionName='matrix_Section', offset=0.0)
    myAssembly.regenerate()
    a=sizeCube[0]
    b=sizeCube[1]
    c=sizeCube[2]
    setXsupAssembly=0
    XsupFaces=[]
    setYsupAssembly=0
    YsupFaces=[]
    setZsupAssembly=0
    ZsupFaces=[]
    setXinfAssembly=0
    XinfFaces=[]
    setYinfAssembly=0
    YinfFaces=[]
    setZinfAssembly=0
    ZinfFaces=[]
    XsupEdgesToExclude=[]
    XsupVertToExclude=[]
    YsupEdgesToExclude=[]
    YsupVertToExclude=[]
    ZsupEdgesToExclude=[]
    ZsupVertToExclude=[]
    XinfEdgesToExclude=[]
    XinfVertToExclude=[]
    YinfEdgesToExclude=[]
    YinfVertToExclude=[]
    ZinfEdgesToExclude=[]
    ZinfVertToExclude=[]
    #matrix
    matrixInst = myAssembly.instances['MatrixInst']
    allCells=[]
    for inst in myAssembly.instances.values():
        cells=inst.cells
        allCells.append(cells[0:len(cells)])
        excludeFlag = 1
        partName = inst.partName
        if(not inst==matrixInst):
            partName = partName[0:partName.rfind('_')]
            if(phaseUse3DCohesive.has_key(partName) and phaseUse3DCohesive[partName]):
                excludeFlag = 0
            if(phaseIsCoating.has_key(partName+'_ctg')):
                excludeFlag = 0
        f1 = inst.faces
        for i in range(len(f1)):
            currentFace = f1[i]
            currentCentroid=currentFace.getCentroid()
            if(equals(currentCentroid[0][0],a)):
                XsupFaces.append(f1[i:i+1])
                if(not inst==matrixInst and excludeFlag==1):   
                    tmpE = f1[i].getEdges()
                    for e in tmpE:
                        if(isEdgeOnBoundary(e,inst,sizeCube)):
                            tmpVert=inst.edges[e].getVertices()
                            vert0=tmpVert[0]
                            vert1=tmpVert[1]
                            XsupVertToExclude.append(inst.vertices[vert0:vert0+1])
                            XsupVertToExclude.append(inst.vertices[vert1:vert1+1])
                        else:
                            XsupEdgesToExclude.append(inst.edges[e:e+1])
            elif(equals(currentCentroid[0][1],b)):
                YsupFaces.append(f1[i:i+1])
                if(not inst==matrixInst and excludeFlag==1):   
                    tmpE = f1[i].getEdges()
                    for e in tmpE:
                        if(isEdgeOnBoundary(e,inst,sizeCube)):
                            tmpVert=inst.edges[e].getVertices()
                            vert0=tmpVert[0]
                            vert1=tmpVert[1]
                            YsupVertToExclude.append(inst.vertices[vert0:vert0+1])
                            YsupVertToExclude.append(inst.vertices[vert1:vert1+1])
                        else:
                            YsupEdgesToExclude.append(inst.edges[e:e+1])
            elif(equals(currentCentroid[0][2],c)):
                ZsupFaces.append(f1[i:i+1])
                if(not inst==matrixInst and excludeFlag==1):   
                    tmpE = f1[i].getEdges()
                    for e in tmpE:
                        if(isEdgeOnBoundary(e,inst,sizeCube)):
                            tmpVert=inst.edges[e].getVertices()
                            vert0=tmpVert[0]
                            vert1=tmpVert[1]
                            ZsupVertToExclude.append(inst.vertices[vert0:vert0+1])
                            ZsupVertToExclude.append(inst.vertices[vert1:vert1+1])
                        else:
                            ZsupEdgesToExclude.append(inst.edges[e:e+1])
            elif(equals(currentCentroid[0][0],0)):
                XinfFaces.append(f1[i:i+1])
                if(not inst==matrixInst and excludeFlag==1):   
                    tmpE = f1[i].getEdges()
                    for e in tmpE:
                        if(isEdgeOnBoundary(e,inst,sizeCube)):
                            tmpVert=inst.edges[e].getVertices()
                            vert0=tmpVert[0]
                            vert1=tmpVert[1]
                            XinfVertToExclude.append(inst.vertices[vert0:vert0+1])
                            XinfVertToExclude.append(inst.vertices[vert1:vert1+1])
                        else:
                            XinfEdgesToExclude.append(inst.edges[e:e+1])
            elif(equals(currentCentroid[0][1],0)):
                YinfFaces.append(f1[i:i+1])
                if(not inst==matrixInst and excludeFlag==1):   
                    tmpE = f1[i].getEdges()
                    for e in tmpE:
                        if(isEdgeOnBoundary(e,inst,sizeCube)):
                            tmpVert=inst.edges[e].getVertices()
                            vert0=tmpVert[0]
                            vert1=tmpVert[1]
                            YinfVertToExclude.append(inst.vertices[vert0:vert0+1])
                            YinfVertToExclude.append(inst.vertices[vert1:vert1+1])
                        else:
                            YinfEdgesToExclude.append(inst.edges[e:e+1])
            elif(equals(currentCentroid[0][2],0)):
                ZinfFaces.append(f1[i:i+1])
                if(not inst==matrixInst and excludeFlag==1):   
                    tmpE = f1[i].getEdges()
                    for e in tmpE:
                        if(isEdgeOnBoundary(e,inst,sizeCube)):
                            tmpVert=inst.edges[e].getVertices()
                            vert0=tmpVert[0]
                            vert1=tmpVert[1]
                            ZinfVertToExclude.append(inst.vertices[vert0:vert0+1])
                            ZinfVertToExclude.append(inst.vertices[vert1:vert1+1])
                        else:
                            ZinfEdgesToExclude.append(inst.edges[e:e+1])
    setAllCells = myAssembly.Set(name='allRVE',cells=allCells)
    setXsupAssembly = myAssembly.Set(name='xsup',faces=XsupFaces,xEdges=XsupEdgesToExclude,xVertices=XsupVertToExclude)
    setYsupAssembly = myAssembly.Set(name='ysup',faces=YsupFaces,xEdges=YsupEdgesToExclude,xVertices=YsupVertToExclude)
    setZsupAssembly = myAssembly.Set(name='zsup',faces=ZsupFaces,xEdges=ZsupEdgesToExclude,xVertices=ZsupVertToExclude)
    setXinfAssembly = myAssembly.Set(name='xinf',faces=XinfFaces,xEdges=XinfEdgesToExclude,xVertices=XinfVertToExclude)
    setYinfAssembly = myAssembly.Set(name='yinf',faces=YinfFaces,xEdges=YinfEdgesToExclude,xVertices=YinfVertToExclude)
    setZinfAssembly = myAssembly.Set(name='zinf',faces=ZinfFaces,xEdges=ZinfEdgesToExclude,xVertices=ZinfVertToExclude)
    z0y0Edges=[]
    z0ybEdges=[]
    zcybEdges=[]
    zcy0Edges=[]
    x0z0Edges=[]
    x0zcEdges=[]
    xazcEdges=[]
    xaz0Edges=[]
    x0y0Edges=[]
    x0ybEdges=[]
    xaybEdges=[]
    xay0Edges=[]
    for inst in myAssembly.instances.values():
        e1 = inst.edges
        for i in range(len(e1)):
            currentEdge=e1[i]
            p=currentEdge.pointOn
            if(equals(p[0][1],0) and equals(p[0][2],0)):
                z0y0Edges.append(e1[i:i+1])
            if(equals(p[0][1],b) and equals(p[0][2],0)):
                z0ybEdges.append(e1[i:i+1])
            if(equals(p[0][1],b) and equals(p[0][2],c)):
                zcybEdges.append(e1[i:i+1])
            if(equals(p[0][1],0) and equals(p[0][2],c)):
                zcy0Edges.append(e1[i:i+1])
            if(equals(p[0][0],0) and equals(p[0][2],0)):
                x0z0Edges.append(e1[i:i+1])
            if(equals(p[0][0],0) and equals(p[0][2],c)):
                x0zcEdges.append(e1[i:i+1])
            if(equals(p[0][0],a) and equals(p[0][2],c)):
                xazcEdges.append(e1[i:i+1])
            if(equals(p[0][0],a) and equals(p[0][2],0)):
                xaz0Edges.append(e1[i:i+1])
            if(equals(p[0][0],0) and equals(p[0][1],0)):
                x0y0Edges.append(e1[i:i+1])
            if(equals(p[0][0],0) and equals(p[0][1],b)):
                x0ybEdges.append(e1[i:i+1])
            if(equals(p[0][0],a) and equals(p[0][1],b)):
               xaybEdges.append(e1[i:i+1])
            if(equals(p[0][0],a) and equals(p[0][1],0)):
               xay0Edges.append(e1[i:i+1])
    myXedges=xaybEdges,xay0Edges,xazcEdges,xaz0Edges,XsupEdgesToExclude
    setXsupNoEdgesAssembly = myAssembly.Set(name='xsupNoEdges',faces=XsupFaces,xEdges=merge(myXedges),xVertices=XsupVertToExclude)
    myXedges=zcybEdges,z0ybEdges,x0ybEdges,xaybEdges,YsupEdgesToExclude
    setYsupNoEdgesAssembly = myAssembly.Set(name='ysupNoEdges',faces=YsupFaces,xEdges=merge(myXedges),xVertices=YsupVertToExclude)
    myXedges=zcy0Edges,zcybEdges,x0zcEdges,xazcEdges,ZsupEdgesToExclude
    setZsupNoEdgesAssembly = myAssembly.Set(name='zsupNoEdges',faces=ZsupFaces,xEdges=merge(myXedges),xVertices=ZsupVertToExclude)
    myXedges=x0ybEdges,x0y0Edges,x0z0Edges,x0zcEdges,XinfEdgesToExclude
    setXinfNoEdgesAssembly = myAssembly.Set(name='xinfNoEdges',faces=XinfFaces,xEdges=merge(myXedges),xVertices=XinfVertToExclude)
    myXedges=zcy0Edges,z0y0Edges,x0y0Edges,xay0Edges,YinfEdgesToExclude
    setYinfNoEdgesAssembly = myAssembly.Set(name='yinfNoEdges',faces=YinfFaces,xEdges=merge(myXedges),xVertices=YinfVertToExclude)
    myXedges=x0z0Edges,xaz0Edges,z0y0Edges,z0ybEdges,ZinfEdgesToExclude
    setZinfNoEdgesAssembly = myAssembly.Set(name='zinfNoEdges',faces=ZinfFaces,xEdges=merge(myXedges),xVertices=ZinfVertToExclude)
    myXedges=zcybEdges,z0ybEdges,YsupEdgesToExclude
    setYsupNoXEdgesAssembly = myAssembly.Set(name='ysupNoXEdges',faces=YsupFaces,xEdges=merge(myXedges),xVertices=YsupVertToExclude)
    myXedges=x0ybEdges,xaybEdges,YsupEdgesToExclude
    setYsupNoZEdgesAssembly = myAssembly.Set(name='ysupNoZEdges',faces=YsupFaces,xEdges=merge(myXedges),xVertices=YsupVertToExclude)
    myXedges=zcy0Edges,zcybEdges,ZsupEdgesToExclude
    setZsupNoXEdgesAssembly = myAssembly.Set(name='zsupNoXEdges',faces=ZsupFaces,xEdges=merge(myXedges),xVertices=ZsupVertToExclude)
    myXedges=x0zcEdges,xazcEdges,ZsupEdgesToExclude
    setZsupNoYEdgesAssembly = myAssembly.Set(name='zsupNoYEdges',faces=ZsupFaces,xEdges=merge(myXedges),xVertices=ZsupVertToExclude)
    myXedges=zcy0Edges,z0y0Edges,YinfEdgesToExclude
    setYinfNoXEdgesAssembly = myAssembly.Set(name='yinfNoXEdges',faces=YinfFaces,xEdges=merge(myXedges),xVertices=YinfVertToExclude)
    myXedges=x0y0Edges,xay0Edges,YinfEdgesToExclude
    setYinfNoZEdgesAssembly = myAssembly.Set(name='yinfNoZEdges',faces=YinfFaces,xEdges=merge(myXedges),xVertices=YinfVertToExclude)
    myXedges=z0y0Edges,z0ybEdges,ZinfEdgesToExclude
    setZinfNoXEdgesAssembly = myAssembly.Set(name='zinfNoXEdges',faces=ZinfFaces,xEdges=merge(myXedges),xVertices=ZinfVertToExclude)
    myXedges=x0z0Edges,xaz0Edges,ZinfEdgesToExclude
    setZinfNoYEdgesAssembly = myAssembly.Set(name='zinfNoYEdges',faces=ZinfFaces,xEdges=merge(myXedges),xVertices=ZinfVertToExclude)
    cornerX0Y0Z0=[]
    cornerX0Y0Zc=[]
    cornerX0YbZc=[]
    cornerX0YbZ0=[]
    cornerXaY0Z0=[]
    cornerXaY0Zc=[]
    cornerXaYbZc=[]
    cornerXaYbZ0=[]
    allVert = []
    for inst in myAssembly.instances.values():
        tmpVert = inst.vertices
        for v in tmpVert:
            allVert.append(v)
    v=findVertex3(myAssembly,0,0,0)
    if(v!=None):
        vert = myAssembly.instances[v.instanceName].vertices
        cornerX0Y0Z0.append(vert[v.index:v.index+1])
    else:
        v = findVertex(allVert,0,0,0)
        vert = myAssembly.instances[v.instanceName].vertices
        cornerX0Y0Z0.append(vert[v.index:v.index+1])
    v=findVertex3(myAssembly,0,0,sizeCube[2])
    if(v!=None):
        vert = myAssembly.instances[v.instanceName].vertices
        cornerX0Y0Zc.append(vert[v.index:v.index+1])
    else:
        v = findVertex(allVert,0,0,sizeCube[2])
        vert = myAssembly.instances[v.instanceName].vertices
        cornerX0Y0Zc.append(vert[v.index:v.index+1])
    v=findVertex3(myAssembly,0,sizeCube[1],sizeCube[2])
    if(v!=None):
        vert = myAssembly.instances[v.instanceName].vertices
        cornerX0YbZc.append(vert[v.index:v.index+1])
    else:
        v = findVertex(allVert,0,sizeCube[1],sizeCube[2])
        vert = myAssembly.instances[v.instanceName].vertices
        cornerX0YbZc.append(vert[v.index:v.index+1])
    v=findVertex3(myAssembly,0,sizeCube[1],0)
    if(v!=None):
        vert = myAssembly.instances[v.instanceName].vertices
        cornerX0YbZ0.append(vert[v.index:v.index+1])
    else:
        v = findVertex(allVert,0,sizeCube[1],0)
        vert = myAssembly.instances[v.instanceName].vertices
        cornerX0YbZ0.append(vert[v.index:v.index+1])
    v=findVertex3(myAssembly,sizeCube[0],0,0)
    if(v!=None):
        vert = myAssembly.instances[v.instanceName].vertices
        cornerXaY0Z0.append(vert[v.index:v.index+1])
    else:
        v = findVertex(allVert,sizeCube[0],0,0)
        vert = myAssembly.instances[v.instanceName].vertices
        cornerXaY0Z0.append(vert[v.index:v.index+1])
    v=findVertex3(myAssembly,sizeCube[0],0,sizeCube[2])
    if(v!=None):
        vert = myAssembly.instances[v.instanceName].vertices
        cornerXaY0Zc.append(vert[v.index:v.index+1])
    else:
        v = findVertex(allVert,sizeCube[0],0,sizeCube[2])
        vert = myAssembly.instances[v.instanceName].vertices
        cornerXaY0Zc.append(vert[v.index:v.index+1])
    v=findVertex3(myAssembly,sizeCube[0],sizeCube[1],sizeCube[2])
    if(v!=None):
        vert = myAssembly.instances[v.instanceName].vertices
        cornerXaYbZc.append(vert[v.index:v.index+1])
    else:
        v = findVertex(allVert,sizeCube[0],sizeCube[1],sizeCube[2])
        vert = myAssembly.instances[v.instanceName].vertices
        cornerXaYbZc.append(vert[v.index:v.index+1])
    v=findVertex3(myAssembly,sizeCube[0],sizeCube[1],0)
    if(v!=None):
        vert = myAssembly.instances[v.instanceName].vertices
        cornerXaYbZ0.append(vert[v.index:v.index+1])
    else:
        v = findVertex(allVert,sizeCube[0],sizeCube[1],0)
        vert = myAssembly.instances[v.instanceName].vertices
        cornerXaYbZ0.append(vert[v.index:v.index+1])
    if(len(cornerX0Y0Z0)>0):
        myAssembly.Set(name='point1',vertices=cornerX0Y0Z0)
    if(len(cornerX0Y0Zc)>0):
        myAssembly.Set(name='point2',vertices=cornerX0Y0Zc)
    if(len(cornerX0YbZc)>0):
        myAssembly.Set(name='point3',vertices=cornerX0YbZc)
    if(len(cornerX0YbZ0)>0):
        myAssembly.Set(name='point4',vertices=cornerX0YbZ0)
    if(len(cornerXaY0Z0)>0):
        myAssembly.Set(name='point5',vertices=cornerXaY0Z0)
    if(len(cornerXaY0Zc)>0):
        myAssembly.Set(name='point6',vertices=cornerXaY0Zc)
    if(len(cornerXaYbZc)>0):
        myAssembly.Set(name='point7',vertices=cornerXaYbZc)
    if(len(cornerXaYbZ0)>0):
        myAssembly.Set(name='point8',vertices=cornerXaYbZ0)
    myxVertices=cornerXaY0Z0,cornerXaY0Zc,cornerXaYbZc,cornerXaYbZ0,XsupVertToExclude
    setXsupNoCornerAssembly = myAssembly.Set(name='xsupNoCorner',faces=XsupFaces,xVertices=merge(myxVertices))
    myxVertices=cornerX0YbZc,cornerX0YbZ0,cornerXaYbZc,cornerXaYbZ0,YsupVertToExclude
    setYsupNoCornerAssembly = myAssembly.Set(name='ysupNoCorner',faces=YsupFaces,xVertices=merge(myxVertices))
    myxVertices=cornerX0Y0Zc,cornerX0YbZc,cornerXaY0Zc,cornerXaYbZc,ZsupVertToExclude
    setZsupNoCornerAssembly = myAssembly.Set(name='zsupNoCorner',faces=ZsupFaces,xVertices=merge(myxVertices))
    myxVertices=cornerX0Y0Z0,cornerX0Y0Zc,cornerX0YbZc,cornerX0YbZ0,XinfVertToExclude
    setXinfNoCornerAssembly = myAssembly.Set(name='xinfNoCorner',faces=XinfFaces,xVertices=merge(myxVertices))
    myxVertices=cornerX0Y0Z0,cornerX0Y0Zc,cornerXaY0Z0,cornerXaY0Zc,YinfVertToExclude
    setYinfNoCornerAssembly = myAssembly.Set(name='yinfNoCorner',faces=YinfFaces,xVertices=merge(myxVertices))
    myxVertices=cornerX0Y0Z0,cornerX0YbZ0,cornerXaY0Z0,cornerXaYbZ0,ZinfVertToExclude
    setZinfNoCornerAssembly = myAssembly.Set(name='zinfNoCorner',faces=ZinfFaces,xVertices=merge(myxVertices))
    myXVertices = cornerXaY0Z0,cornerX0Y0Z0,XsupVertToExclude,YsupVertToExclude,ZsupVertToExclude,XinfVertToExclude,YinfVertToExclude,ZinfVertToExclude
    setXparEdge1 = myAssembly.Set(name='xparEdge1',edges=z0y0Edges,xVertices=merge(myXVertices))
    myXVertices = cornerXaY0Zc,cornerX0Y0Zc,XsupVertToExclude,YsupVertToExclude,ZsupVertToExclude,XinfVertToExclude,YinfVertToExclude,ZinfVertToExclude
    setXparEdge2 = myAssembly.Set(name='xparEdge2',edges=zcy0Edges,xVertices=merge(myXVertices))
    myXVertices = cornerXaYbZc,cornerX0YbZc,XsupVertToExclude,YsupVertToExclude,ZsupVertToExclude,XinfVertToExclude,YinfVertToExclude,ZinfVertToExclude
    setXparEdge3 = myAssembly.Set(name='xparEdge3',edges=zcybEdges,xVertices=merge(myXVertices))
    myXVertices = cornerXaYbZ0,cornerX0YbZ0,XsupVertToExclude,YsupVertToExclude,ZsupVertToExclude,XinfVertToExclude,YinfVertToExclude,ZinfVertToExclude
    setXparEdge4 = myAssembly.Set(name='xparEdge4',edges=z0ybEdges,xVertices=merge(myXVertices))
    myXVertices = cornerXaY0Z0,cornerXaYbZ0,XsupVertToExclude,YsupVertToExclude,ZsupVertToExclude,XinfVertToExclude,YinfVertToExclude,ZinfVertToExclude
    setYparEdge1 = myAssembly.Set(name='yparEdge1',edges=xaz0Edges,xVertices=merge(myXVertices))
    myXVertices = cornerX0Y0Z0,cornerX0YbZ0,XsupVertToExclude,YsupVertToExclude,ZsupVertToExclude,XinfVertToExclude,YinfVertToExclude,ZinfVertToExclude
    setYparEdge2 = myAssembly.Set(name='yparEdge2',edges=x0z0Edges,xVertices=merge(myXVertices))
    myXVertices = cornerX0Y0Zc,cornerX0YbZc,XsupVertToExclude,YsupVertToExclude,ZsupVertToExclude,XinfVertToExclude,YinfVertToExclude,ZinfVertToExclude
    setYparEdge3 = myAssembly.Set(name='yparEdge3',edges=x0zcEdges,xVertices=merge(myXVertices))
    myXVertices = cornerXaY0Zc,cornerXaYbZc,XsupVertToExclude,YsupVertToExclude,ZsupVertToExclude,XinfVertToExclude,YinfVertToExclude,ZinfVertToExclude
    setYparEdge4 = myAssembly.Set(name='yparEdge4',edges=xazcEdges,xVertices=merge(myXVertices))
    myXVertices = cornerX0YbZ0,cornerX0YbZc,XsupVertToExclude,YsupVertToExclude,ZsupVertToExclude,XinfVertToExclude,YinfVertToExclude,ZinfVertToExclude
    setZparEdge1 = myAssembly.Set(name='zparEdge1',edges=x0ybEdges,xVertices=merge(myXVertices))
    myXVertices = cornerX0Y0Z0,cornerX0Y0Zc,XsupVertToExclude,YsupVertToExclude,ZsupVertToExclude,XinfVertToExclude,YinfVertToExclude,ZinfVertToExclude
    setZparEdge2 = myAssembly.Set(name='zparEdge2',edges=x0y0Edges,xVertices=merge(myXVertices))
    myXVertices = cornerXaY0Z0,cornerXaY0Zc,XsupVertToExclude,YsupVertToExclude,ZsupVertToExclude,XinfVertToExclude,YinfVertToExclude,ZinfVertToExclude
    setZparEdge3 = myAssembly.Set(name='zparEdge3',edges=xay0Edges,xVertices=merge(myXVertices))
    myXVertices = cornerXaYbZ0,cornerXaYbZc,XsupVertToExclude,YsupVertToExclude,ZsupVertToExclude,XinfVertToExclude,YinfVertToExclude,ZinfVertToExclude
    setZparEdge4 = myAssembly.Set(name='zparEdge4',edges=xaybEdges,xVertices=merge(myXVertices))
    for j in range(len(partNames['Phase2'])):
        tmpPart = myModel.parts[partNames['Phase2'][j]]
        tmpPart.setMeshControls(regions=tmpPart.cells,elemShape=TET,technique=FREE,sizeGrowth=MAXIMUM,allowMapped=TRUE)
        region = tmpPart.sets['Set'+partNames['Phase2'][j]]
        if(len(region.cells)==0 and len(region.edges)>0):
            tmpPart.setElementType(regions=(region.edges, ),elemTypes = [mesh.ElemType(elemCode=B31)])
        else:
            try:
                myModel.materials['CF'].hyperelastic
                tmpPart.setElementType(regions=(region.cells, ),elemTypes = [mesh.ElemType(elemCode=C3D10MH)])
            except (AttributeError):
                tmpPart.setElementType(regions=(region.cells, ),elemTypes = [mesh.ElemType(elemCode=C3D10M)])
    tmpPart = myModel.parts['matrixCut']
    tmpPart.setMeshControls(regions=tmpPart.cells,elemShape=TET,technique=FREE,sizeGrowth=MAXIMUM,allowMapped=TRUE)
    deviationFactor=0.07
    minSizeFactor=0.1
    remeshFlag = NO
    for j in range(len(partNames['Phase2'])):
        tmpPart = myModel.parts[partNames['Phase2'][j]]
        tmpPart.seedPart(size=0.05,deviationFactor=deviationFactor, minSizeFactor=minSizeFactor)
    tmpPart = myModel.parts['matrixCut']
    tmpPart.seedPart(size=0.05,deviationFactor=deviationFactor, minSizeFactor=minSizeFactor)
    rangeMax = len(partNames['Phase2'])
    for j in range(rangeMax):
        tmpPart = myModel.parts[partNames['Phase2'][j]]
        unmeshedCells = tmpPart.cells
        failedCells = tmpPart.cells
        nbMeshingAttempts = 0
        nbTotalWarningElem = 0
        totalVol = sizeCube[0]*sizeCube[1]*sizeCube[2]
        maxNbAttempts = 5
        while ((len(unmeshedCells)>0 or len(failedCells)>0) and nbMeshingAttempts<=maxNbAttempts+1):
            if(nbMeshingAttempts==maxNbAttempts):
                message = 'Some regions could still not be meshed after '+str(nbMeshingAttempts)+' attempts.  Do you want to keep trying with local refinement?'
                continueFlag = getWarningReply(message,(YES,NO))
                if(continueFlag==NO):
                    break
                elif(continueFlag==YES):
                    maxNbAttempts=maxNbAttempts+1
            if(nbMeshingAttempts==1 and remeshFlag==NO):
                remeshFlag = getWarningReply('Some regions could not be meshed or contain failed elements.  Do you want to try automatic mesh refinement in these regions?',(YES,NO))
                if(remeshFlag==NO):
                    break
            nbMeshingAttempts = nbMeshingAttempts + 1
            unmeshedCells=[]
            failedCells=[]
            numberFailedElem=[]
            numberWarningElem=[]
            tmpPart.generateMesh(seedConstraintOverride=ON)
            for tmpCell in tmpPart.cells:
                meshQuality = tmpPart.verifyMeshQuality(criterion=ANALYSIS_CHECKS,elemShape=TET,regions=(tmpCell,))
                if(meshQuality['numElements']==0):
                    unmeshedCells.append(tmpCell)
                if(len(meshQuality['failedElements'])>0):
                    failedCells.append(tmpCell)
                    numberFailedElem.append(len(meshQuality['failedElements']))
                if(len(meshQuality['warningElements'])>0):
                    numberWarningElem.append(len(meshQuality['warningElements']))
            if(len(unmeshedCells)>0):
                print str(len(unmeshedCells)) + ' cells failed to mesh\n'
                print 'Starting local seed size reduction in these cells...\n'
                for cellToReseed in unmeshedCells:
                    if(cellToReseed.getSize() > 0.4*totalVol and len(unmeshedCells)>1):
                        continue
                    else:
                        indexOfEdgesToReseed = cellToReseed.getEdges()
                        edgesToReseed = []
                        for index in indexOfEdgesToReseed:
                            edgesToReseed.append(tmpPart.edges[index])
                        tmpPart.seedEdgeBySize(size=0.05/((nbMeshingAttempts)*2.0),edges=edgesToReseed)
            elif(len(failedCells)>0):
                print str(len(failedCells)) + ' cells have elements that do not pass analysis checks\n'
                for i in range(len(failedCells)):
                    print 'Cell '+str(i)+': '+str(numberFailedElem[i])+' elements with errors\n'
                print 'Starting local seed size reduction in these cells...\n'
                for cellToReseed in failedCells:
                    if(cellToReseed.getSize() > 0.16*totalVol):
                        if(len(unmeshedCells)>1):
                            continue
                    else:
                        indexOfEdgesToReseed = cellToReseed.getEdges()
                        edgesToReseed = []
                        for index in indexOfEdgesToReseed:
                            edgesToReseed.append(tmpPart.edges[index])
                        tmpPart.seedEdgeBySize(size=0.05/((nbMeshingAttempts)*2.0),edges=edgesToReseed)
            else:
                for i in range(len(numberWarningElem)):
                    nbTotalWarningElem = nbTotalWarningElem+numberWarningElem[i]
    rangeMax = 1
    for j in range(rangeMax):
        tmpPart = myModel.parts['matrixCut']
        unmeshedCells = tmpPart.cells
        failedCells = tmpPart.cells
        nbMeshingAttempts = 0
        nbTotalWarningElem = 0
        totalVol = sizeCube[0]*sizeCube[1]*sizeCube[2]
        maxNbAttempts = 5
        while ((len(unmeshedCells)>0 or len(failedCells)>0) and nbMeshingAttempts<=maxNbAttempts+1):
            if(nbMeshingAttempts==maxNbAttempts):
                message = 'Some regions could still not be meshed after '+str(nbMeshingAttempts)+' attempts.  Do you want to keep trying with local refinement?'
                continueFlag = getWarningReply(message,(YES,NO))
                if(continueFlag==NO):
                    break
                elif(continueFlag==YES):
                    maxNbAttempts=maxNbAttempts+1
            if(nbMeshingAttempts==1 and remeshFlag==NO):
                remeshFlag = getWarningReply('Some regions could not be meshed or contain failed elements.  Do you want to try automatic mesh refinement in these regions?',(YES,NO))
                if(remeshFlag==NO):
                    break
            nbMeshingAttempts = nbMeshingAttempts + 1
            unmeshedCells=[]
            failedCells=[]
            numberFailedElem=[]
            numberWarningElem=[]
            tmpPart.generateMesh(seedConstraintOverride=ON)
            for tmpCell in tmpPart.cells:
                meshQuality = tmpPart.verifyMeshQuality(criterion=ANALYSIS_CHECKS,elemShape=TET,regions=(tmpCell,))
                if(meshQuality['numElements']==0):
                    unmeshedCells.append(tmpCell)
                if(len(meshQuality['failedElements'])>0):
                    failedCells.append(tmpCell)
                    numberFailedElem.append(len(meshQuality['failedElements']))
                if(len(meshQuality['warningElements'])>0):
                    numberWarningElem.append(len(meshQuality['warningElements']))
            if(len(unmeshedCells)>0):
                print str(len(unmeshedCells)) + ' cells failed to mesh\n'
                print 'Starting local seed size reduction in these cells...\n'
                for cellToReseed in unmeshedCells:
                    if(cellToReseed.getSize() > 0.4*totalVol and len(unmeshedCells)>1):
                        continue
                    else:
                        indexOfEdgesToReseed = cellToReseed.getEdges()
                        edgesToReseed = []
                        for index in indexOfEdgesToReseed:
                            edgesToReseed.append(tmpPart.edges[index])
                        tmpPart.seedEdgeBySize(size=0.05/((nbMeshingAttempts)*2.0),edges=edgesToReseed)
            elif(len(failedCells)>0):
                print str(len(failedCells)) + ' cells have elements that do not pass analysis checks\n'
                for i in range(len(failedCells)):
                    print 'Cell '+str(i)+': '+str(numberFailedElem[i])+' elements with errors\n'
                print 'Starting local seed size reduction in these cells...\n'
                for cellToReseed in failedCells:
                    if(cellToReseed.getSize() > 0.16*totalVol):
                        if(len(unmeshedCells)>1):
                            continue
                    else:
                        indexOfEdgesToReseed = cellToReseed.getEdges()
                        edgesToReseed = []
                        for index in indexOfEdgesToReseed:
                            edgesToReseed.append(tmpPart.edges[index])
                        tmpPart.seedEdgeBySize(size=0.05/((nbMeshingAttempts)*2.0),edges=edgesToReseed)
            else:
                for i in range(len(numberWarningElem)):
                    nbTotalWarningElem = nbTotalWarningElem+numberWarningElem[i]
    myModel.StaticStep(name='Step-1', previous='Initial', nlgeom=OFF, initialInc=1, minInc=0.1, maxInc=1, timePeriod=1, maxNumInc=2)
    myModel.fieldOutputRequests['F-Output-1'].setValues(variables=('S','U','RF','EVOL','IVOL','E'),frequency=1)
    refpoint4 = myAssembly.ReferencePoint(point=(1.1*sizeCube[0],0.5*sizeCube[1],0.5*sizeCube[2]))
    refpoint5 = myAssembly.ReferencePoint(point=(0.5*sizeCube[0],1.1*sizeCube[1],0.5*sizeCube[2]))
    refpoint6 = myAssembly.ReferencePoint(point=(0.5*sizeCube[0],0.5*sizeCube[1],1.1*sizeCube[2]))
    myAssembly.Set(name='refpoint4',referencePoints=(myAssembly.referencePoints[refpoint4.id],))
    myAssembly.Set(name='refpoint5',referencePoints=(myAssembly.referencePoints[refpoint5.id],))
    myAssembly.Set(name='refpoint6',referencePoints=(myAssembly.referencePoints[refpoint6.id],))
    myModel.DisplacementBC(name='BC-1',createStepName='Initial',region=myAssembly.sets['point1'], u1=SET, u2=SET, u3=SET, ur1=SET, ur2=SET, ur3=SET, distributionType=UNIFORM, fieldName='',localCsys=None)
    myModel.Equation(name='Eq1',terms=((1.0,'point2',1),(-1.0,'point3',1),(1.0,'refpoint5',1)))
    myModel.Equation(name='Eq2',terms=((1.0,'point3',1),(-1.0,'point4',1),(-1.0,'refpoint6',1)))
    myModel.Equation(name='Eq3',terms=((1.0,'point4',1),(-1.0,'point8',1),(1.0,'refpoint4',1)))
    myModel.Equation(name='Eq4',terms=((1.0,'point8',1),(-1.0,'point5',1),(-1.0,'refpoint5',1)))
    myModel.Equation(name='Eq5',terms=((1.0,'point5',1),(-1.0,'point6',1),(1.0,'refpoint6',1)))
    myModel.Equation(name='Eq6',terms=((1.0,'point6',1),(-1.0,'point7',1),(1.0,'refpoint5',1)))
    myModel.Equation(name='Eq7',terms=((1.0,'point7',1),(-1.0,'point1',1),(-1.0,'refpoint4',1),(-1.0,'refpoint5',1),(-1.0,'refpoint6',1)))
    myModel.Equation(name='Eq8',terms=((1.0,'point2',2),(-1.0,'point3',2),(1.0,'refpoint5',2)))
    myModel.Equation(name='Eq9',terms=((1.0,'point3',2),(-1.0,'point4',2),(-1.0,'refpoint6',2)))
    myModel.Equation(name='Eq10',terms=((1.0,'point4',2),(-1.0,'point8',2),(1.0,'refpoint4',2)))
    myModel.Equation(name='Eq11',terms=((1.0,'point8',2),(-1.0,'point5',2),(-1.0,'refpoint5',2)))
    myModel.Equation(name='Eq12',terms=((1.0,'point5',2),(-1.0,'point6',2),(1.0,'refpoint6',2)))
    myModel.Equation(name='Eq13',terms=((1.0,'point6',2),(-1.0,'point7',2),(1.0,'refpoint5',2)))
    myModel.Equation(name='Eq14',terms=((1.0,'point7',2),(-1.0,'point1',2),(-1.0,'refpoint4',2),(-1.0,'refpoint5',2),(-1.0,'refpoint6',2)))
    myModel.Equation(name='Eq15',terms=((1.0,'point2',3),(-1.0,'point3',3),(1.0,'refpoint5',3)))
    myModel.Equation(name='Eq16',terms=((1.0,'point3',3),(-1.0,'point4',3),(-1.0,'refpoint6',3)))
    myModel.Equation(name='Eq17',terms=((1.0,'point4',3),(-1.0,'point8',3),(1.0,'refpoint4',3)))
    myModel.Equation(name='Eq18',terms=((1.0,'point8',3),(-1.0,'point5',3),(-1.0,'refpoint5',3)))
    myModel.Equation(name='Eq19',terms=((1.0,'point5',3),(-1.0,'point6',3),(1.0,'refpoint6',3)))
    myModel.Equation(name='Eq20',terms=((1.0,'point6',3),(-1.0,'point7',3),(1.0,'refpoint5',3)))
    myModel.Equation(name='Eq21',terms=((1.0,'point7',3),(-1.0,'point1',3),(-1.0,'refpoint4',3),(-1.0,'refpoint5',3),(-1.0,'refpoint6',3)))
    a = sizeCube[0]
    b = sizeCube[1]
    c = sizeCube[2]
    myModel.DisplacementBC(name='BC-3',createStepName='Step-1',region=myAssembly.sets['refpoint4'], amplitude=UNSET, u2=0, distributionType=UNIFORM, fieldName='',localCsys=None)
    myModel.DisplacementBC(name='BC-7',createStepName='Step-1',region=myAssembly.sets['refpoint5'], amplitude=UNSET, u3=0, distributionType=UNIFORM, fieldName='',localCsys=None)
    myModel.DisplacementBC(name='BC-8',createStepName='Step-1',region=myAssembly.sets['refpoint6'], amplitude=UNSET, u1=0, distributionType=UNIFORM, fieldName='',localCsys=None)
    myModel.DisplacementBC(name='BC-9',createStepName='Step-1',region=myAssembly.sets['refpoint6'], u2=c*0.03, distributionType=UNIFORM, fieldName='',localCsys=None)
    mdb.Job(name='Job_Analysis_sh_23',model='Analysis_sh_23',type=ANALYSIS, explicitPrecision=SINGLE,nodalOutputPrecision=SINGLE,description='',parallelizationMethodExplicit=DOMAIN,multiprocessingMode=DEFAULT,numDomains=1, userSubroutine='',numCpus=1,scratch='',echoPrint=OFF, modelPrint=OFF,contactPrint=OFF, historyPrint=OFF)
    xMid = sizeCube[0]/2
    yMid = sizeCube[1]/2
    zMid = sizeCube[2]/2
    myModel.setValues(noPartsInputFile=ON)
    myModel.keywordBlock.synchVersions(storeNodesAndElements=False)
    index=0
    for i in range(len(myModel.keywordBlock.sieBlocks)):
        tempoIndex = myModel.keywordBlock.sieBlocks[i].find('** MATERIALS')
        if(tempoIndex!=-1):
            index = i-2
            break    
    nbNodes = 0
    for name in partNames['Phase2']:
        nbNodes = nbNodes+len(myModel.parts[name].nodes)
    nbNodes = nbNodes+len(myModel.parts['matrixCut'].nodes)
    if(nbNodes==0):
        nbNodes=10000000
    else:
        nbNodes=nbNodes+100
    index = index-1
    index = index+1
    myModel.keywordBlock.insert(index,    '*ncopy, change number = '+str(nbNodes)+', old set=xsupNoEdges, new set=xsupCopy, reflect=mirror\n'+str(xMid)+', 0, 0, '+str(xMid)+', '+str(sizeCube[1])+', 0\n'+str(xMid)+', 0, '+str(sizeCube[2])+' ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*ncopy, change number = '+str(2*nbNodes)+', old set=ysupNoEdges, new set=ysupCopy, reflect=mirror\n0, '+str(yMid)+', 0, '+str(sizeCube[0])+', '+str(yMid)+', 0\n0, '+str(yMid)+', '+str(sizeCube[2])+' ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*ncopy, change number = '+str(3*nbNodes)+', old set=zsupNoEdges, new set=zsupCopy, reflect=mirror\n0, 0, '+str(zMid)+', '+str(sizeCube[0])+', 0, '+str(zMid)+'\n0, '+str(sizeCube[1])+', '+str(zMid)+' ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*ncopy, change number = '+str(4*nbNodes)+', old set=yparEdge1, new set=yparEdge1CopyTo2, reflect=mirror\n'+str(xMid)+', 0, 0, '+str(xMid)+', '+str(sizeCube[1])+', 0\n'+str(xMid)+', 0, '+str(sizeCube[2])+'')
    index = index+1
    myModel.keywordBlock.insert(index,    '*ncopy, change number = '+str(5*nbNodes)+', old set=yparEdge4, new set=yparEdge4CopyTo3, reflect=mirror\n'+str(xMid)+', 0, 0, '+str(xMid)+', '+str(sizeCube[1])+', 0\n'+str(xMid)+', 0, '+str(sizeCube[2])+'')
    index = index+1
    myModel.keywordBlock.insert(index,    '*ncopy, change number = '+str(6*nbNodes)+', old set=zparEdge3, new set=zparEdge3CopyTo2, reflect=mirror\n'+str(xMid)+', 0, 0, '+str(xMid)+', '+str(sizeCube[1])+', 0\n'+str(xMid)+', 0, '+str(sizeCube[2])+'')
    index = index+1
    myModel.keywordBlock.insert(index,    '*ncopy, change number = '+str(7*nbNodes)+', old set=zparEdge4, new set=zparEdge4CopyTo1, reflect=mirror\n'+str(xMid)+', 0, 0, '+str(xMid)+', '+str(sizeCube[1])+', 0\n'+str(xMid)+', 0, '+str(sizeCube[2])+'')
    index = index+1
    myModel.keywordBlock.insert(index,    '*ncopy, change number = '+str(8*nbNodes)+', old set=xparEdge3, new set=xparEdge3CopyTo2, reflect=mirror\n0, '+str(yMid)+', 0, '+str(sizeCube[0])+', '+str(yMid)+', 0\n0, '+str(yMid)+', '+str(sizeCube[2])+' ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*ncopy, change number = '+str(9*nbNodes)+', old set=xparEdge4, new set=xparEdge4CopyTo1, reflect=mirror\n0, '+str(yMid)+', 0, '+str(sizeCube[0])+', '+str(yMid)+', 0\n0, '+str(yMid)+', '+str(sizeCube[2])+'')
    index = index+1
    myModel.keywordBlock.insert(index,    '*ncopy, change number = '+str(10*nbNodes)+', old set=zparEdge1, new set=zparEdge1CopyTo2, reflect=mirror\n0, '+str(yMid)+', 0, '+str(sizeCube[0])+', '+str(yMid)+', 0\n0, '+str(yMid)+', '+str(sizeCube[2])+'')
    index = index+1
    myModel.keywordBlock.insert(index,    '*ncopy, change number = '+str(11*nbNodes)+', old set=zparEdge4, new set=zparEdge4CopyTo3, reflect=mirror\n0, '+str(yMid)+', 0, '+str(sizeCube[0])+', '+str(yMid)+', 0\n0, '+str(yMid)+', '+str(sizeCube[2])+'')
    index = index+1
    myModel.keywordBlock.insert(index,    '*ncopy, change number = '+str(12*nbNodes)+', old set=yparEdge3, new set=yparEdge3CopyTo2, reflect=mirror\n0, 0, '+str(zMid)+', '+str(sizeCube[0])+', 0, '+str(zMid)+'\n0, '+str(sizeCube[1])+', '+str(zMid)+' ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*ncopy, change number = '+str(13*nbNodes)+', old set=yparEdge4, new set=yparEdge4CopyTo1, reflect=mirror\n0, 0, '+str(zMid)+', '+str(sizeCube[0])+', 0, '+str(zMid)+'\n0, '+str(sizeCube[1])+', '+str(zMid)+' ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*ncopy, change number = '+str(14*nbNodes)+', old set=xparEdge2, new set=xparEdge2CopyTo1, reflect=mirror\n0, 0, '+str(zMid)+', '+str(sizeCube[0])+', 0, '+str(zMid)+'\n0, '+str(sizeCube[1])+', '+str(zMid)+' ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*ncopy, change number = '+str(15*nbNodes)+', old set=xparEdge4, new set=xparEdge4CopyTo3, reflect=mirror\n0, 0, '+str(zMid)+', '+str(sizeCube[0])+', 0, '+str(zMid)+'\n0, '+str(sizeCube[1])+', '+str(zMid)+' ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*surface, name=copySurfXinf, type=node\nxsupCopy  ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*surface, name=surfXinf, type=node\nxinfNoEdges  ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*surface, name=copySurfYinf, type=node\nysupCopy  ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*surface, name=surfYinf, type=node\nyinfNoEdges  ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*surface, name=copySurfZinf, type=node\nzsupCopy  ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*surface, name=surfZinf, type=node\nzinfNoEdges  ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*surface, name=surfxparEdge1, type=node\nxparEdge1  ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*surface, name=surfxparEdge2, type=node\nxparEdge2  ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*surface, name=surfxparEdge3, type=node\nxparEdge3  ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*surface, name=surfxparEdge4, type=node\nxparEdge4  ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*surface, name=surfxparEdge3CopyTo2, type=node\nxparEdge3CopyTo2  ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*surface, name=surfxparEdge4CopyTo1, type=node\nxparEdge4CopyTo1  ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*surface, name=surfxparEdge2CopyTo1, type=node\nxparEdge2CopyTo1  ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*surface, name=surfxparEdge4CopyTo3, type=node\nxparEdge4CopyTo3  ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*surface, name=surfyparEdge1, type=node\nyparEdge1  ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*surface, name=surfyparEdge2, type=node\nyparEdge2  ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*surface, name=surfyparEdge3, type=node\nyparEdge3  ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*surface, name=surfyparEdge4, type=node\nyparEdge4  ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*surface, name=surfyparEdge1CopyTo2, type=node\nyparEdge1CopyTo2  ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*surface, name=surfyparEdge4CopyTo3, type=node\nyparEdge4CopyTo3  ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*surface, name=surfyparEdge3CopyTo2, type=node\nyparEdge3CopyTo2  ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*surface, name=surfyparEdge4CopyTo1, type=node\nyparEdge4CopyTo1  ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*surface, name=surfzparEdge1, type=node\nzparEdge1  ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*surface, name=surfzparEdge2, type=node\nzparEdge2  ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*surface, name=surfzparEdge3, type=node\nzparEdge3  ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*surface, name=surfzparEdge4, type=node\nzparEdge4  ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*surface, name=surfzparEdge3CopyTo2, type=node\nzparEdge3CopyTo2  ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*surface, name=surfzparEdge4CopyTo1, type=node\nzparEdge4CopyTo1  ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*surface, name=surfzparEdge1CopyTo2, type=node\nzparEdge1CopyTo2  ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*surface, name=surfzparEdge4CopyTo3, type=node\nzparEdge4CopyTo3  ')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Tie, name=Tie-X, tied nset=xsupCopy, adjust=no, type=SURFACE TO SURFACE\ncopySurfXinf,surfXinf')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Tie, name=Tie-Y, tied nset=ysupCopy, adjust=no, type=SURFACE TO SURFACE\ncopySurfYinf,surfYinf')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Tie, name=Tie-Z, tied nset=zsupCopy, adjust=no, type=SURFACE TO SURFACE\ncopySurfZinf,surfZinf')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Tie, name=TieX1, tied nset=xparEdge3CopyTo2, adjust=no, type=SURFACE TO SURFACE\nsurfxparEdge3CopyTo2, surfxparEdge2')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Tie, name=TieX2, tied nset=xparEdge4CopyTo1, adjust=no, type=SURFACE TO SURFACE\nsurfxparEdge4CopyTo1, surfxparEdge1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Tie, name=TieX3, tied nset=xparEdge2CopyTo1, adjust=no, type=SURFACE TO SURFACE\nsurfxparEdge2CopyTo1, surfxparEdge1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Tie, name=TieX4, tied nset=xparEdge4CopyTo3, adjust=no, type=SURFACE TO SURFACE\nsurfxparEdge4CopyTo3, surfxparEdge3')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Tie, name=TieY1, tied nset=yparEdge1CopyTo2, adjust=no, type=SURFACE TO SURFACE\nsurfyparEdge1CopyTo2, surfyparEdge2')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Tie, name=TieY2, tied nset=yparEdge4CopyTo3, adjust=no, type=SURFACE TO SURFACE\nsurfyparEdge4CopyTo3, surfyparEdge3')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Tie, name=TieY3, tied nset=yparEdge3CopyTo2, adjust=no, type=SURFACE TO SURFACE\nsurfyparEdge3CopyTo2, surfyparEdge2')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Tie, name=TieY4, tied nset=yparEdge4CopyTo1, adjust=no, type=SURFACE TO SURFACE\nsurfyparEdge4CopyTo1, surfyparEdge1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Tie, name=TieZ1, tied nset=zparEdge3CopyTo2, adjust=no, type=SURFACE TO SURFACE\nsurfzparEdge3CopyTo2, surfzparEdge2')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Tie, name=TieZ2, tied nset=zparEdge4CopyTo1, adjust=no, type=SURFACE TO SURFACE\nsurfzparEdge4CopyTo1, surfzparEdge1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Tie, name=TieZ3, tied nset=zparEdge1CopyTo2, adjust=no, type=SURFACE TO SURFACE\nsurfzparEdge1CopyTo2, surfzparEdge2')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Tie, name=TieZ4, tied nset=zparEdge4CopyTo3, adjust=no, type=SURFACE TO SURFACE\nsurfzparEdge4CopyTo3, surfzparEdge3')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nxsupNoEdges, 1, 1\nxsupCopy,1, -1\nrefpoint4, 1, -1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nysupNoEdges, 1, 1\nysupCopy,1, -1\nrefpoint5, 1, -1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nzsupNoEdges, 1, 1\nzsupCopy,1, -1\nrefpoint6, 1, -1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nxsupNoEdges, 2, 1\nxsupCopy,2, -1\nrefpoint4, 2, -1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nysupNoEdges, 2, 1\nysupCopy,2, -1\nrefpoint5, 2, -1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nzsupNoEdges, 2, 1\nzsupCopy,2, -1\nrefpoint6, 2, -1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nxsupNoEdges, 3, 1\nxsupCopy,3, -1\nrefpoint4, 3, -1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nysupNoEdges, 3, 1\nysupCopy,3, -1\nrefpoint5, 3, -1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nzsupNoEdges, 3, 1\nzsupCopy,3, -1\nrefpoint6, 3, -1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nxparEdge2, 1, 1\nxparEdge2CopyTo1,1, -1\nrefpoint6, 1, -1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nxparEdge3, 1, 1\nxparEdge3CopyTo2,1, -1\nrefpoint5, 1, -1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nxparEdge4, 1, 1\nxparEdge4CopyTo3,1, -1\nrefpoint6, 1, 1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nxparEdge2, 2, 1\nxparEdge2CopyTo1,2, -1\nrefpoint6, 2, -1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nxparEdge3, 2, 1\nxparEdge3CopyTo2,2, -1\nrefpoint5, 2, -1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nxparEdge4, 2, 1\nxparEdge4CopyTo3,2, -1\nrefpoint6, 2, 1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nxparEdge2, 3, 1\nxparEdge2CopyTo1,3, -1\nrefpoint6, 3, -1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nxparEdge3, 3, 1\nxparEdge3CopyTo2,3, -1\nrefpoint5, 3, -1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nxparEdge4, 3, 1\nxparEdge4CopyTo3,3, -1\nrefpoint6, 3, 1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nyparEdge1, 1, 1\nyparEdge1CopyTo2,1, -1\nrefpoint4, 1, -1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nyparEdge3, 1, 1\nyparEdge3CopyTo2,1, -1\nrefpoint6, 1, -1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nyparEdge4, 1, 1\nyparEdge4CopyTo3,1, -1\nrefpoint4, 1, -1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nyparEdge1, 2, 1\nyparEdge1CopyTo2,2, -1\nrefpoint4, 2, -1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nyparEdge3, 2, 1\nyparEdge3CopyTo2,2, -1\nrefpoint6, 2, -1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nyparEdge4, 2, 1\nyparEdge4CopyTo3,2, -1\nrefpoint4, 2, -1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nyparEdge1, 3, 1\nyparEdge1CopyTo2,3, -1\nrefpoint4, 3, -1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nyparEdge3, 3, 1\nyparEdge3CopyTo2,3, -1\nrefpoint6, 3, -1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nyparEdge4, 3, 1\nyparEdge4CopyTo3,3, -1\nrefpoint4, 3, -1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nzparEdge1, 1, 1\nzparEdge1CopyTo2,1, -1\nrefpoint5, 1, -1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nzparEdge3, 1, 1\nzparEdge3CopyTo2,1, -1\nrefpoint4, 1, -1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nzparEdge4, 1, 1\nzparEdge4CopyTo3,1, -1\nrefpoint5, 1, -1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nzparEdge1, 2, 1\nzparEdge1CopyTo2,2, -1\nrefpoint5, 2, -1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nzparEdge3, 2, 1\nzparEdge3CopyTo2,2, -1\nrefpoint4, 2, -1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nzparEdge4, 2, 1\nzparEdge4CopyTo3,2, -1\nrefpoint5, 2, -1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nzparEdge1, 3, 1\nzparEdge1CopyTo2,3, -1\nrefpoint5, 3, -1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nzparEdge3, 3, 1\nzparEdge3CopyTo2,3, -1\nrefpoint4, 3, -1')
    index = index+1
    myModel.keywordBlock.insert(index,    '*Equation\n3\nzparEdge4, 3, 1\nzparEdge4CopyTo3,3, -1\nrefpoint5, 3, -1')
    mdb.jobs['Job_Analysis_sh_23'].writeInput(consistencyChecking=OFF)
    mdb.saveAs(pyPath+'/Analysis_sh_23.cae')
    print '********************'
    print '*Meshing parameters*'
    print '********************'
    print 'Element shape: Quadratic tetrahedron (C3D10M)\n'
    print 'Element size growth: Moderate\n'
    print 'Use mapped tri meshing on bounding faces\n'
    print 'Initial seed size: '+str(5.000000000000e-002)+'\n'
    if(nbMeshingAttempts>1):
        print 'Number of local seed refinement steps:'+str(nbMeshingAttempts)+'\n'
        print 'Smallest seed size: '+str(5.000000000000e-002/((nbMeshingAttempts)*2))+'\n'
    print 'Mesh quality indicators:\n'
    print 'Number of elements with analysis warnings: '+str(nbTotalWarningElem)+'\n'
    session.viewports['Viewport: 1'].setValues(displayedObject=myAssembly)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=ON)
    del mdb.models['Model-1']


if __name__=='__main__':
    main()
