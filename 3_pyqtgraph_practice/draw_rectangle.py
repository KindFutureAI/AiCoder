from PySide6.QtCore import QRectF, Qt
from PySide6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QVBoxLayout, QWidget, QGraphicsItem
from PySide6.QtGui import QPicture, QPainter, QPen, QColor, QImage, QPixmap

import pyqtgraph as pg


class FillItem(pg.GraphicsObject):
    """ 一个用于填充图形的图形对象类。 """

    x = 0
    y = 0
    w = 0
    h = 0
    line_style = None

    def __init__(self, color, line_style=Qt.PenStyle.SolidLine):
        """ 初始化填充图形对象。

        :param color: 填充颜色。
        :param line_style: 边框线样式，默认为实线。
        """
        pg.GraphicsObject.__init__(self)
        self.picture = QPicture()  # 初始化图片对象
        self.color = color
        self.line_style = line_style

    def setRect(self, _x, _y, _w, _h):
        """ 设置填充图形的矩形区域。  """
        self.x = _x
        self.y = _y
        self.w = _w
        self.h = _h
        self.generate_picture()  # 生成新的图片对象

    def generate_picture(self):
        """ 使用指定的属性生成填充图形的图片。  """
        p = QPainter(self.picture)  # 创建画笔对象
        p.setRenderHint(QPainter.Antialiasing)  # 设置抗锯齿

        p.setPen(pg.mkPen(color=(0, 0, 0, 50), width=1, style=self.line_style))  # 设置边框线
        p.setBrush(pg.mkBrush(color=self.color))  # 设置填充颜色

        rect = QRectF(self.x, self.y, self.w, self.h)  # 创建矩形区域
        p.drawRect(rect)  # 绘制矩形
        p.end()  # 结束画笔

    def paint(self, p: QPainter, option, widget=None, *args):
        """ 绘制填充图形。 """
        p.drawPicture(0, 0, self.picture)  # 使用图片对象进行绘制

    def boundingRect(self):
        """ 返回填充图形的边界矩形。  """
        return QRectF(self.picture.boundingRect())  # 返回图片对象的边界矩形


# 主窗口类，用于展示QGraphicsView中的图形场景
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()  # 调用父类构造函数

        self.view = QGraphicsView()
        self.scene = QGraphicsScene()

        layout = QVBoxLayout(self)  # 创建垂直布局，并将其设置给主窗口
        layout.addWidget(self.view)  # 将QGraphicsView添加到布局中

        # 创建一个PictureItem实例，并将其添加到场景中
        picture_item = FillItem(color=(255, 244, 215, 100))
        picture_item.setRect(0, 0, 100, 100)
        picture_item.setRect(320, 320, 200, 100)
        self.scene.addItem(picture_item)  # 将自定义的图形项添加到场景

        # 将场景设置给视图
        self.view.setScene(self.scene)  # 将QGraphicsScene设置为QGraphicsView的场景


if __name__ == "__main__":
    app = QApplication([])  # 创建QApplication应用实例

    window = MainWindow()  # 创建主窗口实例
    window.show()  # 显示主窗口

    app.exec()  # 启动应用事件循环
