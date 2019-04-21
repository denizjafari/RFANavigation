import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import pdb
import time
import math
import numpy as np

np.seterr(divide='ignore', invalid='ignore')


#
# TreatmentPlanReader
#

class LoadData(ScriptedLoadableModule):
  """This module reads the RFA treatment plan
   to be developed by Grace
   The inputs are pre-operative CT, 
   The tumour volume based on FEM
   Prescribed probe possitions and the location of needle
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "LoadData" # TODO make this more human readable by adding spaces
    self.parent.categories = ["RFANav"]
    self.parent.dependencies = []
    self.parent.contributors = ["Deniz J (SRI)"]
    self.parent.helpText = """
Spinal Metastases RFA procedure navigation workflow - MHSc Thesis
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
"""

#
# TreatmentPlanReaderWidget
#

class LoadDataWidget(ScriptedLoadableModuleWidget):

  def setup(self):

    self.developerMode = True

    ScriptedLoadableModuleWidget.setup(self)
    self.logic = LoadDataLogic()
    self.intraopVolCounter = 0
    self.intraopVolComing = False
    
    
    self.targetPose1AddedFlag = False
    self.entryPose1AddedFlag = False
    
    self.targetPose2AddedFlag = False
    self.entryPose2AddedFlag = False
    
     
    # initialize global variables
    self.identity = vtk.vtkMatrix4x4()
    
    self.probe1Model = None
    self.probe1path = None    
    self.probe1PathTransform = None
  
    self.probe2Model = None
    self.probe2path = None     
    self.probe2PathTransform = None

    
    
    
    self.selectionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSelectionNodeSingleton")
   
    #
    # Load DICOM data
    #
    self.dicomGroupBox = ctk.ctkCollapsibleGroupBox()
    self.dicomGroupBox.title = "Load DICOM"
    self.dicomGroupBox.collapsed = True
    self.layout.addWidget(self.dicomGroupBox)
    dicomGroupBoxFromLayout = qt.QFormLayout(self.dicomGroupBox) 
    dicommodule = slicer.modules.dicom.createNewWidgetRepresentation()
    dicomchildren = dicommodule.children()
    dicomchildren[1].collapsed = True
    dicomchildren[3].hide()
    dicomGroupBoxFromLayout.addWidget(dicommodule)
    
    
    # Pre-op
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Pre-Op  Treatment Plan"
    self.layout.addWidget(parametersCollapsibleButton)
    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

 
    #
    # input pre-op CT (medical scan)
    #
    self.inputScanSelector = slicer.qMRMLNodeComboBox()
    self.inputScanSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.inputScanSelector.selectNodeUponCreation = True
    self.inputScanSelector.addEnabled = False
    self.inputScanSelector.removeEnabled = True
    self.inputScanSelector.renameEnabled = True
    self.inputScanSelector.noneEnabled = False
    self.inputScanSelector.showHidden = False
    self.inputScanSelector.showChildNodeTypes = False
    self.inputScanSelector.setMRMLScene( slicer.mrmlScene )
    self.inputScanSelector.setToolTip( "Pick the input pre-operative medical Scan" )
    parametersFormLayout.addRow("Pre-op Volume: ", self.inputScanSelector)
    # take care of change in preop medical scan
    self.inputScanSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onPreopVolumeChanged)

    #
    # input the segmentation (pre-op plan)
    #
    self.inputPlanSelector = slicer.qMRMLNodeComboBox()
    self.inputPlanSelector.nodeTypes = ["vtkMRMLLabelMapVolumeNode"]
    self.inputPlanSelector.selectNodeUponCreation = True
    self.inputPlanSelector.addEnabled = False
    self.inputPlanSelector.removeEnabled = True
    self.inputPlanSelector.renameEnabled = True
    self.inputPlanSelector.noneEnabled = False
    self.inputPlanSelector.showHidden = False
    self.inputPlanSelector.showChildNodeTypes = False
    self.inputPlanSelector.setMRMLScene(slicer.mrmlScene)
    self.inputPlanSelector.setToolTip("Input the segmentation")
    parametersFormLayout.addRow("Pre-op Segmentation: ", self.inputPlanSelector)  
    # take care of change of  preop treatment plan
    self.inputPlanSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onPreopSegmentationChanged)

    #
    # Generate Model Button
    #
    self.modelGenButton = qt.QPushButton("Generate 3D Model from Preop Plan")
    self.modelGenButton.toolTip = "generates a 3d triangulated surface model from the preop segmentation data"
    if self.inputPlanSelector.currentNode != None:
      self.modelGenButton.enabled = True
    else:
      self.modelGenButton.enabled = False
    parametersFormLayout.addRow(self.modelGenButton)
    self.modelGenButton.connect('clicked(bool)', self.onGenerateModel)  # connection

    #
    # input the Probe poses, the entry and the the tip points for probe 1 and 2
    #
    nText = qt.QLabel("Total Number of Probes: ")
    self.probes = qt.QComboBox()
    self.tprobes = ('1','2')
    self.probes.addItems(self.tprobes)
    parametersFormLayout.addRow(nText,self.probes)

    # implement if case for total number of entry and target points appearing based on number of probes
    self.probes.connect("activated(QString)", self.onProbeNum)

    # Probe 1
    self.entryPose1Selector = slicer.qMRMLNodeComboBox()
    self.entryPose1Selector.nodeTypes = ["vtkMRMLMarkupsFiducialNode"]
    self.entryPose1Selector.selectNodeUponCreation = True
    self.entryPose1Selector.addEnabled = True
    self.entryPose1Selector.removeEnabled = False
    self.entryPose1Selector.noneEnabled = False
    self.entryPose1Selector.showHidden = False
    self.entryPose1Selector.showChildNodeTypes = False
    self.entryPose1Selector.baseName = "Entry1"
    self.entryPose1Selector.setMRMLScene(slicer.mrmlScene)
    self.entryPose1Selector.setToolTip("Input probe 1 entry point")
    self.entryPose1Selector.connect("currentNodeChanged(vtkMRMLNode*)", self.onEntryPose1SelectorChanged)

    self.targetPose1Selector = slicer.qMRMLNodeComboBox()
    self.targetPose1Selector.nodeTypes = ["vtkMRMLMarkupsFiducialNode"]
    self.targetPose1Selector.selectNodeUponCreation = True
    self.targetPose1Selector.addEnabled = True
    self.targetPose1Selector.removeEnabled = False
    self.targetPose1Selector.noneEnabled = False
    self.targetPose1Selector.showHidden = False
    self.targetPose1Selector.showChildNodeTypes = False
    self.targetPose1Selector.baseName = "Target1"
    self.targetPose1Selector.setMRMLScene(slicer.mrmlScene)
    self.targetPose1Selector.setToolTip("Input probe 1 entry point")
    self.targetPose1Selector.connect("currentNodeChanged(vtkMRMLNode*)", self.onTargetPose1SelectorChanged)
    
    self.showProbe1ModelCheckBox = qt.QCheckBox()
    self.showProbe1ModelCheckBox.checked = 1
    self.showProbe1ModelCheckBox.setToolTip("If checked, the probe model is shown in the display")
    self.showProbe1ModelCheckBox.connect('stateChanged(int)', self.onProbeModelCheckBox)

    
    self.probe1Button = qt.QPushButton("Delete Probe 1 Poses")
    self.probe1Button.toolTip = "Deletes probe 1 entry and target poses."
    self.probe1Button.enabled = True
    self.probe1Button.connect('clicked(bool)', self.onDeleteProbe1Button)
    

    self.probe1GroupBox = ctk.ctkCollapsibleGroupBox()
    self.probe1GroupBox.title = "Probe 1"
    self.probe1GroupBox.collapsed = False
    parametersFormLayout.addRow(self.probe1GroupBox)
    probe1GroupBoxLayout = qt.QFormLayout(self.probe1GroupBox)
    probe1GroupBoxLayout.addRow("Input Probe 1 entry point: ", self.entryPose1Selector)
    probe1GroupBoxLayout.addRow("Input Probe 1 target point: ", self.targetPose1Selector)
    probe1GroupBoxLayout.addRow("Show Probe Model in the views", self.showProbe1ModelCheckBox)
    probe1GroupBoxLayout.addRow(self.probe1Button)
   
    # Probe 2
    self.entryPose2Selector = slicer.qMRMLNodeComboBox()
    self.entryPose2Selector.nodeTypes = ["vtkMRMLMarkupsFiducialNode"]
    self.entryPose2Selector.selectNodeUponCreation = True
    self.entryPose2Selector.addEnabled = True
    self.entryPose2Selector.removeEnabled = False
    self.entryPose2Selector.noneEnabled = False
    self.entryPose2Selector.showHidden = False
    self.entryPose2Selector.showChildNodeTypes = False
    self.entryPose2Selector.baseName = "Entry2"
    self.entryPose2Selector.setMRMLScene(slicer.mrmlScene)
    self.entryPose2Selector.setToolTip("Input probe 2 entry point")
    self.entryPose2Selector.connect("currentNodeChanged(vtkMRMLNode*)", self.onEntryPose2SelectorChanged)

    self.targetPose2Selector = slicer.qMRMLNodeComboBox()
    self.targetPose2Selector.nodeTypes = ["vtkMRMLMarkupsFiducialNode"]
    self.targetPose2Selector.selectNodeUponCreation = True
    self.targetPose2Selector.addEnabled = True
    self.targetPose2Selector.removeEnabled = False
    self.targetPose2Selector.noneEnabled = False
    self.targetPose2Selector.showHidden = False
    self.targetPose2Selector.showChildNodeTypes = False
    self.targetPose2Selector.baseName = "Target2"
    self.targetPose2Selector.setMRMLScene(slicer.mrmlScene)
    self.targetPose2Selector.setToolTip("Input probe 2 entry point")
    self.targetPose2Selector.connect("currentNodeChanged(vtkMRMLNode*)", self.onTargetPose2SelectorChanged)
    
    self.showProbe2ModelCheckBox = qt.QCheckBox()
    self.showProbe2ModelCheckBox.checked = 1
    self.showProbe2ModelCheckBox.setToolTip("If checked, the probe model is shown in the display")
    self.showProbe2ModelCheckBox.connect('stateChanged(int)', self.onProbeModelCheckBox)
    
    self.probe2Button = qt.QPushButton("Delete Probe 1 Poses")
    self.probe2Button.toolTip = "Deletes probe 1 entry and target poses."
    self.probe2Button.enabled = True
    self.probe2Button.connect('clicked(bool)', self.onDeleteProbe2Button)


    self.probe2GroupBox = ctk.ctkCollapsibleGroupBox()
    self.probe2GroupBox.title = "Probe 2"
    self.probe2GroupBox.collapsed = False
    parametersFormLayout.addRow(self.probe2GroupBox)
    probe2GroupBoxLayout = qt.QFormLayout(self.probe2GroupBox)  
    probe2GroupBoxLayout.addRow("Input Probe 2 entry point: ", self.entryPose2Selector)
    probe2GroupBoxLayout.addRow("Input Probe 2 target point: ", self.targetPose2Selector)
    probe2GroupBoxLayout.addRow("Show Probe Model in the views", self.showProbe2ModelCheckBox)
    probe2GroupBoxLayout.addRow(self.probe2Button)

    self.onProbeNum()   

    
  def onProbeModelCheckBox(self):
    if self.probe1Model != None:
      displayNode = self.probe1Model.GetDisplayNode()
      if self.showProbe1ModelCheckBox.checked == 1:
        displayNode.SetVisibility(1)
      else:
        displayNode.SetVisibility(0)
    if self.probe2Model != None:
      displayNode = self.probe2Model.GetDisplayNode()
      if self.showProbe2ModelCheckBox.checked == 1:
        displayNode.SetVisibility(1)
      else:
        displayNode.SetVisibility(0)
        

  def onProbeNum(self):
    self.probe2GroupBox.collapsed = True
    if not int(self.probes.currentText) % 2:
      self.probe2GroupBox.collapsed = False
        

    
  def AddProbe(self):
    rfaProbeModelPath = os.path.join(os.path.dirname(__file__), 'RFAProbe.ply')
    rfaProbeModel = slicer.modules.models.logic().AddModel(rfaProbeModelPath)
    probeDisplayNode = rfaProbeModel.GetDisplayNode()
    probeDisplayNode.SetColor(0,1,1)
    probeDisplayNode.SetSliceIntersectionVisibility(1)
    return rfaProbeModel
    
  def onAddProbe1(self):  
    
    if self.targetPose1AddedFlag == True and self.entryPose1AddedFlag == True:
      if self.probe1Model == None:
        self.probe1Model = self.AddProbe()  
        self.probe1Model.SetName('Probe1Model') 
      if self.probe1path == None:
        self.probe1path = self.logic.createTrajectoryModel()  
        self.probe1path.SetName('Probe1Path')
     
      self.probe1PathTransform.RemoveAllObservers()
      self.probe1Model.SetAndObserveTransformNodeID(self.probe1PathTransform.GetID())
      self.probe1path.SetAndObserveTransformNodeID(self.probe1PathTransform.GetID())
      self.targetPose1AddedFlag = False
      self.entryPose1AddedFlag = False
      
    else:
      pass
      
  def onAddProbe2(self):  
       
    if self.targetPose2AddedFlag == True and self.entryPose2AddedFlag == True:
      if self.probe2Model == None:
        self.probe2Model = self.AddProbe()  
        self.probe2Model.SetName('Probe2Model') 

      if self.probe2path == None:
        self.probe2path = self.logic.createTrajectoryModel()  
        self.probe2path.SetName('Probe2Path')      

      self.probe2PathTransform.RemoveAllObservers()
      self.probe2Model.SetAndObserveTransformNodeID(self.probe2PathTransform.GetID())
      self.probe2path.SetAndObserveTransformNodeID(self.probe2PathTransform.GetID())
      self.targetPose2AddedFlag = False
      self.entryPose2AddedFlag = False
      
    else:
      pass


  def onFiducialsModified1(self, observer, eventId):
    # matches which fiducial node to check against
    
    if self.probe1PathTransform == None:
      self.probe1PathTransform = slicer.vtkMRMLTransformNode()
      self.probe1PathTransform.SetName("Probe1PathTransform")
      slicer.mrmlScene.AddNode(self.probe1PathTransform)
      self.probe1PathTransform.SetMatrixTransformToParent(self.identity)
        
    if self.entryPose1Selector.currentNode() != None:
      display = self.entryPose1Selector.currentNode().GetDisplayNode()
      display.SetGlyphScale(1)
    if self.targetPose1Selector.currentNode() != None:         
      display = self.targetPose1Selector.currentNode().GetDisplayNode()
      display.SetGlyphScale(1) 
    
    if self.entryPose1Selector.currentNode() != None and self.targetPose1Selector.currentNode() != None:
      self.probe1PathTransform = self.logic.updateTransform( self.targetPose1Selector.currentNode(), self.entryPose1Selector.currentNode(), self.probe1PathTransform)

        
    else:
      pass
  
  def onFiducialsModified2(self, observer, eventId):
    # matches which fiducial node to check against
    
    if self.probe2PathTransform == None:
      self.probe2PathTransform = slicer.vtkMRMLTransformNode()
      self.probe2PathTransform.SetName("Probe2PathTransform")
      slicer.mrmlScene.AddNode(self.probe2PathTransform)
      self.probe2PathTransform.SetMatrixTransformToParent(self.identity)
      
    if self.entryPose2Selector.currentNode() != None:
      display = self.entryPose2Selector.currentNode().GetDisplayNode()
      display.SetGlyphScale(1)
    if self.targetPose2Selector.currentNode() != None:         
      display = self.targetPose2Selector.currentNode().GetDisplayNode()
      display.SetGlyphScale(1)
        
    if self.entryPose2Selector.currentNode() != None and self.targetPose2Selector.currentNode() != None:
      self.probe2PathTransform = self.logic.updateTransform( self.targetPose2Selector.currentNode(), self.entryPose2Selector.currentNode(), self.probe2PathTransform)
        
    else:
      pass

  def onGenerateModel(self):
    if self.inputPlanSelector.currentNode == None:
      return
    self.modelHNode = slicer.mrmlScene.CreateNodeByClass('vtkMRMLModelHierarchyNode')
    self.modelHNode.SetName('RFATreatmentPlanModel')
    self.modelHNode = slicer.mrmlScene.AddNode(self.modelHNode)
    self.logic.volumeToModel(self.inputPlanSelector.currentNode(), self.modelHNode)
 

  def onPreopSegmentationChanged(self):
    if self.inputPlanSelector.currentNode == None:
      return
    self.modelGenButton.enabled = True
    
  def onPreopVolumeChanged(self):
      if self.inputScanSelector.currentNode == None:
        return
    
  def onEntryPose1SelectorChanged(self):
    if self.entryPose1Selector.currentNode() != None:
      if self.entryPose1Selector.currentNode().GetNumberOfFiducials() == 0:
        self.selectionNode.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsFiducialNode")
        self.selectionNode.SetActivePlaceNodeID(self.entryPose1Selector.currentNode().GetID())
        placeModePersistence = 0
        slicer.modules.markups.logic().StartPlaceMode(placeModePersistence)  
        self.entryPose1Selector.addEnabled = False
      self.entryPose1Selector.currentNode().RemoveAllObservers()
      tag = self.entryPose1Selector.currentNode().AddObserver(vtk.vtkCommand.ModifiedEvent, self.onFiducialsModified1)
      self.entryPose1AddedFlag = True
      self.onAddProbe1()
        
      
    
  def onTargetPose1SelectorChanged(self):   
    if self.targetPose1Selector.currentNode() != None:
      if self.targetPose1Selector.currentNode().GetNumberOfFiducials() == 0:
        self.selectionNode.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsFiducialNode")
        self.selectionNode.SetActivePlaceNodeID(self.targetPose1Selector.currentNode().GetID())
        placeModePersistence = 0
        slicer.modules.markups.logic().StartPlaceMode(placeModePersistence)  
        self.targetPose1Selector.addEnabled = False
      self.targetPose1Selector.currentNode().RemoveAllObservers()
      tag = self.targetPose1Selector.currentNode().AddObserver(vtk.vtkCommand.ModifiedEvent, self.onFiducialsModified1)
      self.targetPose1AddedFlag = True
      self.onAddProbe1()
        
    
  def onEntryPose2SelectorChanged(self):
    if self.entryPose2Selector.currentNode() != None:
      if self.entryPose2Selector.currentNode().GetNumberOfFiducials() == 0:
        self.selectionNode.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsFiducialNode")
        self.selectionNode.SetActivePlaceNodeID(self.entryPose2Selector.currentNode().GetID())
        placeModePersistence = 0
        slicer.modules.markups.logic().StartPlaceMode(placeModePersistence)  
        self.entryPose2Selector.addEnabled = False
      self.entryPose2Selector.currentNode().RemoveAllObservers()
      tag = self.entryPose2Selector.currentNode().AddObserver(vtk.vtkCommand.ModifiedEvent, self.onFiducialsModified2)
      self.entryPose2AddedFlag = True
      self.onAddProbe2()
    
  def onTargetPose2SelectorChanged(self):
    if self.targetPose2Selector.currentNode() != None:
      if self.targetPose2Selector.currentNode().GetNumberOfFiducials() == 0:
        self.selectionNode.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsFiducialNode")
        self.selectionNode.SetActivePlaceNodeID(self.targetPose2Selector.currentNode().GetID())
        placeModePersistence = 0
        slicer.modules.markups.logic().StartPlaceMode(placeModePersistence)  
        self.targetPose2Selector.addEnabled = False
      self.targetPose2Selector.currentNode().RemoveAllObservers()
      tag = self.targetPose2Selector.currentNode().AddObserver(vtk.vtkCommand.ModifiedEvent, self.onFiducialsModified2)
      self.targetPose2AddedFlag = True
      self.onAddProbe2()

  
  # action to be taken in case of deletion of markups  
  def onDeleteProbe1Button(self):
    self.probe1PathTransform.SetMatrixTransformToParent(self.identity)
    slicer.mrmlScene.RemoveNode(self.entryPose1Selector.currentNode())
    slicer.mrmlScene.RemoveNode(self.targetPose1Selector.currentNode())
    modellist = slicer.util.getNodesByClass('vtkMRMLModelNode')
    for i in range (0, len(modellist)):
      if 'Probe1' in modellist[i].GetName():
        slicer.mrmlScene.RemoveNode(modellist[i])
    self.probe1Model = None
    self.probe1path = None
    self.entryPose1Selector.addEnabled = True
    self.targetPose1Selector.addEnabled = True
  

    
  def onDeleteProbe2Button(self):
    self.probe2PathTransform.SetMatrixTransformToParent(self.identity)
    slicer.mrmlScene.RemoveNode(self.entryPose2Selector.currentNode())
    slicer.mrmlScene.RemoveNode(self.targetPose2Selector.currentNode())
    modellist = slicer.util.getNodesByClass('vtkMRMLModelNode')
    for i in range (0, len(modellist)):
      if 'Probe2' in modellist[i].GetName():
        slicer.mrmlScene.RemoveNode(modellist[i])
    self.probe2Model = None
    self.probe2path = None
    self.entryPose2Selector.addEnabled = True
    self.targetPose2Selector.addEnabled = True 
  
  

# TreatmentPlanReaderLogic
#
class LoadDataLogic(ScriptedLoadableModuleLogic):

  def __init__(self):
    self.trajectoryModelNode=None
    
  def volumeToModel(self, volumeLabelNode, modelHNode):

    parameters = {}
    parameters['InputVolume'] = volumeLabelNode.GetID()
    parameters['Labels'] = volumeLabelNode.GetName()
    parameters['Name'] = "TreatmentPlanModel"
    parameters['ModelSceneFile'] = modelHNode.GetID()
    parameters['Smooth'] = 15
    parameters['Labels'] = [1]
    parameters['Pad'] = False
    parameters['GenerateAll'] = True
    parameters['SkipUnNamed'] = False
    parameters['SplitNormals'] = False
    print "Model generation Started..."
    modelMaker = slicer.modules.modelmaker
    slicer.util.showStatusMessage("Model Making Started...", 2000)
    slicer.cli.run(modelMaker, None, parameters, True)
    print "Model generation Complete"
  
  
  
  def createTrajectoryModel (self):
    createModelLogic = slicer.modules.createmodels.logic()
    trajectoryModelNode = slicer.vtkMRMLModelNode()
    trajectoryModelNode = createModelLogic.CreateCylinder(100,0.05)
    probeModelDisplayNode = trajectoryModelNode.GetDisplayNode()
    probeModelDisplayNode.SetColor([1,0,0])   
    probeModelDisplayNode.SetOpacity(0.5)
    probeModelDisplayNode.SetSliceIntersectionVisibility(1)
    slicer.mrmlScene.AddNode(trajectoryModelNode)
    self.trajectoryModelNode=trajectoryModelNode;
    return trajectoryModelNode
    
  def getModel(self):
    return self.trajectoryModelNode
        
      
  def updateTransform(self, targetFiducialList, entryFiducialList, probeModelTransform):


    if targetFiducialList != None and entryFiducialList != None:
      targetPoint = [0, 0, 0]
      entryPoint = [0, 0, 0]
      targetFiducialList.GetNthFiducialPosition(0, targetPoint)
      entryFiducialList.GetNthFiducialPosition(0, entryPoint)

      if targetPoint != [0,0,0] and entryPoint != [0,0,0]:
        zVector = [targetPoint[0]-entryPoint[0], targetPoint[1]-entryPoint[1], targetPoint[2]-entryPoint[2]]
        xVector = [1,0,0]
        yVector = np.cross(zVector,xVector)
        xVector = np.cross(yVector,zVector)
        
        try:
          zVector = zVector/np.linalg.norm(zVector)
        except:
          pass
        try:
          yVector = yVector / np.linalg.norm(yVector)
        except:
          pass
        try:
          xVector = xVector / np.linalg.norm(xVector)
        except:
          pass

        matrix = vtk.vtkMatrix4x4()
        probeModelTransform.GetMatrixTransformToParent(matrix)
        matrix.SetElement(0, 0, xVector[0])
        matrix.SetElement(1, 0, xVector[1])
        matrix.SetElement(2, 0, xVector[2])
        matrix.SetElement(0, 1, yVector[0])
        matrix.SetElement(1, 1, yVector[1])
        matrix.SetElement(2, 1, yVector[2])
        matrix.SetElement(0, 2, zVector[0])
        matrix.SetElement(1, 2, zVector[1])
        matrix.SetElement(2, 2, zVector[2])
        matrix.SetElement(0, 3, targetPoint[0])
        matrix.SetElement(1, 3, targetPoint[1])
        matrix.SetElement(2, 3, targetPoint[2])
        probeModelTransform.SetMatrixTransformToParent(matrix)
        return probeModelTransform
    else:
      matrix = vtk.vtkMatrix4x4()
      probeModelTransform.GetMatrixTransformToParent(matrix)
      probeModelTransform.SetMatrixTransformToParent(matrix)
      return probeModelTransform
  
  
class LoadDataTest(ScriptedLoadableModuleTest):
 
  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)
