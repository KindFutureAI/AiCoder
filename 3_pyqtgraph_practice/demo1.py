from PySide6 import QtWidgets
from PySide6.QtWidgets import QPushButton

import pyqtgraph as pg
import numpy as np
import sys


# 主窗口类
class MainWidget(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(800, 600)
        self.setWindowTitle("DEMODEMODEMO")  # 设置窗口标题
        main_layout = QtWidgets.QVBoxLayout()  # 实例化一个网格布局层
        main_widget = QtWidgets.QWidget()  # 实例化一个widget部件
        main_widget.setLayout(main_layout)  # 设置主widget部件的布局为网格布局

        # data = np.random.random(40)
        # pw = pg.PlotWidget()
        # pw.plot(data)
        # main_layout.addWidget(pw, 0, 0)

        self.setCentralWidget(main_widget)  # 设置窗口默认部件为主widget
        # 创建最小化、最大化和关闭按钮实例
        # self.minBtn = QPushButton(parent=self)
        # self.closeBtn = QPushButton(parent=self)
        # self.maxBtn = QPushButton(parent=self)
        # main_layout.addWidget(self.minBtn, 1, 0)
        # main_layout.addWidget(self.maxBtn, 1, 1)
        # main_layout.addWidget(self.closeBtn, 1, 2)

        color_dict = {
            "Red": "#F44336",  # 红色
            "Pink": "#F48FB1",  # 粉色
            "Purple": "#CE93D8",  # 紫色
            "DeepPurple": "#B39DDB",  # 深紫色
            "Indigo": "#9FA8DA",  # 靛蓝
            "Blue": "#90CAF9",  # 蓝色
            "LightBlue": "#81D4FA",  # 浅蓝色
            "Cyan": "#80DEEA",  # 青色
            "Teal": "#80CBC4",  # 蓝绿色
            "Green": "#A5D6A7",  # 绿色
            "LightGreen": "#C5E1A5",  # 浅绿色
            "Lime": "#ADBF00",  # 酸橙绿
            "Yellow": "#F57F17",  # 黄色
            "Amber": "#D76501",  # 琥珀色
            "Orange": "#D98200",  # 橙色
            "DeepOrange": "#FFAB91",  # 深橙色
            "Brown": "#BCAAA4",  # 棕色
            "Grey": "#EEEEEE",  # 灰色
            "BlueGrey": "#B0BEC5",  # 蓝灰色
        }
        color_dict2 = {
            "Red": "#B71C1C",  # 红色
            "Pink": "#FCE4EC",  # 粉色
            "Purple": "#4A148C",  # 紫色
            "DeepPurple": "#311B92",  # 深紫色
            "Indigo": "#1A237E",  # 靛蓝
            "Blue": "#0D47A1",  # 蓝色
            "LightBlue": "#01579B",  # 浅蓝色
            "Cyan": "#006064",  # 青色
            "Teal": "#004D40",  # 蓝绿色
            "Green": "#004D40",  # 绿色
            "LightGreen": "#33691E",  # 浅绿色
            "Lime": "#827717",  # 酸橙绿
            "Yellow": "#F57F17",  # 黄色
            "Amber": "#FF6F00",  # 琥珀色
            "Orange": "#E65100",  # 橙色
            "DeepOrange": "#BF360C",  # 深橙色
            "Brown": "#3E2723",  # 棕色
            "Grey": "#212121",  # 灰色
            "BlueGrey": "#263238",  # 蓝灰色

        }
        for key, value in color_dict.items():
            button = QPushButton(key)
            button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            button.setStyleSheet(f"background-color: {value};")
            main_layout.addWidget(button)

        for key, value in color_dict2.items():
            button = QPushButton(key)
            button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            button.setStyleSheet(f"background-color: {value};")
            main_layout.addWidget(button)

        # 连接按钮点击信号与对应的槽函数
        # self.minBtn.clicked.connect(self.showMinimized)
        # self.maxBtn.clicked.connect(self.__toggleMaxState)
        # self.closeBtn.clicked.connect(self.close)

    def __toggleMaxState(self):
        # 根据窗口当前是否最大化来决定是还原还是最大化窗口
        if self.window().isMaximized():
            self.window().showNormal()
        else:
            self.window().showMaximized()


# 运行函数
def main():
    app = QtWidgets.QApplication(sys.argv)
    gui = MainWidget()
    gui.show()
    sys.exit(app.exec())


main()
