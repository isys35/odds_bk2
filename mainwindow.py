# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow_v2.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(934, 829)
        MainWindow.setMinimumSize(QtCore.QSize(0, 0))
        MainWindow.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout_3.addWidget(self.pushButton)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_3.addWidget(self.label_3)
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_3.sizePolicy().hasHeightForWidth())
        self.groupBox_3.setSizePolicy(sizePolicy)
        self.groupBox_3.setMinimumSize(QtCore.QSize(350, 0))
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_12 = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.scrollArea = QtWidgets.QScrollArea(self.groupBox_3)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 324, 683))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_13 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.verticalLayout_13.addLayout(self.formLayout)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_12.addWidget(self.scrollArea)
        self.verticalLayout_3.addWidget(self.groupBox_3)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.verticalLayout_21 = QtWidgets.QVBoxLayout()
        self.verticalLayout_21.setObjectName("verticalLayout_21")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_6.addWidget(self.label_4)
        self.lineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit.setObjectName("lineEdit")
        self.verticalLayout_6.addWidget(self.lineEdit)
        self.horizontalLayout_3.addLayout(self.verticalLayout_6)
        self.verticalLayout_9 = QtWidgets.QVBoxLayout()
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.label_6 = QtWidgets.QLabel(self.groupBox)
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.verticalLayout_9.addWidget(self.label_6)
        self.lineEdit_3 = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.verticalLayout_9.addWidget(self.lineEdit_3)
        self.horizontalLayout_3.addLayout(self.verticalLayout_9)
        self.verticalLayout_8 = QtWidgets.QVBoxLayout()
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.verticalLayout_8.addWidget(self.label_5)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.verticalLayout_8.addWidget(self.lineEdit_2)
        self.horizontalLayout_3.addLayout(self.verticalLayout_8)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)
        self.verticalLayout_21.addLayout(self.verticalLayout_4)
        self.pushButton_4 = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_4.setObjectName("pushButton_4")
        self.verticalLayout_21.addWidget(self.pushButton_4)
        self.horizontalLayout_8.addLayout(self.verticalLayout_21)
        self.groupBox_2 = QtWidgets.QGroupBox(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_11 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout()
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.label_7 = QtWidgets.QLabel(self.groupBox_2)
        self.label_7.setAlignment(QtCore.Qt.AlignCenter)
        self.label_7.setObjectName("label_7")
        self.verticalLayout_10.addWidget(self.label_7)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_9 = QtWidgets.QLabel(self.groupBox_2)
        self.label_9.setObjectName("label_9")
        self.horizontalLayout_4.addWidget(self.label_9)
        self.label_10 = QtWidgets.QLabel(self.groupBox_2)
        self.label_10.setObjectName("label_10")
        self.horizontalLayout_4.addWidget(self.label_10)
        self.label_8 = QtWidgets.QLabel(self.groupBox_2)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_4.addWidget(self.label_8)
        self.verticalLayout_10.addLayout(self.horizontalLayout_4)
        self.verticalLayout_11.addLayout(self.verticalLayout_10)
        self.pushButton_5 = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_5.setObjectName("pushButton_5")
        self.verticalLayout_11.addWidget(self.pushButton_5)
        self.horizontalLayout_8.addWidget(self.groupBox_2)
        self.verticalLayout_5.addLayout(self.horizontalLayout_8)
        self.verticalLayout_14 = QtWidgets.QVBoxLayout()
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        self.groupBox_4 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_4.setObjectName("groupBox_4")
        self.verticalLayout_16 = QtWidgets.QVBoxLayout(self.groupBox_4)
        self.verticalLayout_16.setObjectName("verticalLayout_16")
        self.verticalLayout_15 = QtWidgets.QVBoxLayout()
        self.verticalLayout_15.setObjectName("verticalLayout_15")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_11 = QtWidgets.QLabel(self.groupBox_4)
        self.label_11.setObjectName("label_11")
        self.horizontalLayout_6.addWidget(self.label_11)
        self.lineEdit_4 = QtWidgets.QLineEdit(self.groupBox_4)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.horizontalLayout_6.addWidget(self.lineEdit_4)
        self.pushButton_6 = QtWidgets.QPushButton(self.groupBox_4)
        self.pushButton_6.setObjectName("pushButton_6")
        self.horizontalLayout_6.addWidget(self.pushButton_6)
        self.verticalLayout_15.addLayout(self.horizontalLayout_6)
        self.verticalLayout_16.addLayout(self.verticalLayout_15)
        self.verticalLayout_14.addWidget(self.groupBox_4)
        self.groupBox_5 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_5.setObjectName("groupBox_5")
        self.verticalLayout_18 = QtWidgets.QVBoxLayout(self.groupBox_5)
        self.verticalLayout_18.setObjectName("verticalLayout_18")
        self.verticalLayout_17 = QtWidgets.QVBoxLayout()
        self.verticalLayout_17.setObjectName("verticalLayout_17")
        self.label_12 = QtWidgets.QLabel(self.groupBox_5)
        self.label_12.setAlignment(QtCore.Qt.AlignCenter)
        self.label_12.setObjectName("label_12")
        self.verticalLayout_17.addWidget(self.label_12)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_13 = QtWidgets.QLabel(self.groupBox_5)
        self.label_13.setAlignment(QtCore.Qt.AlignCenter)
        self.label_13.setObjectName("label_13")
        self.horizontalLayout_7.addWidget(self.label_13)
        self.label_14 = QtWidgets.QLabel(self.groupBox_5)
        self.label_14.setAlignment(QtCore.Qt.AlignCenter)
        self.label_14.setObjectName("label_14")
        self.horizontalLayout_7.addWidget(self.label_14)
        self.label_15 = QtWidgets.QLabel(self.groupBox_5)
        self.label_15.setAlignment(QtCore.Qt.AlignCenter)
        self.label_15.setObjectName("label_15")
        self.horizontalLayout_7.addWidget(self.label_15)
        self.verticalLayout_17.addLayout(self.horizontalLayout_7)
        self.verticalLayout_18.addLayout(self.verticalLayout_17)
        self.groupBox_7 = QtWidgets.QGroupBox(self.groupBox_5)
        self.groupBox_7.setTitle("")
        self.groupBox_7.setObjectName("groupBox_7")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout(self.groupBox_7)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.label_22 = QtWidgets.QLabel(self.groupBox_7)
        self.label_22.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_22.setObjectName("label_22")
        self.horizontalLayout_10.addWidget(self.label_22)
        self.label_23 = QtWidgets.QLabel(self.groupBox_7)
        self.label_23.setText("")
        self.label_23.setAlignment(QtCore.Qt.AlignCenter)
        self.label_23.setObjectName("label_23")
        self.horizontalLayout_10.addWidget(self.label_23)
        self.label_24 = QtWidgets.QLabel(self.groupBox_7)
        self.label_24.setText("")
        self.label_24.setObjectName("label_24")
        self.horizontalLayout_10.addWidget(self.label_24)
        self.verticalLayout_7.addLayout(self.horizontalLayout_10)
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.label_25 = QtWidgets.QLabel(self.groupBox_7)
        self.label_25.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_25.setObjectName("label_25")
        self.horizontalLayout_13.addWidget(self.label_25)
        self.label_26 = QtWidgets.QLabel(self.groupBox_7)
        self.label_26.setText("")
        self.label_26.setAlignment(QtCore.Qt.AlignCenter)
        self.label_26.setObjectName("label_26")
        self.horizontalLayout_13.addWidget(self.label_26)
        self.label_27 = QtWidgets.QLabel(self.groupBox_7)
        self.label_27.setText("")
        self.label_27.setObjectName("label_27")
        self.horizontalLayout_13.addWidget(self.label_27)
        self.verticalLayout_7.addLayout(self.horizontalLayout_13)
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.label_28 = QtWidgets.QLabel(self.groupBox_7)
        self.label_28.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_28.setObjectName("label_28")
        self.horizontalLayout_14.addWidget(self.label_28)
        self.label_29 = QtWidgets.QLabel(self.groupBox_7)
        self.label_29.setText("")
        self.label_29.setAlignment(QtCore.Qt.AlignCenter)
        self.label_29.setObjectName("label_29")
        self.horizontalLayout_14.addWidget(self.label_29)
        self.label_30 = QtWidgets.QLabel(self.groupBox_7)
        self.label_30.setText("")
        self.label_30.setObjectName("label_30")
        self.horizontalLayout_14.addWidget(self.label_30)
        self.verticalLayout_7.addLayout(self.horizontalLayout_14)
        self.horizontalLayout_15 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.label_31 = QtWidgets.QLabel(self.groupBox_7)
        self.label_31.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_31.setObjectName("label_31")
        self.horizontalLayout_15.addWidget(self.label_31)
        self.label_32 = QtWidgets.QLabel(self.groupBox_7)
        self.label_32.setText("")
        self.label_32.setAlignment(QtCore.Qt.AlignCenter)
        self.label_32.setObjectName("label_32")
        self.horizontalLayout_15.addWidget(self.label_32)
        self.label_33 = QtWidgets.QLabel(self.groupBox_7)
        self.label_33.setText("")
        self.label_33.setObjectName("label_33")
        self.horizontalLayout_15.addWidget(self.label_33)
        self.verticalLayout_7.addLayout(self.horizontalLayout_15)
        self.horizontalLayout_16 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_16.setObjectName("horizontalLayout_16")
        self.label_64 = QtWidgets.QLabel(self.groupBox_7)
        self.label_64.setTextFormat(QtCore.Qt.AutoText)
        self.label_64.setScaledContents(False)
        self.label_64.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_64.setObjectName("label_64")
        self.horizontalLayout_16.addWidget(self.label_64)
        self.label_65 = QtWidgets.QLabel(self.groupBox_7)
        self.label_65.setText("")
        self.label_65.setAlignment(QtCore.Qt.AlignCenter)
        self.label_65.setObjectName("label_65")
        self.horizontalLayout_16.addWidget(self.label_65)
        self.label_66 = QtWidgets.QLabel(self.groupBox_7)
        self.label_66.setText("")
        self.label_66.setObjectName("label_66")
        self.horizontalLayout_16.addWidget(self.label_66)
        self.verticalLayout_7.addLayout(self.horizontalLayout_16)
        self.horizontalLayout_9.addLayout(self.verticalLayout_7)
        self.verticalLayout_20 = QtWidgets.QVBoxLayout()
        self.verticalLayout_20.setObjectName("verticalLayout_20")
        self.verticalLayout_22 = QtWidgets.QVBoxLayout()
        self.verticalLayout_22.setObjectName("verticalLayout_22")
        self.horizontalLayout_27 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_27.setObjectName("horizontalLayout_27")
        self.label_67 = QtWidgets.QLabel(self.groupBox_7)
        self.label_67.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_67.setObjectName("label_67")
        self.horizontalLayout_27.addWidget(self.label_67)
        self.label_68 = QtWidgets.QLabel(self.groupBox_7)
        self.label_68.setText("")
        self.label_68.setAlignment(QtCore.Qt.AlignCenter)
        self.label_68.setObjectName("label_68")
        self.horizontalLayout_27.addWidget(self.label_68)
        self.label_69 = QtWidgets.QLabel(self.groupBox_7)
        self.label_69.setText("")
        self.label_69.setObjectName("label_69")
        self.horizontalLayout_27.addWidget(self.label_69)
        self.verticalLayout_22.addLayout(self.horizontalLayout_27)
        self.horizontalLayout_28 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_28.setObjectName("horizontalLayout_28")
        self.label_70 = QtWidgets.QLabel(self.groupBox_7)
        self.label_70.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_70.setObjectName("label_70")
        self.horizontalLayout_28.addWidget(self.label_70)
        self.label_71 = QtWidgets.QLabel(self.groupBox_7)
        self.label_71.setText("")
        self.label_71.setAlignment(QtCore.Qt.AlignCenter)
        self.label_71.setObjectName("label_71")
        self.horizontalLayout_28.addWidget(self.label_71)
        self.label_72 = QtWidgets.QLabel(self.groupBox_7)
        self.label_72.setText("")
        self.label_72.setObjectName("label_72")
        self.horizontalLayout_28.addWidget(self.label_72)
        self.verticalLayout_22.addLayout(self.horizontalLayout_28)
        self.horizontalLayout_29 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_29.setObjectName("horizontalLayout_29")
        self.label_73 = QtWidgets.QLabel(self.groupBox_7)
        self.label_73.setTextFormat(QtCore.Qt.AutoText)
        self.label_73.setScaledContents(False)
        self.label_73.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_73.setObjectName("label_73")
        self.horizontalLayout_29.addWidget(self.label_73)
        self.label_74 = QtWidgets.QLabel(self.groupBox_7)
        self.label_74.setText("")
        self.label_74.setAlignment(QtCore.Qt.AlignCenter)
        self.label_74.setObjectName("label_74")
        self.horizontalLayout_29.addWidget(self.label_74)
        self.label_75 = QtWidgets.QLabel(self.groupBox_7)
        self.label_75.setText("")
        self.label_75.setObjectName("label_75")
        self.horizontalLayout_29.addWidget(self.label_75)
        self.verticalLayout_22.addLayout(self.horizontalLayout_29)
        self.horizontalLayout_30 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_30.setObjectName("horizontalLayout_30")
        self.label_76 = QtWidgets.QLabel(self.groupBox_7)
        self.label_76.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_76.setObjectName("label_76")
        self.horizontalLayout_30.addWidget(self.label_76)
        self.label_77 = QtWidgets.QLabel(self.groupBox_7)
        self.label_77.setText("")
        self.label_77.setAlignment(QtCore.Qt.AlignCenter)
        self.label_77.setObjectName("label_77")
        self.horizontalLayout_30.addWidget(self.label_77)
        self.label_78 = QtWidgets.QLabel(self.groupBox_7)
        self.label_78.setText("")
        self.label_78.setObjectName("label_78")
        self.horizontalLayout_30.addWidget(self.label_78)
        self.verticalLayout_22.addLayout(self.horizontalLayout_30)
        self.horizontalLayout_31 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_31.setObjectName("horizontalLayout_31")
        self.label_79 = QtWidgets.QLabel(self.groupBox_7)
        self.label_79.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_79.setObjectName("label_79")
        self.horizontalLayout_31.addWidget(self.label_79)
        self.label_80 = QtWidgets.QLabel(self.groupBox_7)
        self.label_80.setText("")
        self.label_80.setAlignment(QtCore.Qt.AlignCenter)
        self.label_80.setObjectName("label_80")
        self.horizontalLayout_31.addWidget(self.label_80)
        self.label_81 = QtWidgets.QLabel(self.groupBox_7)
        self.label_81.setText("")
        self.label_81.setObjectName("label_81")
        self.horizontalLayout_31.addWidget(self.label_81)
        self.verticalLayout_22.addLayout(self.horizontalLayout_31)
        self.horizontalLayout_32 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_32.setObjectName("horizontalLayout_32")
        self.label_82 = QtWidgets.QLabel(self.groupBox_7)
        self.label_82.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_82.setObjectName("label_82")
        self.horizontalLayout_32.addWidget(self.label_82)
        self.label_83 = QtWidgets.QLabel(self.groupBox_7)
        self.label_83.setText("")
        self.label_83.setAlignment(QtCore.Qt.AlignCenter)
        self.label_83.setObjectName("label_83")
        self.horizontalLayout_32.addWidget(self.label_83)
        self.label_84 = QtWidgets.QLabel(self.groupBox_7)
        self.label_84.setText("")
        self.label_84.setObjectName("label_84")
        self.horizontalLayout_32.addWidget(self.label_84)
        self.verticalLayout_22.addLayout(self.horizontalLayout_32)
        self.verticalLayout_20.addLayout(self.verticalLayout_22)
        self.horizontalLayout_9.addLayout(self.verticalLayout_20)
        self.verticalLayout_23 = QtWidgets.QVBoxLayout()
        self.verticalLayout_23.setObjectName("verticalLayout_23")
        self.horizontalLayout_33 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_33.setObjectName("horizontalLayout_33")
        self.label_85 = QtWidgets.QLabel(self.groupBox_7)
        self.label_85.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_85.setObjectName("label_85")
        self.horizontalLayout_33.addWidget(self.label_85)
        self.label_86 = QtWidgets.QLabel(self.groupBox_7)
        self.label_86.setText("")
        self.label_86.setAlignment(QtCore.Qt.AlignCenter)
        self.label_86.setObjectName("label_86")
        self.horizontalLayout_33.addWidget(self.label_86)
        self.label_87 = QtWidgets.QLabel(self.groupBox_7)
        self.label_87.setText("")
        self.label_87.setObjectName("label_87")
        self.horizontalLayout_33.addWidget(self.label_87)
        self.verticalLayout_23.addLayout(self.horizontalLayout_33)
        self.horizontalLayout_34 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_34.setObjectName("horizontalLayout_34")
        self.label_88 = QtWidgets.QLabel(self.groupBox_7)
        self.label_88.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_88.setObjectName("label_88")
        self.horizontalLayout_34.addWidget(self.label_88)
        self.label_89 = QtWidgets.QLabel(self.groupBox_7)
        self.label_89.setText("")
        self.label_89.setAlignment(QtCore.Qt.AlignCenter)
        self.label_89.setObjectName("label_89")
        self.horizontalLayout_34.addWidget(self.label_89)
        self.label_90 = QtWidgets.QLabel(self.groupBox_7)
        self.label_90.setText("")
        self.label_90.setObjectName("label_90")
        self.horizontalLayout_34.addWidget(self.label_90)
        self.verticalLayout_23.addLayout(self.horizontalLayout_34)
        self.horizontalLayout_35 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_35.setObjectName("horizontalLayout_35")
        self.label_91 = QtWidgets.QLabel(self.groupBox_7)
        self.label_91.setTextFormat(QtCore.Qt.AutoText)
        self.label_91.setScaledContents(False)
        self.label_91.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_91.setObjectName("label_91")
        self.horizontalLayout_35.addWidget(self.label_91)
        self.label_92 = QtWidgets.QLabel(self.groupBox_7)
        self.label_92.setText("")
        self.label_92.setAlignment(QtCore.Qt.AlignCenter)
        self.label_92.setObjectName("label_92")
        self.horizontalLayout_35.addWidget(self.label_92)
        self.label_93 = QtWidgets.QLabel(self.groupBox_7)
        self.label_93.setText("")
        self.label_93.setObjectName("label_93")
        self.horizontalLayout_35.addWidget(self.label_93)
        self.verticalLayout_23.addLayout(self.horizontalLayout_35)
        self.horizontalLayout_36 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_36.setObjectName("horizontalLayout_36")
        self.label_94 = QtWidgets.QLabel(self.groupBox_7)
        self.label_94.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_94.setObjectName("label_94")
        self.horizontalLayout_36.addWidget(self.label_94)
        self.label_95 = QtWidgets.QLabel(self.groupBox_7)
        self.label_95.setText("")
        self.label_95.setAlignment(QtCore.Qt.AlignCenter)
        self.label_95.setObjectName("label_95")
        self.horizontalLayout_36.addWidget(self.label_95)
        self.label_96 = QtWidgets.QLabel(self.groupBox_7)
        self.label_96.setText("")
        self.label_96.setObjectName("label_96")
        self.horizontalLayout_36.addWidget(self.label_96)
        self.verticalLayout_23.addLayout(self.horizontalLayout_36)
        self.horizontalLayout_37 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_37.setObjectName("horizontalLayout_37")
        self.label_97 = QtWidgets.QLabel(self.groupBox_7)
        self.label_97.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_97.setObjectName("label_97")
        self.horizontalLayout_37.addWidget(self.label_97)
        self.label_98 = QtWidgets.QLabel(self.groupBox_7)
        self.label_98.setText("")
        self.label_98.setAlignment(QtCore.Qt.AlignCenter)
        self.label_98.setObjectName("label_98")
        self.horizontalLayout_37.addWidget(self.label_98)
        self.label_99 = QtWidgets.QLabel(self.groupBox_7)
        self.label_99.setText("")
        self.label_99.setObjectName("label_99")
        self.horizontalLayout_37.addWidget(self.label_99)
        self.verticalLayout_23.addLayout(self.horizontalLayout_37)
        self.horizontalLayout_9.addLayout(self.verticalLayout_23)
        self.verticalLayout_18.addWidget(self.groupBox_7)
        self.groupBox_6 = QtWidgets.QGroupBox(self.groupBox_5)
        self.groupBox_6.setObjectName("groupBox_6")
        self.verticalLayout_19 = QtWidgets.QVBoxLayout(self.groupBox_6)
        self.verticalLayout_19.setObjectName("verticalLayout_19")
        self.tableWidget = QtWidgets.QTableWidget(self.groupBox_6)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(5, item)
        self.verticalLayout_19.addWidget(self.tableWidget)
        self.verticalLayout_18.addWidget(self.groupBox_6)
        self.verticalLayout_14.addWidget(self.groupBox_5)
        self.verticalLayout_5.addLayout(self.verticalLayout_14)
        self.horizontalLayout.addWidget(self.groupBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "OddsBK"))
        self.pushButton.setText(_translate("MainWindow", "PushButton"))
        self.label_3.setText(_translate("MainWindow", "Всего игр в базе:"))
        self.groupBox_3.setTitle(_translate("MainWindow", "Букмекеры"))
        self.groupBox.setTitle(_translate("MainWindow", "Поиск совпадений"))
        self.label_4.setText(_translate("MainWindow", "П1"))
        self.label_6.setText(_translate("MainWindow", "Х"))
        self.label_5.setText(_translate("MainWindow", "П2"))
        self.pushButton_4.setText(_translate("MainWindow", "Найти совпадения"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Результат"))
        self.label_7.setText(_translate("MainWindow", "Найдено матчей:"))
        self.label_9.setText(_translate("MainWindow", "П1:"))
        self.label_10.setText(_translate("MainWindow", "X:"))
        self.label_8.setText(_translate("MainWindow", "П2:"))
        self.pushButton_5.setText(_translate("MainWindow", "Показать матчи"))
        self.groupBox_4.setTitle(_translate("MainWindow", "Поиск совпадений по предстоящему матчу"))
        self.label_11.setText(_translate("MainWindow", "Ссылка"))
        self.pushButton_6.setText(_translate("MainWindow", "Найти совпадения"))
        self.groupBox_5.setTitle(_translate("MainWindow", "Результат"))
        self.label_12.setText(_translate("MainWindow", "Найдено матчей:"))
        self.label_13.setText(_translate("MainWindow", "П1:"))
        self.label_14.setText(_translate("MainWindow", "X:"))
        self.label_15.setText(_translate("MainWindow", "П2:"))
        self.label_22.setText(_translate("MainWindow", "-0.5к1:"))
        self.label_25.setText(_translate("MainWindow", "-1.5к1:"))
        self.label_28.setText(_translate("MainWindow", "-2.5к1:"))
        self.label_31.setText(_translate("MainWindow", "-3.5к1:"))
        self.label_64.setText(_translate("MainWindow", "-4.5к1:"))
        self.label_67.setText(_translate("MainWindow", "X:"))
        self.label_70.setText(_translate("MainWindow", "ОЗ да:"))
        self.label_73.setText(_translate("MainWindow", "ТБ 0.5:"))
        self.label_76.setText(_translate("MainWindow", "ТБ 1.5:"))
        self.label_79.setText(_translate("MainWindow", "ТБ 2.5:"))
        self.label_82.setText(_translate("MainWindow", "ТБ 3.5:"))
        self.label_85.setText(_translate("MainWindow", "-0.5к2:"))
        self.label_88.setText(_translate("MainWindow", "-1.5к2:"))
        self.label_91.setText(_translate("MainWindow", "-2.5к2:"))
        self.label_94.setText(_translate("MainWindow", "-3.5к2:"))
        self.label_97.setText(_translate("MainWindow", "-4.5к2:"))
        self.groupBox_6.setTitle(_translate("MainWindow", "Букмекеры"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Букмекер"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Количество матчей"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "П1"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "X"))
        item = self.tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "П2"))
        item = self.tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "Показать матчи"))
