from qgis.core import *
from qgis.gui import *

class LayerEventHandler(object):
    """
    Listens for committed feature additions and changes feature attributes.
    """
    def __init__(self, vlayer):
        self.vlayer = vlayer
        self.connect_committed_signals()

    def connect_committed_signals(self):
        """
        Connect signals for editing events
        """
        self.vlayer.committedFeaturesAdded.connect(self.committed_adds)
        self.vlayer.committedGeometriesChanges.connect(self.committed_changes)
        self.vlayer.committedFeaturesRemoved.connect(self.committed_deletes)

    def disconnect_committed_signals(self):
        """
        Disconnect signals for editing events
        """
        self.vlayer.committedFeaturesAdded.disconnect()
        self.vlayer.committedGeometriesChanges.disconnect()
        self.vlayer.committedFeaturesRemoved.disconnect()

    def committed_adds(self, layer_id, added_features):
        print('Committed features added to layer {}:'.format(layer_id))
        for feature in added_features:
            print(feature.id())
            self.replace_feature(feature.id())

    def committed_changes(self, layer_id, changed_geometries):
        print('Committed geometries changed in layer {}:'.format(layer_id))
        for fid in changed_geometries.keys():
            print(fid)
            self.update_geometry(fid, changed_geometries[fid])

    def committed_deletes(self, layer_id, deleted_fids):
        print('Committed features deleted from layer {}:'.format(layer_id))
        for fid in deleted_fids:
            print(fid)

    def replace_feature(self, fid):
        """
        Replace feature with customised geometry and attributes.
        """
        print('Replacing feature {} here.'.format(fid))
        feature = self.vlayer.getFeatures(
            QgsFeatureRequest().setFilterFid(fid)).next()
        geometry = feature.geometry()

        # Create new feature
        new_feature = QgsFeature(self.vlayer.pendingFields())
        geometry.translate(0, 50)  # Modify original geometry
        new_feature.setGeometry(geometry)
        new_feature.setAttribute('symbol', 10)  # Customise attributes

        # Update layer by removing old and adding new
        result = self.vlayer.dataProvider().deleteFeatures([fid])
        result, new_features = self.vlayer.dataProvider().addFeatures(
                [new_feature])
        for f in new_features:
            print('Replacement feature {} added'.format(f.id()))

    def update_geometry(self, fid, geometry):
        """
        Update the geometry of a feature, e.g. jump 100 m east.
        """
        geometry.translate(100, 0)
        self.vlayer.dataProvider().changeGeometryValues({fid: geometry})


class FeatureModifier:
    def __init__(self, vlayer):
        self.iface=vlayer
        self.connect_signals()

    def connect_signals(self):
        self.iface.featureAdded.connect(self.myfonction)
        # self.vlayer.editingStarted.connect(self.editing_started)
        # self.vlayer.editingStopped.connect(self.editing_stopped)
        # self.vlayer.geometryChanged.connect(self.geometry_changed)

    def myfonction(self):
        print ("Geometry added")

    def editing_started(self):
        print('Editing started')
        # Disable attributes dialog
        # QSettings().setValue(
        #     '/qgis/digitizing/disable_enter_attribute_values_dialog', True)
        #self.edit_handler = LayerEventHandler(self.vlayer)

    def editing_stopped(self):
        print('Editing stopped')
        # self.edit_handler = None
        # # Re-enable attributes dialog
        # # QSettings().setValue(
        # #     '/qgis/digitizing/disable_enter_attribute_values_dialog', False)
        # if self.vlayer.isEditable() is True:
        #     # Rolling back changes ends destroys geometry_handler class but
        #     # layer remains editable.  In this case, recreate it.
        #     self.editing_started()