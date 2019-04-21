import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# TreatmentMaker
#

class TreatmentMaker(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "TreatmentMaker" # TODO make this more human readable by adding spaces
    self.parent.categories = [""]
    self.parent.dependencies = []
    self.parent.contributors = ["DJ (SRI)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
It performs a simple thresholding on the input volume and optionally captures a screenshot.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# TreatmentMakerWidget
#

class TreatmentMakerWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    ##### load dicom data #####

    loaddataCollapsibleButton = ctk.ctkCollapsibleButton()
    loaddataCollapsibleButton.text = "Load DICOM Data"
    loaddataCollapsibleButton.collapsed = True
    self.layout.addWidget(loaddataCollapsibleButton)
    loaddataFormLayout = qt.QFormLayout(loaddataCollapsibleButton)
    dicommodule = slicer.modules.dicom.createNewWidgetRepresentation()
    dicomchildren = dicommodule.children()
    dicomchildren[1].collapsed = True
    dicomchildren[3].hide()
    loaddataFormLayout.addWidget(dicommodule)
    	
	
	##### Spine Model #####
	
    spineCollapsibleButton = ctk.ctkCollapsibleButton()
    spineCollapsibleButton.text = "Spine Model"
    spineCollapsibleButton.collapsed = True
    self.layout.addWidget (spineCollapsibleButton)
    spineFormLayout = qt.QFormLayout(spineCollapsibleButton)
	
	
    ##### input volume selector #####
    
    self.inputSelector = slicer.qMRMLNodeComboBox()
    self.inputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.inputSelector.selectNodeUponCreation = True
    self.inputSelector.addEnabled = False
    self.inputSelector.removeEnabled = False
    self.inputSelector.noneEnabled = False
    self.inputSelector.showHidden = False
    self.inputSelector.showChildNodeTypes = False
    self.inputSelector.setMRMLScene( slicer.mrmlScene )
    self.inputSelector.setToolTip( "Pick the input to the algorithm." )
    spineFormLayout.addRow("Input Volume: ", self.inputSelector)
	
	##### Thresholding #####
	
	## I want to write my own code instead of using a module and hiding all of it
	## except the fuctionality that I want 
	
    editormodule = slicer.modules.editor.createNewWidgetRepresentation()
    toolbox = editormodule.findChildren('QToolButton')
    editorchildren = editormodule.children()
    editorchildren[1].hide()
    editorchildren[2].hide()
    [toolbox[i].hide() for i in range(0,19) if i != 15]
    spineFormLayout.addWidget(editormodule)
			
			## using something like this

		   # self.imageThresholdSliderWidget = ctk.ctkDoubleRangeSlider()
		   # self.imageThresholdSliderWidget.orientation = 1
		   # self.imageThresholdSliderWidget.setMinimumValue(-1000)
		   # self.imageThresholdSliderWidget.setMaximumValue(3000)
		   # self.imageThresholdSliderWidget.minimum = -1000
		   # self.imageThresholdSliderWidget.maximum = 3000
		   # spineFormLayout.addRow("Image threshold", self.imageThresholdSliderWidget)
			
			#
			# Apply Threshold Button
			#
		   # self.applythresholdButton = qt.QPushButton("Apply Threshold")
		   # self.applythresholdButton.toolTip = "Run the algorithm."
		   # self.applythresholdButton.enabled = False
		   # spineFormLayout.addRow(self.applythresholdButton)
			
	
	
    ##### Volume Crop #####

    cropvolumemodule = slicer.modules.cropvolume.createNewWidgetRepresentation()
    cropvolumechildren = cropvolumemodule.children()
    #cropvolumechildren[3].hide()
    cropvolumechildren[4].hide()
    cropvolumechildren[5].hide()
    cropvolumechildren[6].hide()
    spineFormLayout.addWidget(cropvolumemodule)
	
	#
    # Crop Button
    #
  #  self.cropButton = qt.QPushButton("Crop Volume")
  #  self.cropButton.toolTip = "Run the algorithm."
  #  self.cropButton.enabled = False
  #  spineFormLayout.addRow(self.cropButton)
	
	##### Model Maker #####
    
    modelmakermodule = slicer.modules.modelmaker.createNewWidgetRepresentation()
    modelmakerchildren = modelmakermodule.children()
    modelmakerchildren[2].setMinimumHeight(350)
    modelmakerchildren[4].hide()
    modelmakerchildren[5].hide()
    modelmakerchildren[6].hide()
    spineFormLayout.addRow(modelmakermodule)
	
	############################
	
	#Tumour Segmentation 
	
    tumorsegmentCollapsibleButton = ctk.ctkCollapsibleButton()
    tumorsegmentCollapsibleButton.text = "Tumour Segmentation"
    tumorsegmentCollapsibleButton.collapsed = True
    self.layout.addWidget (tumorsegmentCollapsibleButton)
    tumorsegmentFormLayout = qt.QFormLayout(tumorsegmentCollapsibleButton)
    segmenteditormodule = slicer.modules.segmenteditor.createNewWidgetRepresentation()
    seditorchildren = segmenteditormodule.children()
    seditorchildren[1].hide()
    #m = seditorchildren[2]
    #morechildren = m.children() 
    tumorsegmentFormLayout.addWidget(segmenteditormodule)
    segmentationmodule = slicer.modules.segmentations.createNewWidgetRepresentation()
    segmentchildren = segmentationmodule.children()
    segmentchildren[1].hide()
    segmentchildren[2].hide()
    segmentchildren[3].hide()
    #segmentchildren[4].hide()
    segmentchildren[5].hide()
    segmentchildren[6].hide()
    segmentchildren[7].hide()
    segmentchildren[8].hide()
    segmentchildren[9].hide()
    tumorsegmentFormLayout.addWidget(segmentationmodule)
    #####################################
	
    # Insert Probe models
  
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "RF Probe Insertion"
    parametersCollapsibleButton.collapsed = True
    self.layout.addWidget(parametersCollapsibleButton)
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)
	
    self.addprobe1Button = qt.QPushButton("Add RF Probe 1")
    self.addprobe1Button.toolTip = "Add RF probe model to the slicer scene."
    self.addprobe1Button.enabled = True
    parametersFormLayout.addRow(self.addprobe1Button)
	
    self.addprobe2Button = qt.QPushButton("Add RF Probe 2")
    self.addprobe2Button.toolTip = "Add RF probe model to the slicer scene."
    self.addprobe2Button.enabled = True
    parametersFormLayout.addRow(self.addprobe2Button)
	
 #   [success, probmodel_1] = slicer.util.loadModel('C:\Users\Deniz\Documents\RFNavigation\Probe_removed_casing_Binary_noWire.ply', returnNode=True)
 #   [success_2, probmodel_2] = slicer.util.loadModel('C:\Users\Deniz\Documents\RFNavigation\Probe_removed_casing_Binary_noWire.ply', returnNode=True)
	

   
    
    # output volume selector
    #
    self.outputSelector = slicer.qMRMLNodeComboBox()
    self.outputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.outputSelector.selectNodeUponCreation = True
    self.outputSelector.addEnabled = True
    self.outputSelector.removeEnabled = True
    self.outputSelector.noneEnabled = True
    self.outputSelector.showHidden = False
    self.outputSelector.showChildNodeTypes = False
    self.outputSelector.setMRMLScene( slicer.mrmlScene )
 #   self.outputSelector.setToolTip( "Pick the output to the algorithm." )
 #   parametersFormLayout.addRow("Output Volume: ", self.outputSelector)
	
	
    transformmodule = slicer.modules.transforms.createNewWidgetRepresentation()
    #transformchildren = transformmodule.children()
    parametersFormLayout.addWidget(transformmodule)
	

   

						#
						# check box to trigger taking screen shots for later use in tutorials
						#
					 #   self.enableScreenshotsFlagCheckBox = qt.QCheckBox()
					 #   self.enableScreenshotsFlagCheckBox.checked = 0
					 #   self.enableScreenshotsFlagCheckBox.setToolTip("If checked, take screen shots for tutorials. Use Save Data to write them to disk.")
					 #   parametersFormLayout.addRow("Enable Screenshots", self.enableScreenshotsFlagCheckBox)

	
	
    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = False
    parametersFormLayout.addRow(self.applyButton)

    # connections
	
   # self.applythresholdButton.connect('clicked(bool)', self.onApplyThresholdButton)
   # self.cropButton.connect('clicked(bool)', self.onCropButton)
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.addprobe1Button.connect('clicked(bool)', self.onAddprobe1Button)
    self.addprobe2Button.connect('clicked(bool)', self.onAddprobe2Button)
    self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()

  def cleanup(self):
    pass

  def onSelect(self):
		  #  self.applythresholdButton.enabled = self.inputSelector.currentNode() 
    self.applyButton.enabled = self.inputSelector.currentNode() 

		  # def onCropButton(self):
		  #   cropVolumelogic = slicer.modules.cropvolume.logic()
		  #  roi = slicer.mrmlScene.GetNodeByID('vtkMRMLAnnotationROINode1')
		  #  cropVolumeNode = slicer.vtkMRMLCropVolumeParametersNode()
		  #  cropVolumeNode.SetInputVolumeNodeID(self.inputSelector.currentNode().GetID())
		  #  cropVolumeNode.SetROINodeID(roi.GetID())
		  #  cropVolumelogic.Apply(cropVolumeNode)
			
	
   
  def onAddprobe1Button(self):
    [success, probmodel_1] = slicer.util.loadModel('C:\Users\Deniz\Documents\RFNavigation\Probe_removed_casing_Binary_noWire.ply', returnNode=True)
    Probe_1_Transformation = slicer.vtkMRMLLinearTransformNode()
    Probe_1_Transformation.ApplyTransform(probmodel_1)
	
  def onAddprobe2Button(self):
    [success_2, probmodel_2] = slicer.util.loadModel('C:\Users\Deniz\Documents\RFNavigation\Probe_removed_casing_Binary_noWire.ply', returnNode=True)
    Probe_2_Transformation = slicer.vtkMRMLLinearTransformNode()
    Probe_2_Transformation.ApplyTransform(probmodel_2)
	
  
  def onApplyButton(self):
    logic = TreatmentMakerLogic()
    enableScreenshotsFlag = self.enableScreenshotsFlagCheckBox.checked
    imageThreshold = self.imageThresholdSliderWidget.value
    logic.run(self.inputSelector.currentNode(), self.outputSelector.currentNode(), imageThreshold, enableScreenshotsFlag)

 # def onApplyThresholdButton(self):
  #  logic = TreatmentMakerLogic()
  # threshold1 = self.imageThresholdSliderWidget.lower()
  #  threshold2 = self.imageThresholdSliderWidget.higher()
  #  logic.thresholdRangeScan(self.inputSelector.currentNode(), threshold1, threshold2, self.outputSelector.currentNode())

  def hideWidgetChild(self, moduleName, xCoordinate, yCoordinate):
    if moduleName.isHidden():
	  moduleName.setVisible(True)
    else:
      pass
    widgetChild = moduleName.childAt(xCoordinate, yCoordinate)
    widgetChild.hide()
#
# TreatmentMakerLogic
#

class TreatmentMakerLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  import SimpleITK as sitk
  import sitkUtils

  
  def thresholdRangeScan(self,inputVolume1, threshold1, threshold2, volumeName):
    #cast = sitk.CastImageFilter()

    inputVolumeName1 = inputVolume1.GetName()
    image1 = sitkUtils.PullFromSlicer(inputVolumeName1)
   
   #image1Cast = cast.Execute(image1)
    #inputVolumeName2 = inputVolume2.GetName()
    #image2 = sitkUtils.PullFromSlicer(inputVolumeName2)
    #image2Cast = cast.Execute(image2)

    thresholdFilter = sitk.ThresholdImageFilter()
    thresholdFilter.SetLower(threshold1)
    thresholdFilter.SetUpper(threshold2)
    thresholdFilter.SetOutsideValue(0)
    thresholdedImage = thresholdFilter.Execute(image1)
    sitkUtils.PushToSlicer(thresholdedImage,volumeName,True)

    thresholdedVolume = slicer.util.getNode(volumeName)

    return thresholdedVolume
  
  def hasImageData(self,volumeNode):
    """This is an example logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      logging.debug('hasImageData failed: no volume node')
      return False
    if volumeNode.GetImageData() is None:
      logging.debug('hasImageData failed: no image data in volume node')
      return False
    return True

  def isValidInputOutputData(self, inputVolumeNode, outputVolumeNode):
    """Validates if the output is not the same as input
    """
    if not inputVolumeNode:
      logging.debug('isValidInputOutputData failed: no input volume node defined')
      return False
    if not outputVolumeNode:
      logging.debug('isValidInputOutputData failed: no output volume node defined')
      return False
    if inputVolumeNode.GetID()==outputVolumeNode.GetID():
      logging.debug('isValidInputOutputData failed: input and output volume is the same. Create a new volume for output to avoid this error.')
      return False
    return True

  def takeScreenshot(self,name,description,type=-1):
    # show the message even if not taking a screen shot
    slicer.util.delayDisplay('Take screenshot: '+description+'.\nResult is available in the Annotations module.', 3000)

    lm = slicer.app.layoutManager()
    # switch on the type to get the requested window
    widget = 0
    if type == slicer.qMRMLScreenShotDialog.FullLayout:
      # full layout
      widget = lm.viewport()
    elif type == slicer.qMRMLScreenShotDialog.ThreeD:
      # just the 3D window
      widget = lm.threeDWidget(0).threeDView()
    elif type == slicer.qMRMLScreenShotDialog.Red:
      # red slice window
      widget = lm.sliceWidget("Red")
    elif type == slicer.qMRMLScreenShotDialog.Yellow:
      # yellow slice window
      widget = lm.sliceWidget("Yellow")
    elif type == slicer.qMRMLScreenShotDialog.Green:
      # green slice window
      widget = lm.sliceWidget("Green")
    else:
      # default to using the full window
      widget = slicer.util.mainWindow()
      # reset the type so that the node is set correctly
      type = slicer.qMRMLScreenShotDialog.FullLayout

    # grab and convert to vtk image data
    qpixMap = qt.QPixmap().grabWidget(widget)
    qimage = qpixMap.toImage()
    imageData = vtk.vtkImageData()
    slicer.qMRMLUtils().qImageToVtkImageData(qimage,imageData)

    annotationLogic = slicer.modules.annotations.logic()
    annotationLogic.CreateSnapShot(name, description, type, 1, imageData)

  def run(self, inputVolume, outputVolume, imageThreshold, enableScreenshots=0):
    """
    Run the actual algorithm
    """

    if not self.isValidInputOutputData(inputVolume, outputVolume):
      slicer.util.errorDisplay('Input volume is the same as output volume. Choose a different output volume.')
      return False

    logging.info('Processing started')

    # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
    cliParams = {'InputVolume': inputVolume.GetID(), 'OutputVolume': outputVolume.GetID(), 'ThresholdValue' : imageThreshold, 'ThresholdType' : 'Above'}
    cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True)

    # Capture screenshot
    if enableScreenshots:
      self.takeScreenshot('TreatmentMakerTest-Start','MyScreenshot',-1)

    logging.info('Processing completed')

    return True


class TreatmentMakerTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_TreatmentMaker1()

  def test_TreatmentMaker1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import urllib
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        logging.info('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        logging.info('Loading %s...' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = TreatmentMakerLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
