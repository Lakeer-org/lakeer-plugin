from PyQt5.QtWidgets import QMessageBox, QStyledItemDelegate, QStyleOptionButton, QStyle, QTreeWidgetItemIterator
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QVariant, Qt, QEvent
from .configuration import *

def check_database_connection(self, db_update=False):
    """
    Method used to check the database connection. And alter whenever necessary.
    :param db_update:
    :return:
    """
    self.database = Database()
    flag, msg = self.database.check_connection(serverSelectionTimeoutMS=10, connectTimeoutMS=20000)

    if flag:
        if db_update:
            buttonReply = QMessageBox.information(self.dlg.centralwidget, 'Configuration',
                                                  "Database connection successful.",
                                                  QMessageBox.Yes)
    else:
        buttonReply = QMessageBox.critical(self.dlg.centralwidget, 'Configuration error',
                                           "Check your database connection (ERROR) : " + str(msg),
                                           QMessageBox.Yes)
    return flag

class Delegate(QStyledItemDelegate):
    """
        Class to change the checkbox to radio button and its selection across treeview.
    """
    def paint(self, painter, option, index):
        if not index.parent().isValid():
            QStyledItemDelegate.paint(self, painter, option, index)
        else:
            widget = option.widget
            style = widget.style() if widget else QApplication.style()
            opt = QStyleOptionButton()
            opt.rect = option.rect
            opt.text = index.data()
            opt.state |= QStyle.State_On if index.data(Qt.CheckStateRole) else QStyle.State_Off
            style.drawControl(QStyle.CE_RadioButton, opt, painter, widget)

    def editorEvent(self, event, model, option, index):
        value = QStyledItemDelegate.editorEvent(self, event, model, option, index)
        if value:
            if event.type() == QEvent.MouseButtonRelease:
                if index.data(Qt.CheckStateRole) == Qt.Checked:
                    for x in range(model.rowCount()):
                        index_model = model.index(x,0)
                        for i in range(model.rowCount(index_model)):
                            if i != index.row() or x != index.parent().row():
                                ix = index_model.child(i, 0)
                                model.setData(ix, Qt.Unchecked, Qt.CheckStateRole)

                    # parent = index.parent()
                    # for i in range(model.rowCount(parent)):
                    #     print ("--------------")
                    #     if i != index.row():
                    #         ix = parent.child(i, 0)
                    #         model.setData(ix, Qt.Unchecked, Qt.CheckStateRole)

        return value

