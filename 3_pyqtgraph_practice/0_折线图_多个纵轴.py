"""
本专题的绘图均采用 PySide6 QWidget + pyqtgraph PlotWidget 的方式
目的是为了将图像嵌入UI界面中，包括父子关系和信号传递的技巧分享
"""
import random
import sys
import time

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication
import pyqtgraph as pg


class Figure(pg.PlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 背景默认使用黑色

        # 定义y1~y4
        self.y1 = pg.AxisItem('right')
        self.y1.setLabel('y1', color='blue')
        self.y1.setPen('blue')

        self.y2 = pg.AxisItem('right')
        self.y2.setLabel('y2', color='red')
        self.y2.setPen('red')

        self.y3 = pg.AxisItem('right')
        self.y3.setLabel('y3', color='green')
        self.y3.setPen('green')

        self.y4 = pg.AxisItem('right')
        self.y4.setLabel('y4', color='yellow')
        self.y4.setPen('yellow')

        # 定义v1~v4
        self.v1 = pg.ViewBox()
        self.v2 = pg.ViewBox()
        self.v3 = pg.ViewBox()
        self.v4 = pg.ViewBox()

        # 创建布局
        lay = pg.GraphicsLayout()
        self.setCentralWidget(lay)

        # p0 作为主要视窗, vp0是它的 ViewBox
        self.p0 = pg.PlotItem()
        # p0 从界面获取主要纵坐标y0
        self.p0.getAxis('left').setLabel('y0', color='white')
        self.p0.getAxis('left').setPen('white')
        self.vp0 = self.p0.vb
        # 主视窗的变化链接到所有视窗的绑定函数
        self.vp0.sigResized.connect(self.update)

        # 从左到右排布纵坐标轴
        # 关键点在于 p0 放在第二列，p0 的纵坐标 y0 放在第一列
        lay.addItem(self.p0, row=1, col=2, rowspan=2, colspan=1)
        lay.addItem(self.p0.getAxis('left'), row=1, col=1)

        # y1~y4的位置
        lay.addItem(self.y1, row=1, col=3, rowspan=1, colspan=1)
        lay.addItem(self.y2, row=1, col=4, rowspan=1, colspan=1)
        lay.addItem(self.y3, row=1, col=5, rowspan=1, colspan=1)
        lay.addItem(self.y4, row=1, col=6, rowspan=1, colspan=1)

        # 新建一个空横轴，注意颜色一定要与画布背景颜色一致，才能隐藏该轴
        x_ept = pg.AxisItem('bottom')
        # !!!!!!! 空轴千万不能设置标签（本身隐藏也没必要），否则会导致纵坐标零点错位，本教程做无用功
        # 如下语句若启用则纵坐标零点错位，可以对比运行试试
        # x_ept.setLabel('x_emp', color='black')
        x_ept.setPen('black')
        # 空轴的列（col）可以换成其他，不妨自己尝试更改下看看效果
        lay.addItem(x_ept, row=2, col=10)

        # 这里建议用布局添加标签的方式间接给横坐标轴标签，但是得用 HTML 语言
        lay.addLabel("<p style='color:white;'>风量 [m\u00b3/h]<\p>", 3, 2)

        # 布局场景添加 v1~v4
        lay.scene().addItem(self.v1)
        lay.scene().addItem(self.v2)
        lay.scene().addItem(self.v3)
        lay.scene().addItem(self.v4)

        # 将 y1~y4 绑定到 v1~v4
        self.y1.linkToView(self.v1)
        self.y2.linkToView(self.v2)
        self.y3.linkToView(self.v3)
        self.y4.linkToView(self.v4)

        # 将 v1~v4 的横坐标关联到主要视窗 vp0
        self.v1.setXLink(self.vp0)
        self.v2.setXLink(self.vp0)
        self.v3.setXLink(self.vp0)
        self.v4.setXLink(self.vp0)

        # 绘图函数
        # self.draw()
        self.x = []
        self.y0 = []
        self.y1 = []
        self.y2 = []
        self.y3 = []
        self.y4 = []
        timer = QTimer(self)
        timer.timeout.connect(self.draw)
        timer.start(1000)

    def draw(self):
        # 偷懒就将所有曲线坐标相等了，运行程序后可以自己拖动坐标轴分开
        timestamp = time.time()
        self.x.append(timestamp)
        # y0 = y1 = y2 = y3 = y4 = x
        self.y0.append(random.randint(17, 20))
        self.y1.append(random.randint(255, 280))
        self.y2.append(random.randint(2, 10))
        self.y3.append(random.randint(100, 150))
        self.y4.append(random.randint(1112, 1500))

        self.vp0.addItem(pg.PlotCurveItem(self.x, self.y0, pen=pg.mkPen(color='white', width=2)))
        self.v1.addItem(pg.PlotCurveItem(self.x, self.y1, pen=pg.mkPen(color='blue', width=2)))
        self.v2.addItem(pg.PlotCurveItem(self.x, self.y2, pen=pg.mkPen(color='red', width=2)))
        self.v3.addItem(pg.PlotCurveItem(self.x, self.y3, pen=pg.mkPen(color='green', width=2)))
        self.v4.addItem(pg.PlotCurveItem(self.x, self.y4, pen=pg.mkPen(color='yellow', width=2)))

    def update(self):
        # 所有视窗位置绑定到主要视窗 vp0， 若无则布局错乱
        self.v1.setGeometry(self.vp0.sceneBoundingRect())
        self.v2.setGeometry(self.vp0.sceneBoundingRect())
        self.v3.setGeometry(self.vp0.sceneBoundingRect())
        self.v4.setGeometry(self.vp0.sceneBoundingRect())


# PySide6 中定义 QWidget，用于嵌入上述 PlotWidget
class WidgetWindow(QWidget):
    def __init__(self):
        super().__init__()

        # 简单设置下窗口尺寸
        self.resize(500, 500)

        # 导入PlotWidget类， 用self写作类变量是为了扩展处理数据方便
        # Figure(self)是将WidgetWindow定义为Figure的父项
        self.cuv = Figure(self)

        # 创建一个垂直布局，并将self.cuv添加进去
        layout = QVBoxLayout()
        layout.addWidget(self.cuv)
        self.setLayout(layout)

        # 至此，WidgetWindow已经嵌入了Figure， 即PlotWidget， 下面运行程序
        # **************************************************************END


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = WidgetWindow()
    win.show()
    sys.exit(app.exec())