# -*- coding: utf-8 -*-
"""
/***************************************************************************
 lakeer_plugin
                                 A QGIS plugin
 lakeer plugin to import/export data
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-03-06
        git sha              : $Format:%H$
        copyright            : (C) 2019 by lakeer
        email                : amar.kamthe@soft-corner.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QVariant
from PyQt5.QtGui import QIcon, QStandardItem, QStandardItemModel, QColor,  QPainter, QFont, QPalette, QBrush, QPen
from PyQt5.QtWidgets import QAction, QCheckBox, QListWidget, QTreeWidgetItem, QMessageBox, QWidget
from PyQt5 import QtGui, QtCore
from qgis.core import *#QgsVectorLayer, QgsProject
import qgis

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .lakeer_dialog import lakeer_pluginDialog
import os.path
import math
from .configuration import *

class lakeer_plugin:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'lakeer_plugin_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&lakeer plugin')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None
        self.database = Database()

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('lakeer_plugin', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/lakeer/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'lakeer plugin'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&lakeer plugin'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started

        if self.first_start == True:

            self.first_start = False
            self.dlg = lakeer_pluginDialog()
            self.dlg.tabWidget.currentChanged.connect(self.tab_clicked)
            self.tab_clicked(1)

            # self.dlg.tabWidget.currentChanged(0)
            # self.dlg.databaseSetting.activated.connect(self.tab2_configuration)
            self.dlg.button_box.accepted.connect(self.tab1_accept)
            self.dlg.button_box.rejected.connect(self.reject)
            self.dlg.buttonBox.accepted.connect(self.tab2_accept)
            self.dlg.buttonBox.rejected.connect(self.reject)

            # self.overlay = Overlay(self.dlg.centralWidget())
            # self.overlay.hide()
            # self.overlay.show()



        self.dlg.show()
        self.check_database_connection()
        # Run the dialog event loop
        # result = self.dlg.exec_()

    def tab_clicked(self, i):
        tab_selection = [self.tab1_loaddata, self.tab2_configuration]
        val = True
        if i != 1:
            val = self.check_database_connection()
        if val:
            tab_selection[i]()

    def tab1_loaddata(self):
        self.render_tree_widget()
        self.renderComboBox()

    def tab2_configuration(self):
        config = self.database.readSettings()
        self.dlg.txt_databasename_2.setText(config['database_name'])
        self.dlg.txt_host_2.setText(config['host'])
        self.dlg.txt_port_2.setText(config['port'])
        self.dlg.txt_username_2.setText(config['username'])
        self.dlg.txt_password_2.setText(config['password'])


    def reject(self):
        print ("Inside reject")
        self.dlg.close()

    def tab1_accept(self):
        proj = QgsProject.instance()
        current_layer =[x.name() for x in proj.mapLayers().values()]

        ####################################################
        ## Load department
        ####################################################
        selected_department = self.dlg.comboBox.currentText()
        if selected_department != '-':
            level_boundaries = self.database.department_polygon(selected_department)
            vectorLayer = None
            # assets = db.service_assets.find({"service_metric_id":self.check_list[item]})
            if selected_department not in current_layer:
                vectorLayer = QgsVectorLayer('Polygon?crs=epsg:4326', selected_department, 'memory')
                # vectorLayer.setCustomProperty("showFeatureCount", len(list(level_boundaries)))
                proj.addMapLayer(vectorLayer)
            else:
                vectorLayerTemp = proj.mapLayersByName(selected_department)
                if len(vectorLayerTemp) > 0:
                    vectorLayer = vectorLayerTemp[0]
                    vectorLayer.dataProvider().truncate()

            if vectorLayer:
                prov = vectorLayer.dataProvider()
                new_coords = []
                fields = QgsFields()
                for x in ['name', 'level_type']:
                    fields.append(QgsField(x, QVariant.String))
                prov.addAttributes(fields)
                vectorLayer.updateFields()
                fields = prov.fields()
                for level_boundary in level_boundaries:
                    try:
                        polygons = [[[QgsPointXY(point[0], point[1]) for point in polygon] for polygon in multi_polygon] for multi_polygon in level_boundary['geometry']['coordinates']]


                        #new_coords_tmp = QgsMultiPolygon(level_boundary['geometry']['coordinates'])
                        geom = QgsGeometry.fromMultiPolygonXY(polygons)
                        #geom = QgsGeometry(new_coords_tmp)
                        outGeom = QgsFeature()
                        outGeom.setFields(fields)
                        outGeom.setAttribute('name', level_boundary['name'])
                        outGeom.setAttribute('level_type', level_boundary['level_type'])

                        outGeom.setGeometry(geom)
                        new_coords.append(outGeom)
                    except Exception as e:
                        print (e)

                # single_symbol_renderer = vectorLayer.renderer()
                # symbol = single_symbol_renderer.symbol()
                # symbol.setOpacity(45)
                # symbols = QgsSingleSymbolRenderer(symbol)
                # vectorLayer.triggerRepaint()

                #Seems to work
                symbol = QgsFillSymbol.defaultSymbol(vectorLayer.geometryType())
                symbol.setOpacity(0.6)
                myRenderer = QgsSingleSymbolRenderer(symbol)
                vectorLayer.setRenderer(myRenderer)

                # try:
                #     myOpacity = 0.4
                #     myMin = 0.0
                #     myMax = 50.0
                #     myLabel = 'Group 1'
                #     myColour = QtGui.QColor('#ffee00')


                #     mySymbol1 = QgsSymbol.defaultSymbol(vectorLayer.geometryType())
                #     mySymbol1.setColor(myColour)
                #     mySymbol1.setOpacity(myOpacity)
                #     myRange1 = QgsRendererRange(myMin, myMax, mySymbol1, myLabel)
                #     myRenderer = QgsGraduatedSymbolRenderer('', [myRange1])
                #     vectorLayer.setRenderer(myRenderer)
                # except:
                #     pass

                # symbol = QgsFillSymbol.defaultSymbol(vectorLayer.geometryType())
                # symbol_layer = QgsSimpleFillSymbolLayer()
                # symbol_layer.setColor(QColor("#ffffff"))
                # symbol.appendSymbolLayer(symbol_layer)
                # renderer =QgsSingleSymbolRenderer(symbol)
                # vectorLayer.setRendererV2(renderer)
                # vectorLayer.triggerRepaint()


                prov.addFeatures(new_coords)
                vectorLayer.updateExtents()
                # print (vectorLayer.featureCount())
        ################################################################
        # Display selected metrics
        #
        ################################################################
        for item in self.dlg.selected_items:
            vectorLayer = None
            #assets = db.service_assets.find({"service_metric_id":self.check_list[item]})
            if item not in current_layer:
                vectorLayer = QgsVectorLayer('Point?crs=epsg:4326', item, 'memory')

                proj.addMapLayer(vectorLayer)
            else:
                vectorLayerTemp = proj.mapLayersByName(item)
                if len(vectorLayerTemp) >0:
                    vectorLayer = vectorLayerTemp[0]
                    vectorLayer.dataProvider().truncate()

            if vectorLayer:
                prov = vectorLayer.dataProvider()
                #fields = prov.fields()
                #vectorLayer.updateFields()
                #feat =vectorLayer.getFeatures()
                #attrs = feat.attributes()
                #geom = feat.geometry()
                #coords = geom.asPoint()
                assets = self.database.service_metrics_geometry(self.check_list[item])
                # vectorLayer.setCustomProperty("showFeatureCount", len(list(assets)))
                new_coords =[]
                fields = QgsFields()
                for x, y in assets[0]['properties'].items():
                    fields.append(QgsField(x, QVariant.String))
                prov.addAttributes(fields)
                vectorLayer.updateFields()
                fields = prov.fields()
                for asset in assets:
                    try:
                        new_coords_tmp = QgsPoint(asset['location'][0], asset['location'][1])
                        geom = QgsGeometry(new_coords_tmp)

                        outGeom = QgsFeature()
                        outGeom.setGeometry(geom)


                        # outGeom.initAttributes(2)
                        # outGeom.setAttributes( [asset['properties']['stop_id'], asset['properties']['stop_name']])
                        # fields = QgsFields()
                        # for x,y in asset['properties'].items():
                        #
                        #     fields.append(QgsField(x, QVariant.String))
                        #
                        #
                        outGeom.setFields(fields)
                        for x, y in asset['properties'].items():
                            outGeom.setAttribute(x,str(y))
                        # if 'stop_id' in asset['properties'].keys():
                        #     outGeom.setAttribute('stop_id',asset['properties']['stop_id'])
                        # if 'stop_name' in asset['properties'].keys():
                        #     outGeom.setAttribute('stop_name',asset['properties']['stop_name'])
                        new_coords.append(outGeom)
                    except Exception as e:
                        print (e)
                #outGeom.setAttributes(attrs)
                prov.addFeatures(new_coords)
                vectorLayer.updateExtents()


        root = QgsProject.instance().layerTreeRoot()
        for child in root.children():
            if isinstance(child, QgsLayerTreeLayer):
                child.setCustomProperty("showFeatureCount", True)

        qgis.utils.iface.zoomToActiveLayer()

        self.dlg.close()

    def tab2_accept(self):
        config={}
        database_name = self.dlg.txt_databasename_2.text().strip()
        host = self.dlg.txt_host_2.text().strip()
        port = self.dlg.txt_port_2.text().strip()
        username = self.dlg.txt_username_2.text().strip()
        password = self.dlg.txt_password_2.text().strip()


        config['database_name'] = database_name or 'lakeer'
        config['host'] = host or '127.0.0.1'
        config['port'] = port or '27017'
        config['username'] = username or ''
        config['password'] = password or ''
        self.database.writeSettings(config)

        self.check_database_connection(True)

    def check_database_connection(self, db_update = False):

        self.database = Database()
        flag, msg = self.database.check_connection(serverSelectionTimeoutMS=10, connectTimeoutMS=20000)

        if flag:
            if db_update:
                buttonReply = QMessageBox.information(self.dlg.centralwidget, 'Configuration',
                                                  "Database connection successful.",
                                                  QMessageBox.Yes)
        else:
            buttonReply = QMessageBox.critical(self.dlg.centralwidget, 'Configuration error', "Check your database connection (ERROR) : " + str(msg),
                                               QMessageBox.Yes)
        return flag

    def render_tree_widget(self):

        self.dlg.items = []
        list_widget = self.dlg.treeWidget
        list_widget.clear()
        self.check_list ={}
        self.dlg.selected_items = []
        categories =self.database.service_categories()

        for category in categories:
            targetTree = QTreeWidgetItem([category['name']])
            targetTree.setFlags(targetTree.flags() | QtCore.Qt.ItemIsTristate | QtCore.Qt.ItemIsUserCheckable)
            targetTree.setText(0, category['name'])
            service_categories = self.database.service_per_category(category['_id'])

            for service_category in service_categories:
                pathTree = QTreeWidgetItem([service_category['service_type']])
                pathTree.setFlags(pathTree.flags() | QtCore.Qt.ItemIsTristate | QtCore.Qt.ItemIsUserCheckable)
                pathTree.setCheckState(0, QtCore.Qt.Unchecked)
                pathTree.setText(0, service_category['service_type'])
                targetTree.addChild(pathTree)
                for service in sorted(service_category['metrics'], key=lambda x: x['display_name']):
                    self.check_list[service['display_name']]= service['_id']
                    child = QTreeWidgetItem([service['display_name']])
                    child.setFlags(child.flags() | QtCore.Qt.ItemIsUserCheckable)
                    child.setCheckState(0, QtCore.Qt.Unchecked)
                    child.setText(0, service['display_name'])
                    pathTree.addChild(child)
            list_widget.expandToDepth(2)
            list_widget.addTopLevelItem(targetTree)
            list_widget.setStyleSheet('''
                                             QTreeWidget {
     alternate-background-color: yellow;
 }

                                          QTreeWidget {
     show-decoration-selected: 1;
 }
QTreeWidget::item:first  {
        font:bold;
    }
 QTreeWidget::item {
      border: 1px solid #d9d9d9;
     border-top-color: transparent;
     border-bottom-color: transparent;
 }

 QTreeWidget::item:hover {
     background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #e7effd, stop: 1 #cbdaf1);
     border: 1px solid #bfcde4;
 }

 QTreeWidget::item:selected {
     border: 1px solid #567dbc;
 }

 QTreeWidget::item:selected:active{
     background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #6ea1f1, stop: 1 #567dbc);
 }

 QTreeWidget::item:selected:!active {
     background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #6b9be8, stop: 1 #577fbf);
 }''')
        list_widget.setHeaderLabels(["Service metrics"])
        list_widget.itemChanged.connect(self.handle_item_changed)

    def handle_item_changed(self, item, column):
        if item.checkState(column) == QtCore.Qt.Checked:
            if item.text(0) not in self.dlg.selected_items and item.text(0) in self.check_list.keys():
                self.dlg.selected_items.append(item.text(0))
        elif item.checkState(column) == QtCore.Qt.Unchecked:
            if item.text(0) in self.dlg.selected_items:
                self.dlg.selected_items.remove(item.text(0))

    def renderComboBox(self):
        self.dlg.items = []
        combobox = self.dlg.comboBox
        combobox.clear()
        combo_list = self.database.fetch_department()
        combobox.addItems(combo_list)


class Overlay(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        palette = QPalette(self.palette())
        palette.setColor(palette.Background, QtCore.Qt.transparent)
        self.setPalette(palette)

    def paintEvent(self, event):

        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(event.rect(), QBrush(QColor(255, 255, 255, 127)))
        painter.setPen(QPen(QtCore.Qt.NoPen))

        for i in range(6):
            if (self.counter / 5) % 6 == i:
                painter.setBrush(QBrush(QColor(127 + (self.counter % 5) * 32, 127, 127)))
            else:
                painter.setBrush(QBrush(QColor(127, 127, 127)))
            painter.drawEllipse(
                self.width() / 2 + 30 * math.cos(2 * math.pi * i / 6.0) - 10,
                self.height() / 2 + 30 * math.sin(2 * math.pi * i / 6.0) - 10,
                20, 20)
        painter.end()

    def showEvent(self, event):
        self.timer = self.startTimer(50)
        self.counter = 0

    def timerEvent(self, event):
        self.counter += 1
        self.update()
        if self.counter == 60:
            self.killTimer(self.timer)
            self.hide()
