import os
import unittest
import vtk, qt, ctk, slicer, time
from slicer.ScriptedLoadableModule import *
import logging

#
# TreatmentVisualization
#

class Visualization(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Visualization"
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
# TreatmentVisualizationWidget
#

class VisualizationWidget(ScriptedLoadableModuleWidget):

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)
    
    self.logic = VisualizationLogic()
    self.watchDog = None
    self.trackedToolTipTransform = None

    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    
    
    # watch dog stuff 
    
    watchDogCollapsibleButton = ctk.ctkCollapsibleButton()
    watchDogCollapsibleButton.text = "Tracked Instruments"
    watchDogCollapsibleButton.collapsed = True 
    self.layout.addWidget(watchDogCollapsibleButton)
    watchDogCollapsibleButton.connect("clicked(bool)", self.onWatchDogCollapsibleButton)
    watchDogFormLayout = qt.QFormLayout(watchDogCollapsibleButton)
    

    self.table = qt.QTableWidget()
    self.table.setColumnCount(2)
    header = ['Name', 'Status']
    self.table.setHorizontalHeaderLabels(header)
    watchDogFormLayout.addWidget(self.table)
    
    visualizationCollapsibleButton = ctk.ctkCollapsibleButton()
    visualizationCollapsibleButton.text = "Visualization Tools"
    visualizationCollapsibleButton.collapsed = True
    self.layout.addWidget(visualizationCollapsibleButton)
    visualizationFormLayout = qt.QFormLayout(visualizationCollapsibleButton)
    
    
    
    # input tool model selector
    #
    self.inputSelector = slicer.qMRMLNodeComboBox()
    self.inputSelector.nodeTypes = ["vtkMRMLModelNode"]
    self.inputSelector.selectNodeUponCreation = False
    self.inputSelector.addEnabled = False
    self.inputSelector.removeEnabled = False
    self.inputSelector.noneEnabled = True
    self.inputSelector.showHidden = False
    self.inputSelector.showChildNodeTypes = False
    self.inputSelector.renameEnabled = False
    self.inputSelector.setMRMLScene( slicer.mrmlScene )
    self.inputSelector.setToolTip( "The currently navigated tool" )
    visualizationFormLayout.addRow("Tracking Tool: ", self.inputSelector)
    # connection
    self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onToolNavigated)
    
    self.toolViewCheckBox = qt.QCheckBox()
    self.toolViewCheckBox.checked = 0
    self.toolViewCheckBox.setToolTip("If checked, the views will track the tip of the tool selected")
    self.toolViewCheckBox.connect('stateChanged(int)', self.onToolViewCheckBox)
    visualizationFormLayout.addRow("Attach views to tool tip", self.toolViewCheckBox)
    
    self.toolErrorCheckBox = qt.QCheckBox()
    self.toolErrorCheckBox.checked = 0
    self.toolErrorCheckBox.setToolTip("If checked, the show error cone")
    self.toolErrorCheckBox.connect('stateChanged(int)', self.onToolErrorCheckBox)
    visualizationFormLayout.addRow("Show the Error cone", self.toolErrorCheckBox)
   
    
    #
    self.screenShotButton = qt.QPushButton("Take Screenshot")
    self.screenShotButton.toolTip = "Takes screenshot of the procedure display and saves the image in the ?? folder."
    self.screenShotButton.enabled = True
    visualizationFormLayout.addRow(self.screenShotButton)

    # connections
    self.screenShotButton.connect('clicked(bool)', self.onScreenShotButton)
    
    

    
    
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "RFA Generator Parameters"
    parametersCollapsibleButton.collapsed = True
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # input time 
    self.rfaTime = qt.QSpinBox()
    self.rfaTime.minimum = 0
    self.rfaTime.maximum = 900
    self.rfaTime.suffix = 's'
    self.rfaTime.setValue(900)
    parametersFormLayout.addRow("Input Ablation Time: ", self.rfaTime)

    #
    # output volume selector
    #
    self.rfaPower = qt.QSpinBox()
    self.rfaPower.minimum = -1
    self.rfaPower.maximum = 15
    self.rfaPower.suffix = 'W'
    self.rfaPower.setValue(5)
    parametersFormLayout.addRow("RFA Power: ", self.rfaPower)

   
    self.ablationButton = qt.QPushButton("Start Ablation")
    self.ablationButton.toolTip = "Ablation timer countdown"
    self.ablationButton.enabled = True
    parametersFormLayout.addRow(self.ablationButton)

    # connections
    self.ablationButton.connect('clicked(bool)', self.onStartAblation)
    
    self.qLabel=qt.QLabel('') 
    self.layout.addWidget(self.qLabel)
    
   
   

    # Add vertical spacer
    self.layout.addStretch(1)

  #
  #   Connection Functions
  #

  def onWatchDogCollapsibleButton(self):
    if self.watchDog == None:
      self.watchDog = slicer.vtkMRMLWatchdogNode()
      self.watchDog.SetName('RFNavigationToolWatcher')
      slicer.mrmlScene.AddNode(self.watchDog)
    igtConnections = slicer.mrmlScene.GetNodesByClass('vtkMRMLIGTLConnectorNode')
    
    for i in range(igtConnections.GetNumberOfItems()):
      if igtConnections.GetItemAsObject(i).GetState() == 2:
        row  = 0 
        for j in range (igtConnections.GetItemAsObject(i).GetNumberOfIncomingMRMLNodes()):
          if "Reference" in igtConnections.GetItemAsObject(i).GetIncomingMRMLNode(j).GetName():
            self.watchDog.AddWatchedNode(igtConnections.GetItemAsObject(i).GetIncomingMRMLNode(j))
            self.watchDog.SetWatchedNodePlaySound(row,True)
            self.table.insertRow(row)
            self.table.setItem(row, 0, qt.QTableWidgetItem(igtConnections.GetItemAsObject(i).GetIncomingMRMLNode(j).GetName() ))
            if self.watchDog.GetWatchedNodeUpToDate(row):
              self.table.setItem(row, 1, qt.QTableWidgetItem('Tool currently in View'))
            else: 
              self.table.setItem(row, 1, qt.QTableWidgetItem('Tool currently NOT in View'))

            tag = self.watchDog.GetWatchedNode(row).AddObserver(vtk.vtkCommand.ModifiedEvent, self.onWatchDogStatusChange)
            row = row + 1
      else:
        pass

  
  
  
  def onWatchDogStatusChange(self, observer, eventId):

    for dog in range(self.watchDog.GetNumberOfWatchedNodes()):
      if self.watchDog.GetWatchedNodeUpToDate(dog):
        self.table.setItem(dog, 1, qt.QTableWidgetItem('Tool currently in View'))
      else: 
        self.table.setItem(dog, 1, qt.QTableWidgetItem('Tool currently NOT in View'))
      dog += 1
      
    
  
  def onToolNavigated(self):
    pass
  
  
  def onToolViewCheckBox(self):
    if self.toolViewCheckBox.checked == 1:
      if self.inputSelector.currentNode() != None:
        transforms = slicer.mrmlScene.GetNodesByClass('vtkMRMLLinearTransformNode')
        for i in range (0, len(transforms)):
          if self.inputSelector.currentNode().GetName() in transforms[i].GetName() and "Tip" in transforms[i].GetName():
            self.trackedToolTipTransform = transforms[i]
            self.updateSliceView()
            
            
            
  def updateSliceView(self):
    probeToWorldTransformMatrix = vtk.vtkMatrix4x4()
    self.trackedToolTipTransform.GetMatrixTransformToWorld(probeToWorldTransformMatrix)
    yellowSlice = slicer.app.layoutManager().sliceWidget("Yellow")
    yellowController = yellowSlice.sliceController()
    yellowController.setSliceOffsetValue(probeToWorldTransformMatrix.GetElement(0,3))

    greenSlice = slicer.app.layoutManager().sliceWidget("Green")
    greenController = greenSlice.sliceController()
    greenController.setSliceOffsetValue(probeToWorldTransformMatrix.GetElement(1, 3))

    redSlice = slicer.app.layoutManager().sliceWidget("Red")
    redController = redSlice.sliceController()
    redController.setSliceOffsetValue(probeToWorldTransformMatrix.GetElement(2, 3))

    slicer.app.layoutManager().threeDWidget(0).threeDView().resetFocalPoint()
    slicer.app.layoutManager().threeDWidget(0).threeDView().resetCamera()
            
        
      
  def onToolErrorCheckBox(self):
    pass
    
  
  def onScreenShotButton(self):
    pass
  
  def onStartAblation(self):
    n = 0 
    while n < self.rfaTime:
      self.qLabel=qt.QLabel('The ablation seconds completed are: {}'.format(n))
      self.layout.update()
      time.sleep(1)
      n += 1

#
# TreatmentVisualizationLogic
#

class VisualizationLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

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

  


class VisualizationTest(ScriptedLoadableModuleTest):
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
    self.test_TreatmentVisualization1()

  def test_TreatmentVisualization1(self):
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
    logic = TreatmentVisualizationLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
