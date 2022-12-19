from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QApplication
import sys
sys.path.insert(1, r'C:\Users\MERT ÜNÜBOL\Desktop\SİHA-Workspace\Glados_yolov5_plane_detection_training\src\maximum_roverdrive\images')
# I HATE THIS - PyQt5 doesn't allow you to style a QCheckbox without importing custom images to overlay
import images


class QAppMPLookAndFeel(QApplication):
    def __init__(self, args):
        super(QAppMPLookAndFeel, self).__init__(args)
        self.apply_style()

    def apply_style(self):
        self.setStyle('Fusion')
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(38, 39, 40))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(38, 39, 40))
        dark_palette.setColor(QPalette.AlternateBase, QColor(38, 39, 40))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, QColor(221, 221,221))
        dark_palette.setColor(QPalette.ButtonText, QColor(64, 87, 4))
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(dark_palette)
        self.setStyleSheet('QWidget { font-family: "Segue UI", sans-serif; font-size: 12px; }'
                           'QTabWidget>QWidget{ background-color: rgb(38, 39, 40); }'
                           'QFrame { border: 1px solid #515253; }'
                           'QFrame[objectName=mav_command_start] { border: 3px solid #185927; border-radius: 5px; }'
                           'QFrame[objectName=mav_command_start] > QLineEdit'
                           '{ border: 1px solid #185927; border-radius: 3px; }'
                           'QFrame[objectName=mav_command_start] > QLineEdit:disabled'
                           '{ border: 1px solid #38393a; border-radius: 3px; }'
                           'QFrame[objectName=mav_command_start] > QLineEdit:focus'
                           '{ border: 1px solid #53a0ed; border-radius: 3px; }'
                           'QFrame[objectName=mav_command_start] > QComboBox'
                           '{ color: white; border: 1px solid #185927; border-radius: 3px; }'
                           'QFrame[objectName=mav_command_start] > QComboBox:disabled'
                           '{ border: 1px solid #38393a; border-radius: 3px; }'
                           'QFrame[objectName=mav_command_start] > QComboBox:focus'
                           '{ border: 1px solid #53a0ed; border-radius: 3px; }'
                           'QFrame[objectName=mav_command_end] { border: 3px solid #856404; border-radius: 5px }'
                           'QFrame[objectName=mav_command_end] > QLineEdit'
                           '{ border: 1px solid #856404; border-radius: 3px; }'
                           'QFrame[objectName=mav_command_end] > QLineEdit:disabled'
                           '{ border: 1px solid #38393a; border-radius: 3px; }'
                           'QFrame[objectName=mav_command_end] > QLineEdit:focus'
                           '{ border: 1px solid #53a0ed; border-radius: 3px; }'
                           'QFrame[objectName=mav_command_end] > QComboBox'
                           '{ color: white; border: 1px solid #856404; border-radius: 3px; }'
                           'QFrame[objectName=mav_command_end] > QComboBox:disabled'
                           '{ border: 1px solid #38393a; border-radius: 3px; }'
                           'QFrame[objectName=mav_command_end] > QComboBox:focus'
                           '{ border: 1px solid #53a0ed; border-radius: 3px; }'
                           'QLabel { border: 0px; }'
                           'QLabel[objectName=label_about] { qproperty-alignment: AlignCenter; '
                           'text-decoration: underline; }'
                           'QLabel[objectName=label_arg] { qproperty-alignment: AlignCenter; }'
                           'QLineEdit[objectName=text_arg] { qproperty-alignment: AlignCenter; }'
                           'QLineEdit { border: 1px solid #515253; }'
                           'QLineEdit:focus { border: 1px solid #53a0ed; }'
                           'QTextEdit { border: 1px solid #515253; }'
                           'QTextEdit:focus { border: 1px solid #53a0ed; }'
                           'QToolTip { color: white; background-color: #515253; border: 1px solid  #4592df; }'
                           'QTableView { font-family: "Consolas", fixed;  font-size: 14px; '
                           'border: 1px solid #515253; gridline-color: #515253; }'
                           'QCheckBox:indicator:unchecked { image: url(:/images/unchecked.png); }'
                           'QCheckBox:indicator:unchecked:hover { image: url(:/images/unchecked_hover.png); }'
                           'QCheckBox:indicator:unchecked:pressed { image: url(:/images/unchecked_pressed.png); }'
                           'QCheckBox:indicator:checked { image: url(:/images/checked.png); }'
                           'QCheckBox:indicator:checked:hover { image: url(:/images/checked_hover.png); }'
                           'QCheckBox:indicator:checked:pressed { image: url(:/images/checked_pressed.png); }'
                           'QPushButton { min-height: 21px; padding-left: 7px; padding-right: 7px; '
                           'border: 0px; border-radius: 2px; border-color: #405704; background: '
                           'qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #97c224, stop: 1 #c8df8c); }'
                           'QPushButton:hover { background:'
                           'qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #789b1b, stop: 1 #9bb065); }'
                           'QPushButton:pressed { background:'
                           'qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #628014, stop: 1 #7b8f49); }')