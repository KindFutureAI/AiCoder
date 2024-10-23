import pyqtgraph as pg

app = pg.mkQApp()
## 创建绘图窗口和GraphicsLayoutWidget
view = pg.GraphicsView()
layout_widget = pg.GraphicsLayout()
view.setCentralItem(layout_widget)
view.show()

## 添加多个PlotItem
plot1 = layout_widget.addPlot(0, 0)
plot2 = layout_widget.addPlot(0, 1)
plot3 = layout_widget.addPlot(1, 0, rowspan=2, colspan=1)
plot4 = layout_widget.addPlot(1, 1)
plot5 = layout_widget.addPlot(2, 1)
plot6 = layout_widget.addPlot(3, 0, rowspan=1, colspan=2)

## 设置网格中相邻项目的间距和网格的边距
layout_widget.setSpacing(10)
layout_widget.setContentsMargins(20, 20, 20, 20)

## 在每个PlotItem中添加数据
plot1.plot([1, 2, 3, 4, 5], [1, 2, 3, 2, 1])
plot2.plot([1, 2, 3, 4, 5], [1, 4, 9, 16, 25])
plot3.plot([1, 2, 3, 4, 5], [1, 2, 1, 2, 1])
plot4.plot([1, 2, 3, 4, 5], [1, 3, 2, 4, 3])
plot5.plot([1, 2, 3, 4, 5], [1, 3, 2, 4, 3])
plot6.plot([1, 2, 3, 4, 5], [1, 3, 2, 4, 3])

app.exec()