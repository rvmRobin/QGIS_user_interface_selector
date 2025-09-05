from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QComboBox, QDialogButtonBox, QWidget
from qgis.core import QgsProcessingAlgorithm, QgsProcessingFeedback
from qgis.utils import iface

# Globals to store the original state before role switch
previous_toolbar_state = {}
previous_panel_state = {}

class InterfaceRoleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Select userinterface')

        self.role_box = QComboBox()
        self.role_box.addItems(['Editor', 'Viewer', 'Analyser', 'Reset to default'])

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.role_box)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_selected_role(self):
        return self.role_box.currentText()


class SetUserInterfaceRole(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        pass

    def processAlgorithm(self, parameters, context, feedback: QgsProcessingFeedback):
        global previous_toolbar_state, previous_panel_state

        dialog = InterfaceRoleDialog()

        try:
            accepted_code = QDialog.Accepted
        except AttributeError:
            accepted_code = QDialog.DialogCode.Accepted

        if dialog.exec() != accepted_code:
            feedback.pushInfo("Set interface cancelled.")
            return {}

        role = dialog.get_selected_role()
        main_window = iface.mainWindow()

        # Get all toolbars in the main window
        all_toolbars = main_window.findChildren(type(iface.digitizeToolBar()))

        # Get all panels (widgets that are children of main window, not top-level windows)
        all_panels = [
            w for w in main_window.findChildren(QWidget)
            if w.parent() == main_window and not w.isWindow()
        ]

        # Save current states if not resetting and no previous saved state yet
        if role != 'Reset to standard' and not previous_toolbar_state:
            previous_toolbar_state = {}
            for tb in all_toolbars:
                name = tb.objectName()
                if name:
                    previous_toolbar_state[name] = tb.isVisible()

        if role != 'Reset to standard' and not previous_panel_state:
            previous_panel_state = {}
            for p in all_panels:
                name = p.objectName()
                if name:
                    previous_panel_state[name] = p.isVisible()

        # 1. Disable all toolbars and panels
        for tb in all_toolbars:
            tb.setVisible(False)
        for p in all_panels:
            if p.objectName() not in ['centralwidget', 'menubar', '', 'statusbar']:
                p.setVisible(False)

        # 2. Reset to previous saved state
        if role == 'Reset naar standaard':
            for tb in all_toolbars:
                name = tb.objectName()
                if name in previous_toolbar_state:
                    tb.setVisible(previous_toolbar_state[name])
            for p in all_panels:
                name = p.objectName()
                if name in previous_panel_state:
                    p.setVisible(previous_panel_state[name])

            iface.messageBar().pushSuccess("Interface", "Interface set to original.")
            previous_toolbar_state = {}
            previous_panel_state = {}
            return {}
      
        # 3. Role-based toolbar and panel visibility setup
        toolbars_by_role = {
            'Editor': [
                'mFileToolBar', 'mDigitizeToolBar', 'mAdvancedDigitizeToolBar', 'mMapNavToolBar', 'mAttributesToolBar',
                'mSnappingToolBar', 'mSelectionToolBar', 'mBrowserToolbar', 'MerginMapsToolbar', 'mIdentifyToolbar',
                'processingToolbar', 'mTopologyToolbar'
            ],

            'Viewer': [
                'mFileToolBar', 'mMapNavToolBar', 'mAttributesToolBar',
                'mBrowserToolbar', 'MerginMapsToolbar', 'mIdentifyToolbar',
                'processingToolbar'
            ],

            'Analyser': [
                'mFileToolBar', 'mMapNavToolBar', 'mAttributesToolBar',
                'mSelectionToolBar', 'mBrowserToolbar', 'MerginMapsToolbar', 
                'mIdentifyToolbar', 'processingToolbar'
            ]
        }

        panels_by_role = {
            'Editor': [
                'centralwidget','menubar','statusbar','mFileToolBar','mDigitizeToolBar','mAdvancedDigitizeToolBar',
                'mMapNavToolBar','mAttributesToolBar','mSnappingToolBar','mSelectionToolBar','Layers','Browser',
                'IdentifyResultsDock','ProcessingToolbox', 'checkDock'
                ],

            'Viewer': [
                'centralwidget','menubar','statusbar','mFileToolBar',
                'mMapNavToolBar','mAttributesToolBar','Layers','Browser',
                'IdentifyResultsDock','ProcessingToolbox'
                ],
                
            'Analyser': [
                'centralwidget','menubar','statusbar','mFileToolBar',
                'mMapNavToolBar','mAttributesToolBar','Layers','Browser',
                'IdentifyResultsDock','ProcessingToolbox',
                'StatisticalSummaryDockWidget'
                ]

        }

        # Enable only toolbars for selected role
        for tb in all_toolbars:
            if tb.objectName() in toolbars_by_role.get(role, []):
                tb.setVisible(True)

        # Enable only panels for selected role
        for p in all_panels:
            if p.objectName() in panels_by_role.get(role, []):
                p.setVisible(True)

        iface.messageBar().pushSuccess("Interface", f"Interface set for: {role}")

        return {}

    def name(self):
        return 'set_user_interface_panels_and_toolbars'

    def displayName(self):
        return 'Set user interface (toolbars and panals)'

    def group(self):
        return 'Set user interface'

    def groupId(self):
        return "Setuserinterface"

    def createInstance(self):
        return SetUserInterfaceRole()
