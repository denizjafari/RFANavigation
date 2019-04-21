needleTipToNeedle = slicer.vtkMRMLLinearTransformNode()
>>> needleTipToNeedle.SetName("NeedleTipToNeedle")
>>>

>>> needleTipToNeedle
(vtkCommonCorePython.vtkMRMLLinearTransformNode)0000028924D93348

>>> slicer.mrmlScene.AddNode(needleTipToNeedle)
(vtkCommonCorePython.vtkMRMLLinearTransformNode)0000028924D93348
>>> slicer.util.getNode('NeedleTipToNeedle')
(vtkCommonCorePython.vtkMRMLLinearTransformNode)0000028924D93348

>>> slicer.util.getNode('NeedleTipToNeedle')
(vtkCommonCorePython.vtkMRMLLinearTransformNode)0000028924D93348
>>> slicer.util.getNode('NeedleModel')
(vtkCommonCorePython.vtkMRMLModelNode)0000028924D93E88

>>> slicer.util.getNode('NeedleModel').GetDisplayNode().SliceIntersectionVisibilityOn()
>>> slicer.util.getNode('NeedleModel').SetAndObserveTransformNodeID(slicer.util.getNode('NeedleTipToNeedle').GetID())
True
>>>


self.needleModel_NeedleTip = slicer.util.getNode('NeedleModel')
    if not self.needleModel_NeedleTip:
      slicer.modules.createmodels.logic().CreateNeedle(80, 1.0, 2.5, 0)
      self.needleModel_NeedleTip = slicer.util.getNode(pattern = "NeedleModel")
      self.needleModel_NeedleTip.GetDisplayNode().SetColor(0.333333, 1.0, 1.0)
      self.needleModel_NeedleTip.SetName("NeedleModel")
      self.needleModel_NeedleTip.GetDisplayNode().SliceIntersectionVisibilityOn()





>>> marks = slicer.modules.markups
>>> marks = slicer.modules.markups.createNewWidgetRepresentation()
>>> marks.children(0
... )
Traceback (most recent call last):
  File "<console>", line 1, in <module>
ValueError: Could not find matching overload for given arguments:
(0,)
 The following slots are available:
children() -> QList<QObject*>
children() -> QList<QObject*>

>>> marks.children()
(QVBoxLayout (QVBoxLayout at: 0x0000023123845350), QLabel (QLabel at: 0x0000023123846100), qMRMLNodeComboBox (qMRMLNodeComboBox at: 0x00000231238335B0), qMRMLNodeComboBoxMenuDelegate (qMRMLNodeComboBoxMenuDelegate at: 0x00000231237EC9F0), QLabel (QLabel at: 0x0000023123847210), ctkSliderWidget (ctkSliderWidget at: 0x0000023123833570), QPushButton (QPushButton at: 0x0000023123847390), QPushButton (QPushButton at: 0x0000023123847270), QGroupBox (QGroupBox at: 0x0000023123846BB0), ctkMenuButton (ctkMenuButton at: 0x00000231238351F0), ctkMenuButton (ctkMenuButton at: 0x0000023123835FB0), ctkMenuButton (ctkMenuButton at: 0x00000231238358F0), QPushButton (QPushButton at: 0x00000231238478D0), QPushButton (QPushButton at: 0x0000023123847F60), QCheckBox (QCheckBox at: 0x0000023123847DB0), QCheckBox (QCheckBox at: 0x0000023123847DE0), QTableWidget (QTableWidget at: 0x00000231238472A0), ctkCollapsibleGroupBox (ctkCollapsibleGroupBox at: 0x00000231238352F0))
>>> combo = marks.children(2)
Traceback (most recent call last):
  File "<console>", line 1, in <module>
ValueError: Could not find matching overload for given arguments:
(2,)
 The following slots are available:
children() -> QList<QObject*>
children() -> QList<QObject*>

>>> combo = marks.children()[2]
>>> combo
qMRMLNodeComboBox (qMRMLNodeComboBox at: 0x00000231238335B0)
>>> combo.currentNode()
(vtkCommonCorePython.vtkMRMLMarkupsFiducialNode)0000023122A764C8
>>> combo.currentNode().GetNumberOfFiducials()
2
>>>
>>> combo.currentNode()
(vtkCommonCorePython.vtkMRMLMarkupsFiducialNode)0000023122A764C8
>>> combo.currentNode().GetNumberOfFiducials()
2
>>> marks.show()
>>> combo.setCurrentNode('MarkupsFiducial_7')
Traceback (most recent call last):
  File "<console>", line 1, in <module>
TypeError: method requires a VTK object
>>> combo.setCurrentNode(getNode('MarkupsFiducial_7'))
>>> combo.currentNode()
(vtkCommonCorePython.vtkMRMLMarkupsFiducialNode)0000023122BE4708
>>> combo.currentNode().GetNumberOfFiducials()
