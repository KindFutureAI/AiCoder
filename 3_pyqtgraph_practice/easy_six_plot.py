import pyqtgraph as pg
import numpy as np

x = np.random.random(50)
a = np.random.random(8)


# 最简单直接的plot()
def pg_plot():
    app = pg.QtWidgets.QApplication([])
    pg.plot(x, title='PyQtGraph教程 - plot()方法')
    app.exec()


# 运行函数，我们将会得到两个图形窗口
def pg_plot2():
    app = pg.QtWidgets.QApplication([])
    pg.plot(x, title='PyQtGraph教程 - plot()方法 x数组')
    pg.plot(a, title='PyQtGraph教程 - plot()方法 a数组')
    app.exec()


# 使用plot()方法在同一个图形中绘制多个数据，
def pg_plot2_add():
    # 需要先将pyqtgraph的plot()方法实例化，
    # 然后再使用实例化后的plot的plot()方法进行图形绘制
    app = pg.QtWidgets.QApplication([])
    plot = pg.plot(title='PyQtGraph教程 - plot()方法')
    plot.plot(x, pen='r')
    plot.plot(a, pen='g')
    app.exec()


# 使用pyqtgraph的GraphicsView和GraphicsLayout方法绘制图形
def pg_graphic_win_plot():
    """
    GraphicsView和GraphicsLayout方法绘制图形

    通过GraphicsLayout图形层方法绘制图形的过程相较于前述的方法，稍显复杂。
    首先通过实例化pyqtgraph的GraphicsView()方法，创建一个图形视图；
    然后通过实例化pyqtgraph的GraphicsLayout()方法，创建一个图形层；
    再设置图形视图的中心层为刚刚创建的图形层，并设置显示图形视图。
    最后使用图形层的addplot()方法添加一个图形，再将使用图形的plot()方法将图形绘制出来。
    """
    app = pg.QtWidgets.QApplication([])
    view = pg.GraphicsLayoutWidget()
    layout = pg.GraphicsLayout()

    view.setCentralItem(layout)
    view.show()

    p1 = layout.addPlot(title='PyQtGraph教程 - 通过图形层绘制图形')
    p1.plot(x)

    app.exec()


# 使用PlotWidget绘制图形
def pg_plotwidget_plot():
    # 使用pyqtgraph的PlotWidget方法绘制图形与直接使用plot()方法绘制图形有些许类似
    app = pg.QtWidgets.QApplication([])
    plot_wit = pg.PlotWidget(title='PyQtGraph教程 - PlotWidget绘制图形')
    plot_wit.plot(x)
    plot_wit.show()
    app.exec()


# 通过PlotItem方法绘制图形
def pg_plotitem_plot():
    # 使用pyqtgraph的PlotItem方法绘制图形
    app = pg.QtWidgets.QApplication([])
    view = pg.GraphicsView()
    plot_item = pg.PlotItem(title='PyQtGraph教程 - PlotItem绘制图形')
    plot_item.plot(x)
    # view.setCentralItem(plot_item)  # 这个也可以的
    view.setCentralWidget(plot_item)
    view.show()
    app.exec()

def datetime_axis():
    from datetime import datetime, timedelta
    app = pg.mkQApp()
    # 示例数据：X轴为datetime，Y轴为随机数值
    x_data = [datetime(2022, 3, 1) + timedelta(days=i) for i in range(7)]
    y_data = [np.random.rand() for _ in x_data]
    # 将datetime对象转换为Unix时间戳（浮点数）
    x_data_timestamps = np.array([timestamp.timestamp() for timestamp in x_data])

    # 创建图形视图和绘图项
    view = pg.GraphicsView()
    layout = pg.GraphicsLayout()
    view.setCentralItem(layout)
    plot = layout.addPlot(title="Datetime on X-Axis")


    # 设置X轴为DateAxisItem
    x_axis = pg.DateAxisItem(orientation='bottom')
    plot.setAxisItems({'bottom': x_axis})

    # 显示图形视图
    view.show()
    # 添加数据到图表
    plot.plot(x=x_data_timestamps, y=y_data, pen='r')
    app.exec()

if __name__ == '__main__':
    # pg_plot()
    # pg_plot2()
    # pg_plot2_add()
    # pg_graphic_win_plot()
    # pg_plotwidget_plot()
    # pg_plotitem_plot()
    datetime_axis()
