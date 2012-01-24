# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ExifTool.ui'
#
# Created: Tue Jun 22 12:55:41 2010
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_ExifToolMainDialog(object):
    def setupUi(self, ExifToolMainDialog):
        ExifToolMainDialog.setObjectName("ExifToolMainDialog")
        ExifToolMainDialog.resize(478, 645)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ExifToolMainDialog.sizePolicy().hasHeightForWidth())
        ExifToolMainDialog.setSizePolicy(sizePolicy)
        self.widget = QtGui.QWidget(ExifToolMainDialog)
        self.widget.setGeometry(QtCore.QRect(1, 7, 471, 631))
        self.widget.setObjectName("widget")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout_2.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.source_path = QtGui.QLineEdit(self.widget)
        self.source_path.setObjectName("source_path")
        self.horizontalLayout.addWidget(self.source_path)
        self.source_path_button = QtGui.QPushButton(self.widget)
        self.source_path_button.setObjectName("source_path_button")
        self.horizontalLayout.addWidget(self.source_path_button)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.destination_path = QtGui.QLineEdit(self.widget)
        self.destination_path.setObjectName("destination_path")
        self.horizontalLayout_2.addWidget(self.destination_path)
        self.destination_path_button = QtGui.QPushButton(self.widget)
        self.destination_path_button.setObjectName("destination_path_button")
        self.horizontalLayout_2.addWidget(self.destination_path_button)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.radioButton = QtGui.QRadioButton(self.widget)
        self.radioButton.setObjectName("radioButton")
        self.gridLayout.addWidget(self.radioButton, 0, 1, 1, 1)
        self.radioButton_2 = QtGui.QRadioButton(self.widget)
        self.radioButton_2.setObjectName("radioButton_2")
        self.gridLayout.addWidget(self.radioButton_2, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setMinimumSize(QtCore.QSize(0, 27))
        self.buttonBox.setMaximumSize(QtCore.QSize(467, 16777215))
        self.buttonBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Discard)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 2, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 2, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 0, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.plainTextEdit = QtGui.QPlainTextEdit(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plainTextEdit.sizePolicy().hasHeightForWidth())
        self.plainTextEdit.setSizePolicy(sizePolicy)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.verticalLayout_2.addWidget(self.plainTextEdit)
        self.progressBar = QtGui.QProgressBar(self.widget)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout_2.addWidget(self.progressBar)

        self.retranslateUi(ExifToolMainDialog)
        QtCore.QMetaObject.connectSlotsByName(ExifToolMainDialog)

    def retranslateUi(self, ExifToolMainDialog):
        ExifToolMainDialog.setWindowTitle(QtGui.QApplication.translate("ExifToolMainDialog", "ExifToolMainDialog", None, QtGui.QApplication.UnicodeUTF8))
        self.source_path_button.setText(QtGui.QApplication.translate("ExifToolMainDialog", "source path", None, QtGui.QApplication.UnicodeUTF8))
        self.destination_path_button.setText(QtGui.QApplication.translate("ExifToolMainDialog", "destination path", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton.setText(QtGui.QApplication.translate("ExifToolMainDialog", "move files", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_2.setText(QtGui.QApplication.translate("ExifToolMainDialog", "copy files", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ExifToolMainDialog = QtGui.QDialog()
    ui = Ui_ExifToolMainDialog()
    ui.setupUi(ExifToolMainDialog)
    ExifToolMainDialog.show()
    sys.exit(app.exec_())

