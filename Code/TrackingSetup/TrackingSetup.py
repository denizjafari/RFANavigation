import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# ToolTracking
#

class TrackingSetup(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "TrackingSetup" # TODO make this more human readable by adding spaces
    self.parent.categories = ["RFANav"]
    self.parent.dependencies = []
    self.parent.contributors = ["Deniz J (SRI)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
It performs a simple thresholding on the input volume and optionally captures a screenshot.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
Spinal Metastases RFA procedure navigation workflow - MHSc Thesis
""" # replace with organization, grant and thanks.

#
# ToolTrackingWidget
#

class TrackingSetupWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)
    self.logic = TrackingSetupLogic()

    # Instantiate and connect widgets ...


 # intra-op

    opticalTrackerCollapsibleButton = ctk.ctkCollapsibleButton()
    opticalTrackerCollapsibleButton.text = "Connection to Motive"
    self.layout.addWidget(opticalTrackerCollapsibleButton)
    opticalTrackerFormLayout = qt.QFormLayout(opticalTrackerCollapsibleButton)
    
    
    self.openIGTWidget = slicer.modules.openigtlinkif.widgetRepresentation()
    self.openIGTWidget.children()[2].children()[2].hide()
    
    opticalTrackerFormLayout.addWidget(self.openIGTWidget)
    
 

    
    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Tool Selection and Calibration"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)


    # The name of the tool to be inserted to the scene
    # has to include different probe sizes and other guided tools, needles in various gages
    nText = qt.QLabel("The tool to be inserted: ")
    self.tools = qt.QComboBox()
    self.Ttools = ('Introducer_1', 'RFAProbe_1', 'Introducer_2', 'RFAProbe_2', 'Stylus', 'Other')
    self.tools.addItems(self.Ttools)
    parametersFormLayout.addRow(nText, self.tools)
    self.tools.connect("currentNodeChanged(vtkMRMLNode*)", self.onChoosingTool)
    
    # Add New Needle model if needed 
    self.AddModelButton = qt.QPushButton("Add New Tool Model")
    self.AddModelButton.toolTip = "New Tool Model is added to the scene."
    self.AddModelButton.enabled = True
    parametersFormLayout.addRow(self.AddModelButton)
    # connection
    self.AddModelButton.connect('clicked(bool)', self.onAddModelButton)
   
    
    # input tool model selector
    #
    self.inputSelector = slicer.qMRMLNodeComboBox()
    self.inputSelector.nodeTypes = ["vtkMRMLModelNode"]
    self.inputSelector.selectNodeUponCreation = True
    self.inputSelector.addEnabled = False
    self.inputSelector.removeEnabled = True
    self.inputSelector.noneEnabled = False
    self.inputSelector.showHidden = False
    self.inputSelector.showChildNodeTypes = False
    self.inputSelector.renameEnabled = True
    self.inputSelector.setMRMLScene( slicer.mrmlScene )
    self.inputSelector.setToolTip( "The tool to be calibrated" )
    parametersFormLayout.addRow("Input Model: ", self.inputSelector)
    # connection
    self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onEnableTransform)
    #self.inputSelector.connect("nodeAddedByUser(vtkMRMLNode*)", self.onNewModel)
    
    #
    # Pivot Calibration 
    #
    pCalWidget = slicer.modules.pivotcalibration.createNewWidgetRepresentation()
    parametersFormLayout.addRow(pCalWidget)
    
    self.IO = pCalWidget.children()[1]
    self.IO.collapsed = True
    # they are qMRMLNodeComboBox with nodeTypes = ["vtkMRMLLinearTransformNode"]
    self.inputtransformSelector = self.IO.children()[2]
    self.inputtransformSelector.selectNodeUponCreation = False
    self.outputtransformSelector = self.IO.children()[5]
    
    

    #self.tools.connect("currentNodeChanged(vtkMRMLNode*)", self.onToolSelect)
    
    self.inputtransformSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onInputTransformSelect)
     # when this button is pressed, connection to Stealth is made

    
    
    
    
    #self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onToolSelect)
   # self.transformSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)
    
    self.connectToMotive('fusion' , 18944)

    # Refresh Apply button state
    #self.onSelect()
    
  # IGT connection to Motive
  def connectToMotive(self, host, port):

    # QLineEdit has input validation methods that can be implemented here for more robustness
    try:
      connectorNode = slicer.vtkMRMLIGTLConnectorNode()
      connectorNode.SetTypeClient(host, int(port))
      slicer.mrmlScene.AddNode(connectorNode)
      connectorNode.Start()
      

    except:
      slicer.util.errorDisplay("Unexpected hostname or port number")
    
    self.connection = slicer.mrmlScene.GetNodeByID('vtkMRMLIGTLConnectorNode1')
    status = self.connection.GetState()

    if status == 0:
      slicer.util.errorDisplay("Connection to Motive Optical Tracker is off.")
    elif status == 1:
      slicer.util.errorDisplay("run the PlusServer.")
    elif status == 2:
      print("Successfully connected to Motive Optical Tracker")

    else:
      slicer.util.errorDisplay("unexpected error connecting to Motive Optical Tracker")
      
      
  
  def onChoosingTool(self):
    self.outputtransformSelector.enabled = False

  def onAddModelButton(self):
    #self.toolmodel = slicer.vtkMRMLModelNode()
    
    self.toolName = self.tools.currentText
    self.toolmodel = self.logic.createNeedleModel (self.toolName)
    self.inputSelector.setCurrentNodeID(self.toolmodel.GetID())
    

  def onEnableTransform(self):
    self.IO.collapsed = False
    self.inputtransformSelector.enabled = self.inputSelector.currentNode()
    
      
    #print  self.inputSelector.currentNode()
  #  self.currentModel = self.inputSelector.currentNode()
    
    
    
   # currentModelCreated = 
    
  def onInputTransformSelect(self):
    self.TipTransform = slicer.vtkMRMLLinearTransformNode()
    newName = self.inputtransformSelector.currentNode().GetName().rstrip('ToReference')
    self.TipTransform.SetName(newName +'TipTo' + newName)
    slicer.mrmlScene.AddNode(self.TipTransform)
    self.outputtransformSelector.setCurrentNodeID(self.TipTransform.GetID())
    self.inputSelector.currentNode().SetAndObserveTransformNodeID(self.TipTransform.GetID())
    self.TipTransform.SetAndObserveTransformNodeID(self.inputtransformSelector.currentNode().GetID())
    
    

  def cleanup(self):
    pass

  def onMotiveButton(self):
    self.logic.connectToMotive('fusion' , 18944)
    

  

 # load the model of the requested tool name
  def onToolSelect(self):
      
    self.AddModelButton.enabled = True

    if 0:
      toolname = self.tools.currentText
      if toolname == 'RFAProbe':
        toolpath = "C:\Users\Deniz\Documents\RFNavigation\RFNavigation\RFANavToolModels\\"  + toolname + ".ply"
      # toolpath = 'C:\Users\Deniz\Documents\RFNavigation\RFNavigation\RFANavToolModels\RFAProbe.ply'
      # load the requested the model onto the scene as well as the input selector
      slicer.util.loadModel(toolpath, returnNode=True)
      # self.inputSelector.setCurrentNode()
     
        
#
# ToolTrackingLogic
#

class TrackingSetupLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
  
      
  # create a new needle model for new tool added
  def createNeedleModel (self, toolname):
    
    modelNode = slicer.vtkMRMLModelNode()
    # create needle model module logic  
    createModelLogic = slicer.modules.createmodels.logic()
    #modelDisplayNode = slicer.vtkMRMLModelDisplayNode()
    #modelDisplayNode.SetName(modelNode.GetName())
    
    # create a RFA probe needle
    if 'RFAProbe' in toolname:
      modelNode = createModelLogic.CreateNeedle(150,True, 0,1)  
      modelNode.SetName(toolname)
      modelDisplayNode = modelNode.GetDisplayNode()
      modelDisplayNode.SetColor([0,0,1]) # Blue
     # slicer.mrmlScene.AddNode(modelDisplayNode)
     # modelNode.SetAndObserveDisplayNodeID(modelDisplayNode.GetID())
      
    elif 'Introducer' in toolname:
      modelNode = createModelLogic.CreateNeedle(100,True, 0,1)
      modelNode.SetName(toolname)
      modelDisplayNode = modelNode.GetDisplayNode()
      modelDisplayNode.SetColor([1,0,0]) # Red
     # slicer.mrmlScene.AddNode(modelDisplayNode)
     # modelNode.SetAndObserveDisplayNodeID(modelDisplayNode.GetID())
      
    else:  
      modelNode = createModelLogic.CreateNeedle(100,True, 1,1)
      modelNode.SetName(toolname)
      modelDisplayNode = modelNode.GetDisplayNode()
      modelDisplayNode.SetColor([0,1,0])
    
    return modelNode
 
           
  


class TrackingSetupTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)
