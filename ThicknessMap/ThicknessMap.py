import vtk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import SimpleITK as sitk
import sitkUtils
import pandas as pd
from pathlib import Path

#
# ThicknessMap
#

class ThicknessMap(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "ThicknessMap"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["Shape Analysis"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["M. Fatih Talu (Inonu Univ.)"]  # TODO: replace with "Firstname Lastname (Organization)"
    # TODO: update with short description of the module and a link to online module documentation
    self.parent.helpText = """
This module is an extention for 3D Slicer. 
It was implemented to generate Thickness Maps of 3D segments obtained from MRI-CT data. 
First, select a Volume (MRI-CT). Then, using 'Apply Segmentation' button, set a threshold value to determine a segment in the volume. 
Finally, generate the map by clicking the Apply Thickness button.
"""
    # TODO: replace with organization, grant and thanks
    self.parent.acknowledgementText = """
This file was originally developed by Muhammed Fatih Talu, Inonu University, Computer Science Department.
"""
    # Additional initialization step after application startup is complete
    #slicer.app.connect("startupCompleted()", registerSampleData)

#
# ThicknessMapWidget
#

class ThicknessMapWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent=None):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)  # needed for parameter node observation
    self.logic = None
    self._parameterNode = None
    self._updatingGUIFromParameterNode = False

  def setup(self):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.setup(self)

    # Load widget from .ui file (created by Qt Designer).
    # Additional widgets can be instantiated manually and added to self.layout.
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/ThicknessMap.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
    # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
    # "setMRMLScene(vtkMRMLScene*)" slot.
    uiWidget.setMRMLScene(slicer.mrmlScene)

    # Create logic class. Logic implements all computations that should be possible to run
    # in batch mode, without a graphical user interface.
    self.logic = ThicknessMapLogic()

    # Connections

    # These connections ensure that we update parameter node when scene is closed
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

    # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
    # (in the selected parameter node).
    self.ui.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.SegmentationThresholdSliderWidget.connect("valueChanged(double)", self.updateParameterNodeFromGUI)

    # Buttons
    self.ui.ApplySegmentationButton.connect('clicked(bool)', self.onApplySegmentationButton)
    self.ui.ApplyThicknessButton.connect('clicked(bool)', self.onApplyThicknessButton)
    self.ui.ApplyExportButton.connect('clicked(bool)', self.onApplyExportButton)

    # Make sure parameter node is initialized (needed for module reload)
    self.initializeParameterNode()

  def cleanup(self):
    """
    Called when the application closes and the module widget is destroyed.
    """
    self.removeObservers()

  def enter(self):
    """
    Called each time the user opens this module.
    """
    # Make sure parameter node exists and observed
    self.initializeParameterNode()

  def exit(self):
    """
    Called each time the user opens a different module.
    """
    # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
    self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

  def onSceneStartClose(self, caller, event):
    """
    Called just before the scene is closed.
    """
    # Parameter node will be reset, do not use it anymore
    self.setParameterNode(None)

  def onSceneEndClose(self, caller, event):
    """
    Called just after the scene is closed.
    """
    # If this module is shown while the scene is closed then recreate a new parameter node immediately
    if self.parent.isEntered:
      self.initializeParameterNode()

  def initializeParameterNode(self):
    """
    Ensure parameter node exists and observed.
    """
    # Parameter node stores all user choices in parameter values, node selections, etc.
    # so that when the scene is saved and reloaded, these settings are restored.

    self.setParameterNode(self.logic.getParameterNode())

    # Select default input nodes if nothing is selected yet to save a few clicks for the user
    if not self._parameterNode.GetNodeReference("InputVolume"):
      firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
      if firstVolumeNode:
        self._parameterNode.SetNodeReferenceID("InputVolume", firstVolumeNode.GetID())

  def setParameterNode(self, inputParameterNode):
    """
    Set and observe parameter node.
    Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
    """

    if inputParameterNode:
      self.logic.setDefaultParameters(inputParameterNode)

    # Unobserve previously selected parameter node and add an observer to the newly selected.
    # Changes of parameter node are observed so that whenever parameters are changed by a script or any other module
    # those are reflected immediately in the GUI.
    if self._parameterNode is not None:
      self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
    self._parameterNode = inputParameterNode
    if self._parameterNode is not None:
      self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    # Initial GUI update
    self.updateGUIFromParameterNode()

  def updateGUIFromParameterNode(self, caller=None, event=None):
    """
    This method is called whenever parameter node is changed.
    The module GUI is updated to show the current state of the parameter node.
    """

    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)
    self._updatingGUIFromParameterNode = True

    # Update node selectors and sliders
    self.ui.inputSelector.setCurrentNode(self._parameterNode.GetNodeReference("InputVolume"))
    if self._parameterNode.GetParameter("Threshold"):
      self.ui.SegmentationThresholdSliderWidget.value = float(self._parameterNode.GetParameter("Threshold"))

    # All the GUI updates are done
    self._updatingGUIFromParameterNode = False

  def updateParameterNodeFromGUI(self, caller=None, event=None):
    """"""

    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch

    self._parameterNode.SetNodeReferenceID("InputVolume", self.ui.inputSelector.currentNodeID)
    self._parameterNode.SetParameter("Threshold", str(self.ui.SegmentationThresholdSliderWidget.value))

    self._parameterNode.EndModify(wasModified)

  def onApplySegmentationButton(self):
    with slicer.util.tryWithErrorDisplay("Segmentation is failed", waitCursor=True):      
      self.logic.ProcessSegmentation(self.ui.inputSelector.currentNode(), self.ui.SegmentationThresholdSliderWidget.value)

  def onApplyThicknessButton(self):    
    with slicer.util.tryWithErrorDisplay("Thickness Calculation is failed.", waitCursor=True):
      self.logic.ProcessThickness(self.ui.inputSelector.currentNode())

  def onApplyExportButton(self):    
    with slicer.util.tryWithErrorDisplay("Export failed.", waitCursor=True):
      self.logic.ProcessExport()

