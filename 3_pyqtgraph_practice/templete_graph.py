# 导入必要的库
import pyqtgraph as pg
import tushare as ts
import numpy as np

# 使用tushare模块获取上证指数的历史数据
# 参数为指数代码和起止日期，返回一个经过排序的DataFrame对象
# data = ts.get_hist_data('sh', start='2018-01-01', end='2018-02-01').sort_index(ascending=True)

# 处理获取的数据，以便于设置坐标轴刻度文本
# # 将日期索引转换为字典，并提取部分日期作为坐标轴刻度
# xdict = dict(enumerate(data.index))
# axis_1 = [(i, list(data.index)[i]) for i in range(0, len(data.index), 5)]

# 创建PyQtGraph应用程序和图形界面
app = pg.mkQApp("这是一个测试app")

# 构建图形布局和视图
layout = pg.GraphicsLayout()
view = pg.GraphicsView()
view.setCentralItem(layout)
view.show()

# # 创建自定义字符串坐标轴
# stringaxis = pg.AxisItem(orientation='bottom')
# stringaxis.setTicks([axis_1, xdict.items()])

# 在布局中添加绘图窗口，并设置标题和坐标轴项目
plot = layout.addPlot(row=0, col=0,  title='上证指数')

# 添加标题和图例
label = pg.TextItem()
label.setText('上证指数')
plot.addItem(label)
plot.addLegend(size=(150, 80))

# 显示网格和数据
plot.showGrid(x=True, y=True, alpha=0.3)
plot.plot(x=np.random.random(50), y=np.random.random(50), pen='r', name='开盘指数', symbolBrush=(255, 0, 0), )
plot.plot(x=np.random.random(50), y=np.random.random(50), pen='g', name='收盘指数', symbolBrush=(0, 255, 0))

# 设置坐标轴标签
plot.setLabel(axis='left', text='指数')
plot.setLabel(axis='bottom', text='日期')

# 添加水平和垂直无限直线，用于鼠标移动时的标记
vLine = pg.InfiniteLine(angle=90, movable=False, )
hLine = pg.InfiniteLine(angle=0, movable=False, )
plot.addItem(vLine, ignoreBounds=True)
plot.addItem(hLine, ignoreBounds=True)
vb = plot.vb


def mouseMoved(evt):
    # 鼠标移动时的处理函数
    pos = evt[0]
    if plot.sceneBoundingRect().contains(pos):
        mousePoint = vb.mapSceneToView(pos)
        index = int(mousePoint.x())
        pos_y = int(mousePoint.y())
        print(index)
        # if 0 < index < len(data.index):
        #     # 打印并更新当前鼠标位置对应的日期和指数值
        #     print(xdict[index], data['open'][index], data['close'][index])
        #     label.setHtml(
        #         "<p style='color:white'>日期：{0}</p><p style='color:white'>开盘：{1}</p><p style='color:white'>收盘：{2}</p>".format(
        #             xdict[index], data['open'][index], data['close'][index]))
        #     label.setPos(mousePoint.x(), mousePoint.y())
        vLine.setPos(mousePoint.x())
        hLine.setPos(mousePoint.y())


proxy = pg.SignalProxy(plot.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)

app.exec()