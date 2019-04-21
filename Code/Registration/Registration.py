import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import RegistrationLib
import EditorLib
#
# ImageRegistration
#

class Registration(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Registration" # TODO make this more human readable by adding spaces
    self.parent.categories = ["RFANav"]
    self.parent.dependencies = []
    self.parent.contributors = ["Deniz J, Michael H (SRI)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
Spinal Metastases RFA procedure navigation workflow - MHSc Thesis
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """

""" # replace with organization, grant and thanks.

#
# ImageRegistrationWidget
#

class RegistrationWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    self.developerMode = True
    ScriptedLoadableModuleWidget.setup(self)
    self.logic = RegistrationLogic()
    self.cropVolumeParameterNode = slicer.vtkMRMLCropVolumeParametersNode()
    
    # why initializing them here?
    
    self.VIEW_MODE_Preop_Only = 0 
    self.VIEW_MODE_Intraop_Only = 1
    self.VIEW_MODE_ThreeCompare = 2
    self.VIEW_MODE_Axial = 3
    self.VIEW_MODE_Sagittal = 4
    self.VIEW_MODE_Coronal = 5
    
    self.PREOP_VOLUME = None
    self.INTRAOP_VOLUME = None

    
    volumes = slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode")
    for i in range(0,len(volumes)):
        if 'Preop' in volumes[i].GetName():
          self.PREOP_VOLUME = volumes[i]
        elif 'Intraop' in volumes[i].GetName():
          self.INTRAOP_VOLUME = volumes[i]
            
    
    
    scansCollapsibleButton = ctk.ctkCollapsibleButton()
    scansCollapsibleButton.text = "Volumes"
    
    self.layout.addWidget(scansCollapsibleButton)
    scansFormLayout = qt.QFormLayout(scansCollapsibleButton)
    # Layout within the dummy collapsible button
    
    
    # input inputBackVol
    self.inputBackVol = slicer.qMRMLNodeComboBox()
    self.inputBackVol.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.inputBackVol.selectNodeUponCreation = True
    self.inputBackVol.setAutoFillBackground(self.INTRAOP_VOLUME)
    self.inputBackVol.addEnabled = False
    self.inputBackVol.removeEnabled = False
    self.inputBackVol.noneEnabled = True
    self.inputBackVol.showHidden = False
    self.inputBackVol.showChildNodeTypes = False
    self.inputBackVol.setMRMLScene( slicer.mrmlScene )
    self.inputBackVol.setToolTip( "Pick the input scan to the algorithm." )
  #  self.layout.addWidget("Input Background Volume: ", self.inputBackVol)
    # input vol node connection
    self.inputBackVol.connect("currentNodeChanged(vtkMRMLNode*)", self.onInputBackVol)
    
    # input inputBackVol
    self.inputForVol = slicer.qMRMLNodeComboBox()
    self.inputForVol.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.inputForVol.selectNodeUponCreation = True
    self.inputForVol.setAutoFillBackground(self.PREOP_VOLUME)
    self.inputForVol.addEnabled = False
    self.inputForVol.removeEnabled = False
    self.inputForVol.noneEnabled = True
    self.inputForVol.showHidden = False
    self.inputForVol.showChildNodeTypes = False
    self.inputForVol.setMRMLScene( slicer.mrmlScene )
    self.inputForVol.setToolTip( "Pick the input scan to the algorithm." )
  #  self.layout.addWidget("Input Foreground Volume: ", self.inputForVol)
    # input vol node connection
    self.inputForVol.connect("currentNodeChanged(vtkMRMLNode*)", self.onInputForVol)   
    scansFormLayout.addRow("Input Intraop Volume: ", self.inputBackVol)
    scansFormLayout.addRow("Input Preop Volume: ", self.inputForVol)
    
    #  
    # ROI Area
    #
    self.roiCollapsibleGroupBox = ctk.ctkCollapsibleGroupBox()
    self.roiCollapsibleGroupBox.title = "Define ROI"
    self.roiCollapsibleGroupBox.collapsed = True
    self.layout.addWidget(self.roiCollapsibleGroupBox)

    # Layout within the dummy collapsible button
    roiFormLayout = qt.QFormLayout(self.roiCollapsibleGroupBox)

    # input intraop/fixed volume selector
    self.inputVol = slicer.qMRMLNodeComboBox()
    self.inputVol.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.inputVol.selectNodeUponCreation = True
    self.inputVol.setAutoFillBackground(False)
    self.inputVol.addEnabled = False
    self.inputVol.removeEnabled = False
    self.inputVol.noneEnabled = True
    self.inputVol.showHidden = False
    self.inputVol.showChildNodeTypes = False
    self.inputVol.setMRMLScene( slicer.mrmlScene )
    self.inputVol.setToolTip( "Pick the input scan to the algorithm." )
    roiFormLayout.addRow("Input Volume: ", self.inputVol)
    # input vol node connection
    self.inputVol.connect("currentNodeChanged(vtkMRMLNode*)", self.onInputVol)

    # ROI Buttons
    self.defineROIButton = qt.QPushButton("Define ROI")
    self.defineROIButton.enabled = False
    self.defineROIButton.toolTip = "Define the region/vertebrae of the interest"

    self.applyROIButton = qt.QPushButton("Crop the ROI")
    self.applyROIButton.enabled = False
    self.defineROIButton.toolTip = "Crop the region/vertebrae of the interest"
    # place them on GUI side by side
    roiFormLayout.addWidget(self.createHLayout([self.defineROIButton, self.applyROIButton]))

    self.defineROIButton.connect("clicked(bool)", self.onDefineROIButton)

    self.applyROIButton.connect("clicked(bool)", self.onApplyROIButton)


    self.thresholdGroupBox = ctk.ctkCollapsibleGroupBox()
    self.thresholdGroupBox.title = "Generate Mesh"
    self.thresholdGroupBox.collapsed = True
    roiFormLayout.addRow(self.thresholdGroupBox)
    self.thresholdGroupBox.connect('clicked(bool)' , self.onGenerateMeshGroupBox)
    
    thresholdGroupBoxLayout = qt.QFormLayout(self.thresholdGroupBox)
    # threshold value
    self.threshold = ctk.ctkRangeWidget()
    self.threshold.spinBoxAlignment = 0xff  # put enties on top
    self.threshold.singleStep = 0.1
    self.threshold.minimum = -1000
    self.threshold.maximum = 3000
    self.threshold.setToolTip(
      "Set the range of the background values that should be labeled.")
    thresholdGroupBoxLayout.addRow("Image threshold", self.threshold)
    # Generate Mesh based on the cursour movment
    
    self.generateMeshButton = qt.QPushButton("Generate Mesh")
    self.generateMeshButton.enabled = False
    self.generateMeshButton.toolTip = "Crop the region/vertebrae of the interest"
    # place them on GUI side by side
    thresholdGroupBoxLayout.addRow(self.generateMeshButton)
    
    self.generateMeshButton.connect('clicked()', self.onMeshButton)  # connection
    
    

    # Instantiate and connect widgets ...
    self.displayLayoutBox = qt.QGroupBox('Display Layout')
    self.displayLayout = qt.QGridLayout()
    self.displayLayoutBox.setLayout(self.displayLayout)
    self.layout.addWidget(self.displayLayoutBox)
        
    # button to only show preop volume 
    self.PreopOnlyButton = qt.QPushButton("Preop Only")
    self.PreopOnlyButton.name = "Preop Only"
    self.PreopOnlyButton.setCheckable(True)
    self.PreopOnlyButton.setFlat(True)
    self.displayLayout.addWidget(self.PreopOnlyButton, 0, 0)
    self.PreopOnlyButton.connect('clicked()', lambda: self.onViewMode(self.VIEW_MODE_Preop_Only))  
    
    # button to only show intraop volume 
    self.IntraopOnlyButton = qt.QPushButton("Intraop Only")
    self.IntraopOnlyButton.name = "Intraop Only"
    self.IntraopOnlyButton.setCheckable(True)
    self.IntraopOnlyButton.setFlat(True)
    self.displayLayout.addWidget(self.IntraopOnlyButton, 0, 1)
    self.IntraopOnlyButton.connect('clicked()', lambda: self.onViewMode(self.VIEW_MODE_Intraop_Only))
    
    # button to show the overalp of the intraop and preop volumes 
    self.OverlapButton = qt.QPushButton("Ax/Sa/Co")
    self.OverlapButton.name = "Ax/Sa/Co"
    self.OverlapButton.setCheckable(True)
    self.OverlapButton.setFlat(True)
    self.displayLayout.addWidget(self.OverlapButton, 0, 2)
    self.OverlapButton.connect('clicked()', lambda: self.onViewMode(self.VIEW_MODE_ThreeCompare))
    
    # button to only show Axial view of preop, intraop, and overlap  
    self.AxialButton = qt.QPushButton("Axial View")
    self.AxialButton.name = "Axial View"
    self.AxialButton.setCheckable(True)
    self.AxialButton.setFlat(True)
    self.displayLayout.addWidget(self.AxialButton, 1, 0)
    self.AxialButton.connect('clicked()', lambda: self.onViewMode(self.VIEW_MODE_Axial))
    
    # button to only show Sagittal view of preop, intraop, and overlap  
    self.SagittalButton = qt.QPushButton("Sagittal View")
    self.SagittalButton.name = "Sagittal View"
    self.SagittalButton.setCheckable(True)
    self.SagittalButton.setFlat(True)
    self.displayLayout.addWidget(self.SagittalButton, 1, 1)
    self.SagittalButton.connect('clicked()', lambda: self.onViewMode(self.VIEW_MODE_Sagittal))
    
    # button to only show Coronal view of preop, intraop, and overlap  
    self.CoronalButton = qt.QPushButton("Coronal View")
    self.CoronalButton.name = "Coronal View"
    self.CoronalButton.setCheckable(True)
    self.CoronalButton.setFlat(True)
    self.displayLayout.addWidget(self.CoronalButton, 1, 2)
    self.CoronalButton.connect('clicked()', lambda: self.onViewMode(self.VIEW_MODE_Coronal))
    
    # extra visualization    
    self.VisualizationGroupBox = ctk.ctkCollapsibleGroupBox()
    self.VisualizationGroupBox.title = "Visualization"
    self.VisualizationGroupBox.collapsed = True
    self.layout.addWidget(self.VisualizationGroupBox)
    VisualizationFormLayout = qt.QFormLayout(self.VisualizationGroupBox)
    self.visualizationWidget = RegistrationLib.VisualizationWidget(self.logic)
    b = self.visualizationWidget.widget
    allChildren = b.children()[1].children()[1].children()
    groupbox = b.children()[1].children()[1]
    groupbox.setTitle('')
    allChildren[1].hide()
    allChildren[2].hide()
    allChildren[3].hide()
    allChildren[4].hide()
    VisualizationFormLayout.addWidget(b)
    
       
   

    # Landmark Registration Area        
    fiducialregistrationwizardModuleWidget = slicer.modules.fiducialregistrationwizard.createNewWidgetRepresentation()
    fiducialregistrationwizardModuleWidgetGroupBoxes = fiducialregistrationwizardModuleWidget.findChildren("ctkCollapsibleGroupBox")
    fiducialregistrationwizardModuleWidgetQGroupBoxes = fiducialregistrationwizardModuleWidget.findChildren("QGroupBox")
    self.FidRegWizRegResultComboBox = fiducialregistrationwizardModuleWidgetQGroupBoxes[3].children()[1]
    fiducialregistrationwizardModuleWidgetGroupBoxes[2].hide() #hide the landmark from transform 
    # hide extra crap
    extra = fiducialregistrationwizardModuleWidget.children()[1].children()
    self.FiducialRegWizNode = slicer.vtkMRMLFiducialRegistrationWizardNode()
    
    slicer.mrmlScene.AddNode(self.FiducialRegWizNode)
    tag = self.FiducialRegWizNode.AddObserver(vtk.vtkCommand.ModifiedEvent, self.onFiducialRegWizNode)
    extra[1].setCurrentNode(self.FiducialRegWizNode)
    extra[1].hide()
    extra[3].hide()
    extra[4].hide()
    #registrationResult = extra[8]
    #initialregTransformBox = registrationResult.children()[1]
    #self.initialLandmarkTransform
    #initialregTransformBox.setCurrentNode(slicer.util.getNode('FromPreopToIntraopInitialTransform'))
    
    fiducialregistrationwizardModuleWidgetCollapsibleButton = fiducialregistrationwizardModuleWidget.findChildren("ctkCollapsibleButton")
    fiducialregistrationwizardModuleWidgetCollapsibleButton[0].setText('Landmark Registration')
    fiducialregistrationwizardModuleWidgetCollapsibleButton[0].collapsed = True
    #fiducialregistrationwizardModuleWidgetGroupBoxes[3].setText('')   
    self.layout.addWidget(fiducialregistrationwizardModuleWidget)
   
    
    AutoCollapsibleButton = ctk.ctkCollapsibleButton()
    AutoCollapsibleButton.text = "Auto Registrationn"
    self.layout.addWidget(AutoCollapsibleButton)
    AutoCollapsibleButton.collapsed = True
    # Layout within the dummy collapsible button
    autoFormLayout = qt.QFormLayout(AutoCollapsibleButton)
    
    self.rigidCheckmarkBox = qt.QCheckBox()
    self.rigidCheckmarkBox.checked = 1
    self.rigidCheckmarkBox.setToolTip("If checked, the rigid registration is performed (6 DOF)")
    
    self.rigidscaleCheckmarkBox = qt.QCheckBox()
    self.rigidscaleCheckmarkBox.checked = 0
    self.rigidscaleCheckmarkBox.setToolTip("If checked, the rigid and scaling is performed (7 DOF)")
   
    
    # Auto Rigid Registration Button
    self.autoRegButton = qt.QPushButton("Run Registration")
    self.autoRegButton.toolTip = "Run the automatic brains rigid registration algorithm."
    self.autoRegButton.enabled = True  
    self.autoRegButton.connect('clicked(bool)', self.onautoRegButton)  # connection
    
    # input moving mesh 
    self.inputMovingMesh = slicer.qMRMLNodeComboBox()
    self.inputMovingMesh.nodeTypes = ["vtkMRMLLabelMapVolumeNode"]
    self.inputMovingMesh.selectNodeUponCreation = True
    self.inputMovingMesh.addEnabled = False
    self.inputMovingMesh.removeEnabled = False
    self.inputMovingMesh.noneEnabled = True
    self.inputMovingMesh.showHidden = False
    self.inputMovingMesh.showChildNodeTypes = False
    self.inputMovingMesh.setMRMLScene( slicer.mrmlScene )
    self.inputMovingMesh.setToolTip( "Pick the input mesh for intraop scan" )
    
    #self.inputVol.connect("currentNodeChanged(vtkMRMLNode*)", self.onInputPreopMesh)
    
    # input fixed mesh 
    self.inputFixedMesh = slicer.qMRMLNodeComboBox()
    self.inputFixedMesh.nodeTypes = ["vtkMRMLLabelMapVolumeNode"]
    self.inputFixedMesh.selectNodeUponCreation = True
    self.inputFixedMesh.addEnabled = False
    self.inputFixedMesh.removeEnabled = False
    self.inputFixedMesh.noneEnabled = True
    self.inputFixedMesh.showHidden = False
    self.inputFixedMesh.showChildNodeTypes = False
    self.inputFixedMesh.setMRMLScene( slicer.mrmlScene )
    self.inputFixedMesh.setToolTip( "Pick the input mesh for intraop scan" )
    
   # self.inputMovingMesh.connect("currentNodeChanged(vtkMRMLNode*)", self.onInputPreopMesh)
   # self.inputFixedMesh.connect("currentNodeChanged(vtkMRMLNode*)", self.onInputIntraopMesh)
  
    autoFormLayout.addRow('Rigid (6 DOF)', self.rigidCheckmarkBox)
    autoFormLayout.addRow('Rigid+Scaling (7 DOF)', self.rigidscaleCheckmarkBox)
    
    autoFormLayout.addRow("Input Intraop Mesh: ", self.inputFixedMesh)
    autoFormLayout.addRow("Input Preop Mesh: ", self.inputMovingMesh)
    autoFormLayout.addRow(self.autoRegButton)
    # Add vertical spacer
    self.layout.addStretch(1)
    
    
   

      
  # put buttons side by side
  def createHLayout(self, elements):
    widget = qt.QWidget()
    rowLayout = qt.QHBoxLayout()
    rowLayout.setContentsMargins(0, 0, 0, 0)
    widget.setLayout(rowLayout)
    for element in elements:
      rowLayout.addWidget(element)
    return widget

  # enabling different view modes 
  def onViewMode(self, mode):
    
    displayLayoutManager = slicer.app.layoutManager()
    
    # PREOP ONLY VIEW 
    if mode == self.VIEW_MODE_Preop_Only:
      self.RestViewButtons(self.PreopOnlyButton.name)
      displayLayoutManager.layout = slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView
      self.ResetSliceOrientations()
      slicer.util.setSliceViewerLayers(foregroundOpacity=1)
      defaultSliceCompositeNode = slicer.vtkMRMLSliceCompositeNode()
      defaultSliceCompositeNode.SetLinkedControl(1)
      slicer.mrmlScene.AddDefaultNode(defaultSliceCompositeNode)
      
    # INTRAOP ONLY VIEW   
    if mode == self.VIEW_MODE_Intraop_Only:
      self.RestViewButtons(self.IntraopOnlyButton.name)
      displayLayoutManager.layout = slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView
      self.ResetSliceOrientations()
      slicer.util.setSliceViewerLayers(foregroundOpacity=0)
      defaultSliceCompositeNode = slicer.vtkMRMLSliceCompositeNode()
      defaultSliceCompositeNode.SetLinkedControl(1)
      slicer.mrmlScene.AddDefaultNode(defaultSliceCompositeNode)

    # THREE SLICE COMPARISSON VIEW    
    if mode == self.VIEW_MODE_ThreeCompare:
      self.RestViewButtons(self.OverlapButton.name)
      displayLayoutManager.layout = slicer.vtkMRMLLayoutNode.SlicerLayoutThreeOverThreeView
      self.ResetSliceOrientations()
      for color in ['Red', 'Yellow', 'Green']:
        displayLayoutManager.sliceWidget(color).sliceLogic().GetSliceCompositeNode().SetForegroundOpacity(0)

      for color in ['Red+', 'Yellow+', 'Green+']:
        displayLayoutManager.sliceWidget(color).sliceLogic().GetSliceCompositeNode().SetForegroundOpacity(1)
      
    # AXIAL SLICE COMPARISSON VIEWS
    if mode == self.VIEW_MODE_Axial:
      self.RestViewButtons(self.AxialButton.name)
      displayLayoutManager.layout = slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView
      displayLayoutManager.sliceWidget('Red').sliceLogic().GetSliceCompositeNode().SetForegroundOpacity(0)
      displayLayoutManager.sliceWidget('Yellow').sliceLogic().GetSliceCompositeNode().SetForegroundOpacity(1)
      displayLayoutManager.sliceWidget('Green').sliceLogic().GetSliceCompositeNode().SetForegroundOpacity(0.5)
      for color in ['Red', 'Yellow', 'Green']:
        displayLayoutManager.sliceWidget(color).setSliceOrientation('Axial')
        #unlinking the views
        displayLayoutManager.sliceWidget(color).sliceLogic().GetSliceCompositeNode().SetLinkedControl(0)
             
    # SAGITTAL SLICE COMPARISSON VIEWS     
    if mode == self.VIEW_MODE_Sagittal:
      self.RestViewButtons(self.SagittalButton.name)
      displayLayoutManager.layout = slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView
      displayLayoutManager.sliceWidget('Red').sliceLogic().GetSliceCompositeNode().SetForegroundOpacity(0)
      displayLayoutManager.sliceWidget('Yellow').sliceLogic().GetSliceCompositeNode().SetForegroundOpacity(1)
      displayLayoutManager.sliceWidget('Green').sliceLogic().GetSliceCompositeNode().SetForegroundOpacity(0.5)
      for color in ['Red', 'Yellow', 'Green']:
        displayLayoutManager.sliceWidget(color).setSliceOrientation('Sagittal')
        #unlinking the views
        displayLayoutManager.sliceWidget(color).sliceLogic().GetSliceCompositeNode().SetLinkedControl(0)
    
    # CORONAL SLICE COMPARISSON VIEWS    
    if mode == self.VIEW_MODE_Coronal:
      self.RestViewButtons(self.CoronalButton.name)
      for color in ['Red', 'Yellow', 'Green']:
        displayLayoutManager.sliceWidget(color).setSliceOrientation('Coronal')
        #unlinking the views
        displayLayoutManager.sliceWidget(color).sliceLogic().GetSliceCompositeNode().SetLinkedControl(0)
      displayLayoutManager.layout = slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView
      displayLayoutManager.sliceWidget('Red').sliceLogic().GetSliceCompositeNode().SetForegroundOpacity(0)
      displayLayoutManager.sliceWidget('Yellow').sliceLogic().GetSliceCompositeNode().SetForegroundOpacity(1)
      displayLayoutManager.sliceWidget('Green').sliceLogic().GetSliceCompositeNode().SetForegroundOpacity(0.5)
      
      
 
    
  def RestViewButtons(self, trueButtonName):
    for button in [self.PreopOnlyButton, self.IntraopOnlyButton, self.OverlapButton, self.AxialButton, self.SagittalButton, self.CoronalButton]:
      if button.name == trueButtonName:
        button.setChecked(True)
      else:
        button.setChecked(False)
        
  def ResetSliceOrientations(self):
    slicer.app.layoutManager().sliceWidget('Red').setSliceOrientation('Axial')
    slicer.app.layoutManager().sliceWidget('Yellow').setSliceOrientation('Sagittal')
    slicer.app.layoutManager().sliceWidget('Green').setSliceOrientation('Coronal')
    
  def onFiducialRegWizNode(self, observer, eventId):
    if self.FiducialRegWizNode.GetOutputTransformNode() == None:
      self.initialLandmarkTransform = slicer.vtkMRMLTransformNode()
      self.initialLandmarkTransform.SetName("FromPreopToIntraopInitialTransform")
      slicer.mrmlScene.AddNode(self.initialLandmarkTransform)
      self.FidRegWizRegResultComboBox.setCurrentNode(self.initialLandmarkTransform)
    else: 
      self.initialLandmarkTransform = self.FiducialRegWizNode.GetOutputTransformNode()
      
      
  def onInputBackVol(self):
    slicer.util.setSliceViewerLayers(background = self.inputBackVol.currentNode())
    self.INTRAOP_VOLUME = self.inputBackVol.currentNode()
    
  def onInputForVol(self):
    slicer.util.setSliceViewerLayers(foreground = self.inputForVol.currentNode())
    self.PREOP_VOLUME = self.inputForVol.currentNode()
      

  def onInputVol(self):
    if self.inputVol.currentNode == None:
      return
    slicer.util.setSliceViewerLayers(background=self.inputVol.currentNode())
    self.defineROIButton.enabled = True

  # define ROI button actiondefineROIRun
  def onDefineROIButton(self):
    self.logic.defineROIRun(self.inputVol.currentNode(), self.cropVolumeParameterNode)
    self.applyROIButton.enabled = True
    self.defineROIButton.enabled = False

  def onApplyROIButton(self):
    self.logic.applyROIRun(self.cropVolumeParameterNode)
    # set the slice views to the cropped volume
    newVolname = self.inputVol.currentNode().GetName() + '_Cropped'
    slicer.util.setSliceViewerLayers(background=slicer.util.getNode(newVolname))
    # turn off the scene visibility of the ROI box
    items = slicer.util.getNodesByClass('vtkMRMLAnnotationROINode')
    for i in items:
      i.SetDisplayVisibility(0)
    self.inputVol.setCurrentNode(slicer.util.getNode(newVolname))

  def onGenerateMeshGroupBox(self):
    self.generateMeshButton.enabled = True 
  # generate mesh of the ROI
  def onMeshButton(self):
    if self.inputVol.currentNode == None:
      return
    masterVolume = self.inputVol.currentNode()
    self.logic.thresholdVolumeRun(masterVolume, self.threshold.minimumValue, self.threshold.maximumValue)
    labelVolume = slicer.util.getNode(masterVolume.GetName() + '-label')
    if 'Preop' in labelVolume.GetName():
      self.inputMovingMesh.currentNode = labelVolume
    elif 'Inraop' in labelVolume.GetName():
      self.inputFixedMesh.currentNode = labelVolume
      
  # perform the initial landmark registration
  if 0:
      def onapplyFidRegButton(self):
        pass
        # run fiducial registration algorithm
        # display rms error
        self.rmsValue = 0
        self.logic.landmarkRegRun(self.intraFid.currentNode(), self.preFid.currentNode(), self.transformSelector.currentNode(), self.rmsValue)
        self.outputLine.setText(self.rmsValue)


  # perform the auto rigid registration
  def onautoRegButton(self):
    self.outputTransform = slicer.vtkMRMLLinearTransformNode()
    self.logic.rigidVolumeRegistration(self.INTRAOP_VOLUME, self.PREOP_VOLUME, self.inputMovingMesh.currentNode(), self.inputFixedMesh.currentNode(), self.rigidCheckmarkBox.isChecked(), self.rigidscaleCheckmarkBox.isChecked())
    self.outputTransform = slicer.mrmlScene.GetNodesByName('PreopToIntraopAutodRegTransform').GetItemAsObject(0)
    #if self.outputTransform != None:
      
    
  
    # CODE FOR ELASTIX REGISTRATION
    #ElastixLogic = slicer.modules.elastix.logic()
    #logic = ElastixLogic()
    #parameterFilenames = logic.getRegistrationPresets()[0][RegistrationPresets_ParameterFilenames]
    #logic.registerVolumes(tumor1, tumor2, parameterFilenames=parameterFilenames, outputVolumeNode=outputVolume)



#
# RegistrationLogic
#

class RegistrationLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  
  """

  # define RIO
  def defineROIRun(self, originalVolume, cropVolumeParameterNode):
    roi = slicer.vtkMRMLAnnotationROINode()
    roi.SetName(originalVolume.GetName()+ "_ROI")
    slicer.mrmlScene.AddNode(roi)

    croppedVolume = slicer.vtkMRMLScalarVolumeNode()
    croppedVolume.SetName(originalVolume.GetName() + "_Cropped")
    slicer.mrmlScene.AddNode(croppedVolume)

    cropVolumeParameterNode.SetInputVolumeNodeID(originalVolume.GetID())
    cropVolumeParameterNode.SetOutputVolumeNodeID(croppedVolume.GetID())
    cropVolumeParameterNode.SetROINodeID(roi.GetID())

    # set ROI Annotation box to cover the whole volume
    volumeBounds_ROI, roiCenter, roiRadius = [0, 0, 0, 0, 0, 0], [0, 0, 0], [0, 0, 0]
    originalVolume.GetSliceBounds(volumeBounds_ROI, vtk.vtkMatrix4x4())
    for i in range(3):
      roiCenter[i] = (volumeBounds_ROI[i * 2 + 1] + volumeBounds_ROI[i * 2]) / 2
      roiRadius[i] = (volumeBounds_ROI[i * 2 + 1] - volumeBounds_ROI[i * 2]) / 2
    roi.SetXYZ(roiCenter)
    roi.SetRadiusXYZ(roiRadius)

  # crop the volume
  def applyROIRun(self, cropVolumeParameterNode):
    slicer.modules.cropvolume.logic().Apply(cropVolumeParameterNode)



  def volumeToModel(self, volumeLabelNode, modelNode):

    # modelHierarchyNode = slicer.vtkMRMLModelHierarchyNode()
    # modelHierarchyNode.SetScene(slicer.mrmlScene)
    # slicer.mrmlScene.AddNode(modelHierarchyNode)

    #modelHNode = slicer.mrmlScene.CreateNodeByClass('vtkMRMLModelHierarchyNode')
    #modelHNode.SetName(modelNode)
    #modelHNode = slicer.mrmlScene.AddNode(modelHNode)
    print volumeLabelNode.GetName()
    parameters = {}
    parameters['InputVolume'] = volumeLabelNode.GetID()
    parameters['Labels'] = volumeLabelNode.GetName()
    parameters['Name'] = "models"

    parameters['ModelSceneFile'] = modelNode.GetID()
    parameters['Smooth'] = 15
    parameters['Labels'] = [1]
    parameters['Pad'] = False
    parameters['GenerateAll'] = True
    parameters['SkipUnNamed'] = False
    parameters['SplitNormals'] = False

    print "Model generation Started..."
    modelMaker = slicer.modules.modelmaker
    slicer.util.showStatusMessage("Model Making Started...", 2000)
    node = slicer.cli.run(modelMaker, None, parameters, True)
    print "Model generation Complete"
    return node

  #def thresholdVolumeRun(self, masterVolume, volumeLabel, minThreshold, maxThreshold):
  def thresholdVolumeRun(self, masterVolume, minThreshold, maxThreshold):
    # returns label volume

    widg = slicer.modules.editor.widgetRepresentation()
    editorWidget = slicer.modules.EditorWidget
    editorWidget.setMasterNode(masterVolume)
    #editorWidget.setMergeNode(volumeLabel)
    slicer.modules.EditorWidget.toolsBox.selectEffect('ThresholdEffect')

    editUtil = EditorLib.EditUtil.EditUtil()
    parameterNode = editUtil.getParameterNode()
    parameterNode.SetParameter("label", "2")

    sbs = widg.findChildren('QDoubleSpinBox')
    minThresh = sbs[0]
    maxThresh = sbs[1]
    minThresh.setValue(minThreshold)
    maxThresh.setValue(maxThreshold)
    pbs = widg.findChildren('QPushButton')
    applyThresholdButton = pbs[7]
    applyThresholdButton.click()
    slicer.modules.EditorWidget.toolsBox.selectEffect('SaveIslandEffect')
    print('mesh generated.')


  def landmarkRegRun(self, fixedLandmarks, movingLandmarks, saveTransform, rmsValue):
    message = ""
    parameters = {}
    parameters['fixedLandmarks'] = fixedLandmarks.GetID()
    parameters['movingLandmarks'] = movingLandmarks.GetID()
    parameters['saveTransform'] = saveTransform.GetID()

    parameters['transformType'] = "Rigid"
    parameters['rms'] = rmsValue.GetID()
    parameters['outputMessage'] = message

    FiducialRegistration = slicer.modules.fiducialregistration
    slicer.util.showStatusMessage("Landmark Registration Started...", 2000)
    slicer.cli.run(FiducialRegistration, None, parameters, True)
    print "Landmark Registration Complete"
    print(message)



  def registerVolumesElastix(self,fixedVolumeNode, movingVolumeNode, outputTransform,
    fixedVolumeMask, movingVolumeMask):

    outputVolume = slicer.vtkMRMLScalarVolumeNode()
    slicer.mrmlScene.AddNode(outputVolume)
    outputVolume.CreateDefaultDisplayNodes()

    logic = slicer.modules.elastix.logic()
    parameterFilenames = logic.getRegistrationPresets()[0][RegistrationPresets_ParameterFilenames]

    logic.registerVolumes(fixedVolumeNode, movingVolumeNode, parameterFilenames=parameterFilenames, outputVolumeNode=outputVolume,
                          outputTransformNode = outputTransform, fixedVolumeMaskNode = fixedVolumeMask, movingVolumeMaskNode = movingVolumeMask)

    self.delayDisplay('Volumes Registered!')
    
    
  def rigidVolumeRegistration(self, fixedVolume, movingVolume, movingBinaryVolume = None, fixedBinaryVolume = None, Rigid = True, RigidScale = False):
    parameters = {}
    brainsFit = slicer.modules.brainsfit
    parameters['fixedVolume'] = fixedVolume.GetID()
    parameters ['movingVolume'] = movingVolume.GetID()
   # parameters["initialTransform"] = initialTransform.GetID()
    parameters["useRigid"] = Rigid
    parameters["useRigid"] = RigidScale
    parameters["useScaleVersor3D"] = True 
    
    outputTransform = slicer.vtkMRMLLinearTransformNode()
    outputTransform.SetName('PreopToIntraopAutoRegTransform')
    slicer.mrmlScene.AddNode(outputTransform)
    parameters ["outputTransform"] = outputTransform.GetID()
    parameters['fixedBinaryVolume'] = fixedBinaryVolume
    parameters['movingBinaryVolume'] = movingBinaryVolume
    
    cliBrainsFitNode = slicer.cli.run(brainsFit, None, parameters)
    waitCount = 0
    while cliBrainsFitNode.GetStatusString() != 'Completed':
      print( "Performing Deformable Registration... %d" % waitCount )
        #print cliBrainsFitNode.GetStatusString()
      waitCount += 1
    print("Automatic Rigid Registration Completed.")
    

  def makeLabel(self, inputVolume):
    # returns label
    labelName = inputVolume.GetName() + '_label'
    vl = slicer.modules.volumes.logic()
    vl.CreateLabelVolume(inputVolume, labelName)
    volumeLabel = slicer.util.getNode(labelName)

    return volumeLabel

 