class ThicknessMapLogic(ScriptedLoadableModuleLogic):
  def __init__(self):
    ScriptedLoadableModuleLogic.__init__(self)

  def setDefaultParameters(self, parameterNode):
    ''''''

  def ProcessSegmentation(self, masterVolumeNode,SegmantationThreshold):
    if not masterVolumeNode:
      print("First, select a volume!")
    else:
      segmentationNode = slicer.mrmlScene.GetFirstNode(None, "vtkMRMLSegmentationNode")
      if not segmentationNode:
          segmentationNode = slicer.vtkMRMLSegmentationNode()
          segmentationNode.SetName("Segmentation")
          slicer.mrmlScene.AddNode(segmentationNode)            

      segmentationNode.CreateDefaultDisplayNodes() # only needed for display
      segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(masterVolumeNode)

      # Create segment editor to get access to effects
      slicer.app.processEvents()
      segmentEditorWidget = slicer.qMRMLSegmentEditorWidget()
      segmentEditorWidget.setMRMLScene(slicer.mrmlScene)

      segmentEditorNode = slicer.vtkMRMLSegmentEditorNode()
      slicer.mrmlScene.AddNode(segmentEditorNode)

      segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
      segmentEditorWidget.setSegmentationNode(segmentationNode)
      segmentEditorWidget.setMasterVolumeNode(masterVolumeNode)

      # if segment is exist
      visibleSegmentIds = vtk.vtkStringArray()
      segmentationNode.GetDisplayNode().GetVisibleSegmentIDs(visibleSegmentIds)
      if visibleSegmentIds.GetNumberOfValues() == 0:      
          SkullSegmentName = segmentationNode.GetSegmentation().AddEmptySegment("Segment")
      else:      
          SkullSegmentName = visibleSegmentIds.GetValue(0)

      ## THRESHOLDING
      slicer.app.processEvents()
      segmentEditorNode.SetSelectedSegmentID(SkullSegmentName)
      segmentEditorWidget.setActiveEffectByName("Threshold")
      effect = segmentEditorWidget.activeEffect()
      effect.setParameter("MinimumThreshold",str(SegmantationThreshold))
      effect.self().onApply()    

      ## KEEP_LARGEST_ISLAND
      slicer.app.processEvents()
      segmentEditorWidget.setActiveEffectByName("Islands")
      effect = segmentEditorWidget.activeEffect()
      effect.setParameterDefault("Operation", "KEEP_LARGEST_ISLAND")
      effect.self().onApply()      

  def ProcessThickness(self, masterVolumeNode):
    segmentationNode = slicer.mrmlScene.GetFirstNode(None, "vtkMRMLSegmentationNode")
    if not segmentationNode and not masterVolumeNode:
      print("First, Select input volume and adjust segmentation threshold!")
    else:      
      # LABELMAP
      segs = vtk.vtkStringArray(); 
      segmentationNode.GetDisplayNode().GetVisibleSegmentIDs(segs)
      labelMapNode = slicer.vtkMRMLLabelMapVolumeNode()
      labelMapNode.SetName("Label")
      slicer.mrmlScene.AddNode(labelMapNode)
      slicer.vtkSlicerSegmentationsModuleLogic.ExportSegmentsToLabelmapNode(segmentationNode, segs, labelMapNode, masterVolumeNode)  

      # Model 
      slicer.modules.segmentations.logic().ExportAllSegmentsToModels(segmentationNode, slicer.mrmlScene.GetSubjectHierarchyNode().GetSceneItemID())
      modelNode = slicer.mrmlScene.GetFirstNodeByName("Segment")
      modelNode.SetName("Model")  

      # BinaryThinningFilter
      ThinLabelNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode", "ThinLabel")      
      inputImage = sitkUtils.PullVolumeFromSlicer(labelMapNode)
      filter = sitk.BinaryThinningImageFilter()
      outputImage = filter.Execute(inputImage)
      sitkUtils.PushVolumeToSlicer(outputImage, ThinLabelNode);   
      
      # DanielssonDistanceMapImageFilter      
      distThinLabelNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode", "DistThinLabel")      
      inputImage = sitkUtils.PullVolumeFromSlicer(ThinLabelNode)
      filter = sitk.DanielssonDistanceMapImageFilter()
      outputImage = filter.Execute(inputImage)
      outputImage = outputImage * 2
      sitkUtils.PushVolumeToSlicer(outputImage, distThinLabelNode)

      ## ProbeVolumeWithModel: Coloring for distance_map with model         
      thicknessNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "ThicknessMap")    
      # Parameters for ProbeVolumeWithModel
      parameters = {}
      parameters["InputVolume"] = distThinLabelNode.GetID()
      parameters["InputModel"] = modelNode.GetID()
      parameters["OutputModel"] = thicknessNode.GetID()   
      # Run probe
      probe = slicer.modules.probevolumewithmodel
      slicer.cli.run(probe, None, parameters, wait_for_completion=True)
      colorLegendDisplayNode = slicer.modules.colors.logic().AddDefaultColorLegendDisplayNode(thicknessNode)
      colorLegendDisplayNode.SetNumberOfLabels(15)
      colorLegendDisplayNode.SetTitleText('Thickness(mm)')
      print("Process completed!. You see ThicknessMap Model")          

  def ProcessExport(self):
    pointListNode = slicer.util.getNode("F")
    thicknessNode = slicer.util.getNode("ThicknessMap")
    if not thicknessNode or not pointListNode:
      print("First, Calculate Thickness and Place Landmarks!")
    else:
      # Get Thickness value from model
      thicknessAll = slicer.util.arrayFromModelPointData(thicknessNode, 'NRRDImage')
      
      # Find thickness 
      pointsLocator = vtk.vtkPointLocator()
      pointsLocator.SetDataSet(thicknessNode.GetPolyData())
      pointsLocator.BuildLocator()

      Label = vtk.vtkStringArray()
      pointListNode.GetControlPointLabels(Label)

      nOfControlPoints = pointListNode.GetNumberOfControlPoints()
      LabelNames = []; ThicknessValue = []
      for i in range(0, nOfControlPoints):        
          ras = [0,0,0]
          pointListNode.GetNthControlPointPositionWorld(i, ras)
          closestPointId = pointsLocator.FindClosestPoint(ras)    
          LabelNames.append(Label.GetValue(i))
          ThicknessValue.append(thicknessAll[closestPointId])

      data = {'Landmark': LabelNames,'Thickness': ThicknessValue}
      df = pd.DataFrame(data)
      
      # save results to csv file
      filepath = Path('out.csv')
      filepath.parent.mkdir(parents=True, exist_ok=True)  
      df.to_csv(filepath,index=False)
      print(df)
      print("File saved. You can see it next to Slicer.exe.")    

class ThicknessMapTest(ScriptedLoadableModuleTest):

  def setUp(self):
    slicer.mrmlScene.Clear()

  def runTest(self):    
    self.setUp()
    self.test_ThicknessMap1()

  def test_ThicknessMap1(self):
    self.delayDisplay("Starting the test")

    # Get/create input data
    import SampleData   
    inputVolume = SampleData.downloadSample('MRHead')
    self.delayDisplay('Loaded test data set')
    
    threshold = 100
    # Test the module logic
    logic = ThicknessMapLogic()    
    logic.ProcessSegmentation(inputVolume, threshold)
    
    self.delayDisplay('Running Thickness Calculation. It takes approximately 30 seconds')    
    logic.ProcessThickness(inputVolume)
    # logic.ProcessExport()

    self.delayDisplay('Test passed')