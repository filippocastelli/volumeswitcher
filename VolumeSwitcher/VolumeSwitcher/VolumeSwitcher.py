import os
import unittest
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

#
# VolumeSwitcher
#


class VolumeSwitcher(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = (
            "VolumeSwitcher"  # TODO: make this more human readable by adding spaces
        )
        self.parent.categories = [
            "Utilities"
        ]  # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.dependencies = (
            []
        )  # TODO: add here list of module names that this module requires
        self.parent.contributors = [
            "Filippo Maria Castelli (European Laboratory for NonLinear Spectroscopy"
        ]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        self.parent.helpText = """
Volume Switcher lets you switch between different volumes without losing track zoom and 3D position.
See more information in <a href="https://github.com/filippocastelli/volumeswitcher">module documentation</a>.
"""
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = """
This file was developed by Filippo Maria Castelli, European Laboratory for NonLinear Spectroscopy.
"""

        # Additional initialization step after application startup is complete
        slicer.app.connect("startupCompleted()", registerSampleData)


#
# Register sample data sets in Sample Data module
#


def registerSampleData():
    """
  Add data sets to Sample Data module.
  """
    # It is always recommended to provide sample data for users to make it easy to try the module,
    # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

    import SampleData

    iconsPath = os.path.join(os.path.dirname(__file__), "Resources/Icons")

    # To ensure that the source code repository remains small (can be downloaded and installed quickly)
    # it is recommended to store data sets that are larger than a few MB in a Github release.

    # VolumeSwitcher1
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category="VolumeSwitcher",
        sampleName="VolumeSwitcher1",
        # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
        # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
        thumbnailFileName=os.path.join(iconsPath, "VolumeSwitcher1.png"),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
        fileNames="VolumeSwitcher1.nrrd",
        # Checksum to ensure file integrity. Can be computed by this command:
        #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
        checksums="SHA256:998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
        # This node name will be used when the data set is loaded
        nodeNames="VolumeSwitcher1",
    )

    # VolumeSwitcher2
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category="VolumeSwitcher",
        sampleName="VolumeSwitcher2",
        thumbnailFileName=os.path.join(iconsPath, "VolumeSwitcher2.png"),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
        fileNames="VolumeSwitcher2.nrrd",
        checksums="SHA256:1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
        # This node name will be used when the data set is loaded
        nodeNames="VolumeSwitcher2",
    )


#
# VolumeSwitcherWidget
#


class VolumeSwitcherWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
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
        uiWidget = slicer.util.loadUI(self.resourcePath("UI/VolumeSwitcher.ui"))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = VolumeSwitcherLogic()

        # Connections

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(
            slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose
        )
        self.addObserver(
            slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose
        )

        # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
        # (in the selected parameter node).

        self.ui.backgroundSelector.connect(
            "currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI
        )

        self.ui.foregroundSelector.connect(
            "currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI
        )

        self.ui.alphaSlider.connect(
            "valueChanged(double)", self.updateParameterNodeFromGUI
        )
        # Buttons

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
        self.removeObserver(
            self._parameterNode,
            vtk.vtkCommand.ModifiedEvent,
            self.updateGUIFromParameterNode,
        )

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
        if not self._parameterNode.GetNodeReference("BackgroundVolume"):
            firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass(
                "vtkMRMLScalarVolumeNode"
            )
            if firstVolumeNode:
                self._parameterNode.SetNodeReferenceID(
                    "BackgroundVolume", firstVolumeNode.GetID()
                )

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
            self.removeObserver(
                self._parameterNode,
                vtk.vtkCommand.ModifiedEvent,
                self.updateGUIFromParameterNode,
            )
        self._parameterNode = inputParameterNode
        if self._parameterNode is not None:
            self.addObserver(
                self._parameterNode,
                vtk.vtkCommand.ModifiedEvent,
                self.updateGUIFromParameterNode,
            )

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
        self.ui.backgroundSelector.setCurrentNode(
            self._parameterNode.GetNodeReference("BackgroundVolume")
        )
        self.ui.foregroundSelector.setCurrentNode(
            self._parameterNode.GetNodeReference("ForegroundVolume")
        )
        self.ui.alphaSlider.value = float(self._parameterNode.GetParameter("AlphaSlider"))

        
        if not (self._parameterNode.GetNodeReference("BackgroundVolume") and self._parameterNode.GetNodeReference("ForegroundVolume")):
            self.ui.alphaSlider.enabled = False
        else:
            self.ui.alphaSlider.enabled = True

        # All the GUI updates are done
        self._updatingGUIFromParameterNode = False

    def updateParameterNodeFromGUI(self, caller=None, event=None):
        """
    This method is called when the user makes any change in the GUI.
    The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
    """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        wasModified = (
            self._parameterNode.StartModify()
        )  # Modify all properties in a single batch
        self._parameterNode.SetNodeReferenceID(
            "BackgroundVolume", self.ui.backgroundSelector.currentNodeID
        )

        self._parameterNode.SetNodeReferenceID(
            "ForegroundVolume", self.ui.foregroundSelector.currentNodeID
        )

        self._parameterNode.SetParameter("AlphaSlider", str(self.ui.alphaSlider.value))

        self._parameterNode.EndModify(wasModified)

        self.launchLogic()

    def launchLogic(self):

        foreground_volume = self._parameterNode.GetNodeReference("ForegroundVolume")
        background_volume = self._parameterNode.GetNodeReference("BackgroundVolume")
        # alpha = self._parameterNode.GetNodeReference("AlphaSlider")
        alpha = self.ui.alphaSlider.value
        self.logic.onItemSelect(background=background_volume,
                                foreground=foreground_volume,
                                alpha=alpha)

