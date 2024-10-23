from pyqtgraph.Qt import QtGui, QtWidgets, QtCore
import numpy as np
import pyqtgraph as pg

pg.setConfigOptions(antialias=True)  # 启用抗锯齿选项


def pg_plotitem_plot():
    """
    绘制折线图
    """
    app = pg.mkQApp()
    win = pg.GraphicsView()
    layout = pg.GraphicsLayout(border=(100, 100, 100))
    win.setCentralItem(layout)
    win.show()

    plot = layout.addPlot()
    y = 50
    height = 100
    color = pg.mkColor(255, 0, 0)

    hLine_up = pg.InfiniteLine(pos=y - 20, angle=0, pen=pg.mkPen(color, width=1))
    hLine_down = pg.InfiniteLine(pos=y + height + 20, angle=0, pen=pg.mkPen(color, width=1))
    plot.addItem(hLine_up)
    plot.addItem(hLine_down)
    app.exec()


if __name__ == '__main__':
    pg_plotitem_plot()
