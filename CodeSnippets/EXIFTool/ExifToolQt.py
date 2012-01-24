import sys
from PyQt4 import QtGui, QtCore
from ExifToolQtDialog import Ui_ExifToolMainDialog as Dlg


class ExifToolDialog(QtGui.QDialog, Dlg):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        self.connectPushButtons()

        self.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        self.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)

    def connectPushButtons(self):
        for button_name in dir(self):
            button = getattr(self, button_name)
#            print button_name, button
            if not isinstance(button, (QtGui.QPushButton, QtGui.QDialogButtonBox)):
                continue

            method_name = button_name + "_clicked"
            method = getattr(self, method_name, None)
            if method is None:
                print "Error: there exist no method '%s', please implement" % method_name
                continue

            self.connect(button, QtCore.SIGNAL("clicked()"), method)

    def destination_path_button_clicked(self):
        print "destination_path_button_clicked"

    def source_path_button_clicked(self):
        print "source_path_button_clicked"

    def accept(self):
        print "self.accept"
    def reject(self):
        print "self.reject"
        self.close()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    dialog = ExifToolDialog()
    dialog.show()
    print "-END-"
    sys.exit(app.exec_())
