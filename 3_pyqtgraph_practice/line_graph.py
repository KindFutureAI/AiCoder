from pyqtgraph.Qt import QtGui, QtWidgets, QtCore
import numpy as np
import pyqtgraph as pg

pg.setConfigOptions(antialias=True)  # 启用抗锯齿选项


def pg_plotitem_plot():
    """
    绘制折线图
    """
    app = QtWidgets.QApplication([])
    win = pg.GraphicsView()
    layout = pg.GraphicsLayout(border=(100, 100, 100))
    win.setCentralItem(layout)
    win.show()

    plot1 = layout.addPlot(title='Plot 1')
    plot1.plot([1, 2, 3, 4, 5, 6],
               [0, 1, 0, 1, 0, 1],
               pen='r',
               symbol='o',
               symbolPen='w',
               symbolBrush='r')

    # 换行
    layout.nextRow()
    plot2 = layout.addPlot(title='Plot 3')
    plot2.showGrid(x=True, y=True, alpha=0.5)
    plot2.plot(
        np.cos(np.linspace(0, 10 * np.pi, 100)),
        np.sin(np.linspace(0, 10 * np.pi, 100))
    )

    # 换行
    layout.nextRow()
    plot3 = layout.addPlot(title='Plot 2')
    plot3.plot(np.random.normal(size=100), pen='r', symbol='o', symbolSize=8)
    plot3.plot(np.random.normal(size=100) + 5, pen='r', symbol='o', symbolSize=8)
    plot3.plot(np.random.normal(size=100) + 10, pen='r', symbol='o', symbolSize=8)

    layout.nextRow()
    plot4 = layout.addPlot(title='Plot 4')

    x = np.random.normal(size=1000) * 1e-5  # 生成X轴数据
    y = x * 1000 + 0.005 * np.random.normal(size=1000)  # 生成Y轴数据
    y -= y.min() - 1.0
    mask = x > 1e-15
    x = x[mask]
    y = y[mask]

    plot4.plot(x, y, pen='r', symbol='o', symbolSize=8)
    plot4.setLabel('left', 'Y Axis', units='A')
    plot4.setLabel('bottom', 'X Axis', units='A')
    plot4.setLogMode(x=True, y=True)

    layout.nextRow()
    plot5 = layout.addPlot(title="绘图数据更新")
    curve = plot5.plot()  # 图形使用黄色画笔进行绘制
    data = np.random.normal(size=(10, 1000))  # 生成随机数据
    ptr = 0  # 初始为0

    # 定义一个更新函数
    def update():
        global curve, data, ptr, plot5
        curve.setData(data[ptr % 10])  # 设置图形的数据值
        if ptr == 0:
            plot5.enableAutoRange('xy', False)  ## 在第一个图形绘制的时候停止自动缩放
        ptr += 1

    timer = QtCore.QTimer()  # 实例化一个计时器
    timer.timeout.connect(update)  # 计时器信号连接到update()函数
    timer.start(200)  # 计时器间隔200毫秒


    app.exec()


if __name__ == '__main__':
    pg_plotitem_plot()