#
# VolumeSwitcherLogic
#


class VolumeSwitcherLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

    def __init__(self):
        """
    Called when the logic class is instantiated. Can be used for initializing member variables.
    """
        ScriptedLoadableModuleLogic.__init__(self)
        
        self.currentID = self._get_currentID()
        self.currentFOV  = self._get_fov()
        self.currentOffset = self._get_offset() 
        self.lastFOV = self.currentFOV
        self.lastOffset = self.currentOffset
        self.lastID = self.currentID
        
        self.isEnabled = False
        self.isUpdatingSlice = False

    def setDefaultParameters(self, parameterNode):
        """
    Initialize parameter node with default settings.
    """
        if not parameterNode.GetParameter("AlphaSlider"):
            parameterNode.SetParameter("AlphaSlider", "0.50")

    def _get_fov(self):
        return self._get_node().GetFieldOfView()
    
    def _get_currentID(self):
        redCompositeNode = self._get_logic().GetSliceCompositeNode
        return  redCompositeNode().GetBackgroundVolumeID()
    
    def _get_slice(self, color="Red"):
        return slicer.app.layoutManager().sliceWidget(color)
    
    def _get_logic(self, color="Red"):
        return self._get_slice(color).sliceLogic()

    def _get_node(self, color="Red"):
        return self._get_slice(color).mrmlSliceNode()
    
    def _set_FOV(self, fov):
        redSlice = self._get_slice()
        redNode = redSlice.mrmlSliceNode()
        redNode.SetFieldOfView(fov[0], fov[1], fov[2])

    def _get_offset(self):
        return self._get_logic().GetSliceOffset()

    def _set_offset(self, offset):
        self._get_logic().SetSliceOffset(offset)

    @staticmethod
    def _get_volumenode(volumenode):
        return slicer.util.getNode(volumenode.GetName())

    def onItemSelect(self, background=None, foreground=None, alpha=None):

        backgroundNode = "keep-current" if background is None else self._get_volumenode(background)
        foregroundNode = None if foreground is None else self._get_volumenode(foreground)

        slicer.util.setSliceViewerLayers(
            background=backgroundNode,
            foreground=foregroundNode,
            rotateToVolumePlane=False,
            fit=False,
            label="keep-current",
            foregroundOpacity=alpha
        )

        self._adjustview()

    def _adjustview(self):
        self.currentFOV = self._get_fov()
        self.lastFOV =  self.currentFOV
        self.currentOffset = self._get_offset()
        self.lastOffset = self.currentOffset

        self._set_FOV(self.currentFOV)
        self._set_offset(self.currentOffset)

#
# VolumeSwitcherTest
#


class VolumeSwitcherTest(ScriptedLoadableModuleTest):
    """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
        slicer.mrmlScene.Clear()

    def runTest(self):
        """Run as few or as many tests as needed here.
    """
        self.setUp()


    #TODO: Implement tests