import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# RFANavWorkflow
#

class RFANavWorkflow(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "RFANavWorkflow" # TODO make this more human readable by adding spaces
    self.parent.categories = ["RFANav"]
    self.parent.dependencies = []
    self.parent.contributors = ["Deniz J (SRI)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
Spinal Metastases RFA procedure navigation workflow - MHSc Thesis
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
""" # replace with organization, grant and thanks.

#
# RFANavWorkflowWidget
#

class RFANavWorkflowWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

 
  def setup(self):
   # self.developerMode = False
   

    ScriptedLoadableModuleWidget.setup(self)
    # Instantiate and connect widgets ...
    
    
    # Tab part of UI
    self.tabWidget = qt.QTabWidget()
    self.layout.addWidget(self.tabWidget)
    self.qWidget1 = qt.QWidget()
    self.qWidget2 = qt.QWidget()
    self.qWidget3 = qt.QWidget()
    self.qWidget4 = qt.QWidget()
    
    
    self.tabWidget.addTab(self.qWidget1, "Load Preop Data")
    self.tabWidget.addTab(self.qWidget2, "Instruments Calibration")
    self.tabWidget.addTab(self.qWidget3, "Inraop Registration")
    self.tabWidget.addTab(self.qWidget4, "Navigation")
    
    self.layout1= qt.QFormLayout(self.qWidget1)
    self.layout2= qt.QFormLayout(self.qWidget2)
    self.layout3= qt.QFormLayout(self.qWidget3)
    self.layout4= qt.QFormLayout(self.qWidget4)
     
    
    self.tabWidget.connect('currentChanged(int)', self.onTabChanged)

  
    
    # Adding load data module to tab 1 
    self.loadDataWidget = slicer.modules.loaddata.widgetRepresentation() 
    self.layout1.addWidget(self.loadDataWidget)
    
    
    # Adding Tracking module 
    self.trackingSetupWidget = slicer.modules.trackingsetup.widgetRepresentation() 
    self.layout2.addWidget(self.trackingSetupWidget)
   
    # Adding Registration module 
    self.registrationWidget = slicer.modules.registration.widgetRepresentation()
    self.layout3.addWidget(self.registrationWidget)
  
    # adding Visualization module 
    self.visualizationWidget = slicer.modules.visualization.widgetRepresentation() 
    self.layout4.addWidget(self.visualizationWidget)
  

  ''' how tabs are updated'''

  def onTabChanged(self):
    currentTab = self.tabWidget.currentIndex
    if currentTab == 0:  # Load Data
      slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)
    
    elif currentTab == 1:  # Tracking Setup
      Volumes = slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode")
      
    elif currentTab == 2:  # Registration
      
      Volumes = slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode")
  '''  if 0:
      elif currentTab == 1:
      #self.trackedParametersModule.setUSCalibrationModule(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)
      elif currentTab == 2:
        self.modelGenerationModule.setToBeTransformedItems(self.igtConnectionModule.getToBeTransformedItems())
      elif currentTab == 3:
        self.patientRegistrationModule.setToBeTransformedItems(self.modelGenerationModule.getToBeTransformedItems())
      elif currentTab == 4:
        self.usCalibrationModule.setUsImage(self.trackedParametersModule.getUsImage())
        self.usCalibrationModule.setPatientVolume(self.igtConnectionModule.getPatientVolume())
    
    
    if 0:  
        models = slicer.mrmlScene.GetNodesByClass('vtkMRMLModelNode')
        numberOfModels = models.GetNumberOfItems()
        latestModel = models.GetItemAsObject(numberOfModels - 1)
    
        currentTab = self.tab1.currentIndex
    
        if currentTab == 0:  
          self.lm.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)
        elif currentTab == 1:  # Registration
          self.lm.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpQuantitativeView)
          # self.ePsfCast.volumeSelector.setCurrentNode(self.ePSFUpdatedInputVolume)
        elif currentTab == 2:  # Tracking Setup
          self.lm.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)
          self.trackCast.inputVolumeSelector.setCurrentNode(self.activeVolume)
          self.svCast.volumeMetadataSelector.setCurrentNode(self.activeVolume)
        else:  # Visualization
          self.lm.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)
'''

  
class RFANavWorkflowLogic(ScriptedLoadableModuleLogic):
    
    def run():
        pass
    
    
    

class RFANavWorkflowTest(ScriptedLoadableModuleTest):
   

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)