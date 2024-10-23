from PySide6.QtCore import QPointF, Qt, QRectF
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QPolygonF
from PySide6.QtWidgets import QWidget


class CustomWidget(QWidget):
    def paintEvent(self, event):
        """
        重写paintEvent方法以实现自定义绘图。
        参数:
            event (QPaintEvent): 与绘图相关的事件对象。
        """

        # 创建QPainter对象用于在CustomWidget上进行绘制
        p = QPainter(self)

        # 设置画笔选项
        p.setRenderHint(QPainter.Antialiasing)  # 开启抗锯齿

        # 示例颜色
        pie_color = QColor(255, 85, 0)  # 橙色

        # 饼图扇形坐标和尺寸
        x = 50
        y = 0
        w = 200
        h = 100
        span_angle = 120  # 扇形角度（假设付款百分比为120度）

        # 绘制付款百分比的扇形
        pen = QPen(pie_color, 2, Qt.PenStyle.SolidLine)
        p.setBrush(QBrush(pie_color))  # 设置填充色为pie_color
        p.setPen(Qt.PenStyle.NoPen)  # 不绘制轮廓线
        rect = QRectF(x, y, w, h)  # 创建绘制扇形的矩形区域
        p.drawPie(rect, -90 * 16, span_angle * 16)  # 绘制付款百分比的扇形
        """
        -90: 起始角度，以度为单位（即16：Qt默认一度为16）
        span_angle：跨越角度，以度为单位
        """

        x = 250
        y = 0
        w = 200
        h = 100
        # 绘制付款标记和线条
        pen = QPen(QColor(0, 0, 0), 2, Qt.PenStyle.SolidLine)
        p.setBrush(Qt.BrushStyle.NoBrush)  # 不填充图形
        p.setPen(pen)  # 设置轮廓线为黑色，宽度为1像素
        p.drawEllipse(QPointF(x, y + h * 3), w, h)  # 绘制付款标记（一个椭圆）
        p.drawLine(QPointF(x, y + h), QPointF(x, y + h * 2))  # 绘制一条水平线条

        # 绘制矩形
        p.setBrush(QBrush(QColor(90, 90, 90)))  # 设置填充颜色
        p.setPen(pen)  # 设置线条颜色和宽度
        p.drawRect(0, 0, 100, 100)  # 绘制账单周期

        # 绘制多边形
        vertices = [
            QPointF(0, 150),  # 顶点
            QPointF(50, 150),  # 左下角
            QPointF(50, 200)  # 右下角
        ]
        color = QColor('red')
        polygon = QPolygonF(vertices)
        p.setPen(QPen(color, 0))
        p.setBrush(QBrush(color))
        p.drawPolygon(polygon)  # 绘制支付标记

        p.end()  # 结束绘图

    def add_text_item(self,
                      plot,
                      x,
                      y,
                      text,
                      is_bill=False,
                      color=QColor("red"),
                      fontsize=10,
                      ZValue=101):
        """
        增加文字说明

        参数:
        - plot: 图表对象，用于添加文字项。
        - x: 文字项在图表上的X坐标。
        - y: 文字项在图表上的Y坐标。
        - text: 要显示的文字内容。
        - color: 文字颜色，默认为黑色。
        - ZValue: 控制文字项在图表中的层叠顺序，默认为2。
        """

        text_item = pg.TextItem(text=text,
                                color=color)

        text_item.setPos(x, y)
        text_item.setZValue(ZValue)
        text_item.setFont(QFont("Arial", fontsize))
        if is_bill:
            text_item.setAnchor((0, 0.5))
        else:
            text_item.setAnchor((0, 0))
        plot.addItem(text_item)

    def get_contract_period(self, tenant):
        """
        获取租户合同的起止时间。

        参数:
        - tenant: 字典类型，包含租户信息及其合同列表。

        返回值:
        - start, end: 合同起止时间的Unix时间戳。如果开始时间晚于结束时间，则返回None。
        """

        # 初始化起止时间为硬编码的日期
        start = datetime.datetime(2050, 1, 1)
        end = datetime.datetime(2014, 1, 1)

        # 遍历租户的所有合同，更新起止时间
        for contract in tenant['contracts']:
            if contract['start'] < start:
                start = contract['start']
            if contract['end'] > end:
                end = contract['end']

        # 检查开始时间是否早于结束时间
        if start < end:
            # 将datetime对象转换为Unix时间戳
            data_timestamps = np.array([timestamp.timestamp() for timestamp in (start, end)])
            start = data_timestamps[0]
            end = data_timestamps[1]
            # 记录调试信息：计算的数据起止时间
            logger.debug(f"计算数据起止时间： start: type {type(start)} {start} - end type {type(end)} {end}")
            return start, end
        else:
            # 记录错误信息：开始时间大于结束时间
            logger.error(f"报错： 计算商户合同的起止时间时，出错： 开始时间 {start} 大于结束时间 {end}")
            return None


class LedgerItem:
    """
    代表一个账目项的类，具有矩形和两个三角形标识。

    参数:
    - x: 距离图表左侧的距离
    - y: 距离图表顶部的距离
    - width: 矩形的宽度，默认为80000
    - height: 矩形的高度，默认为100
    - color: 矩形和三角形的颜色，默认为天空蓝
    """

    def __init__(self, x, y, width=80000, height=100, color=QColor("skyblue")):
        # 初始化账目项，包括矩形和两个三角形标识
        super().__init__()

        self.rect = CustomRectItem(x, y, width, height, color=color)
        # 设置三角形标识的大小
        _width = width / 10
        _height = height / 10
        self.triangle_top = CustomTriangleItem(x=x, y=y, width=_width, height=_height, is_bottom=False)
        self.triangle_bottom = CustomTriangleItem(x=x + width, y=y + height, width=_width, height=_height,
                                                  is_bottom=True)

    class CustomRectItem(QGraphicsRectItem):
        """
        自定义的矩形图形项类，继承自QGraphicsRectItem。

        参数:
        - x: float，矩形左上角的x坐标。
        - y: float，矩形左上角的y坐标。
        - width: float，矩形的宽度。
        - height: float，矩形的高度。
        - color: QColor，矩形的填充颜色。

        方法:
        - mousePressEvent: 处理鼠标按下事件。
        - mouseReleaseEvent: 处理鼠标释放事件。
        - mouseDoubleClickEvent: 处理鼠标双击事件。
        """

        # 初始化类变量
        left = float('inf')
        right = 0
        ratio_x = 0
        ratio_y = 0
        draw_y = 0
        text = ""

        # 信号变量，用于图形更新和创建通知
        bar_updated = Signal()
        bar_created = Signal(float, float)

        def __init__(self, x, y, w, h, color=QColor("skyblue"), text=text, is_text_above=True):
            super().__init__(x, y, w, h)

            self._x = x
            self._y = y
            self._w = w
            self._h = h
            self.text = text
            self.is_text_above = is_text_above

            self.text = f"时间 {datetime.fromtimestamp(self._x)}"
            self.text_item = None

            # print(f"绘制矩形: x={x}, y={y}, width={width}, height={height}")
            # 设置矩形边框的样式和颜色
            pen = QPen()
            pen.setColor(Qt.black)
            pen.setWidth(0)
            pen.setStyle(Qt.SolidLine)
            self.setPen(pen)
            self.setBrush(QBrush(color))
            # self.setFlag(QGraphicsItem.ItemIsMovable)  # 矩形可移动
            self.setFlag(QGraphicsItem.ItemIsSelectable)  # 矩形可选中

        def mousePressEvent(self, event, *args, **kwargs):
            # 处理左键和右键按下事件
            if event.button() == Qt.LeftButton:
                print(f"点击矩形，时间为: {self.text}")
                print("Left mouse pressed on 矩形")
                self.setToolTip(f"时间: {self.text}")
            elif event.button() == Qt.RightButton:
                print("Right mouse pressed on 矩形")
                self.setToolTip("")
            super().mousePressEvent(event)

            print(f"xxxxxxxxxxxxxxxxxxxxxxrect  矩形框的 参数：")
            for arg in args:
                print(arg)
            for kwarg in kwargs:
                print(f"{kwarg}: {kwargs[kwarg]}")

        def mouseReleaseEvent(self, event):
            # 处理左键和右键释放事件
            if event.button() == Qt.LeftButton:
                print("Left mouse button released on 矩形")
            elif event.button() == Qt.RightButton:
                print("Right mouse button released on 矩形")
            super().mouseReleaseEvent(event)

        def mouseDoubleClickEvent(self, event):
            # 处理左键双击事件
            if event.button() == Qt.LeftButton:
                print("Left mouse button double-clicked on 矩形")
            super().mouseDoubleClickEvent(event)

    class CustomTriangleItem(QGraphicsPolygonItem):
        """
        自定义的三角形图形项类，继承自QGraphicsPolygonItem。

        参数:
        - x: int，三角形顶点的x坐标。
        - y: int，三角形顶点的y坐标。
        - is_up: bool，控制三角形的方向，默认为False，表示朝下。

        方法:
        - mousePressEvent: 处理鼠标按下事件。
        """

        def __init__(self, x: int, y: int, width, height, is_bottom=False):
            super().__init__()

            self._x = x
            self._y = y

            self.text = f"时间 {datetime.fromtimestamp(self._x)}"
            self.text_item = None
            self.setZValue(1)

            # 根据is_up参数决定三角形的方向并设置颜色
            if is_bottom:
                # print(f"绘制上三角形: x={x}, y={y}, width={width}, height={height}")
                vertices = [
                    QPointF(x, y),  # 顶点
                    QPointF(x - width / 2, y + height / 2),  # 左上角
                    QPointF(x + width / 2, y + height / 2)  # 右上角
                ]
                color = QColor("skyblue")
                # self.set_text(self.text, "bottom")
            else:
                # print(f"绘制下三角形: x={x}, y={y}, width={width}, height={height}")
                vertices = [
                    QPointF(x, y),  # 顶点
                    QPointF(x - width / 2, y - height / 2),  # 左下角
                    QPointF(x + width / 2, y - height / 2)  # 右下角
                ]
                color = QColor('red')
                # self.set_text(self.text, "top")

            polygon = QPolygonF(vertices)
            self.setPolygon(polygon)
            self.setPen(QPen(color, 0))
            self.setBrush(QBrush(color))

        # def set_text(self, text, position="top"):
        #     if self.text_item:
        #         self.scene().removeItem(self.text_item)
        #         self.text_item = None
        #
        #     if text:
        #         self.text_item = QGraphicsTextItem(text, parent=self)
        #         font = QFont("Arial", 10)
        #         self.text_item.setFont(font)
        #         self.text_item.setDefaultTextColor(QColor("red"))
        #
        #         if position == "top":
        #             # 将文本放置在三角形上方
        #             text_y = self.y() - self.boundingRect().height() / 2 + self.text_item.boundingRect().height() - 5  # 调整间距
        #             text_x = self.x() - self.boundingRect().width() / 2 + self.text_item.boundingRect().width() / 2
        #         elif position == "bottom":
        #             # 将文本放置在三角形下方
        #             text_y = self.y() + self.boundingRect().height() / 2 - 5  # 调整间距
        #             text_x = self.x() - self.boundingRect().width() / 2 + self.text_item.boundingRect().width() / 2
        #         else:
        #             raise ValueError("Invalid text position. Expected 'top' or 'bottom'.")
        #         # print(f"text_x: {text_x}, text_y: {text_y}")
        #         self.text_item.setPos(text_x, text_y)

        def mousePressEvent(self, event):
            # 处理左键和右键按下事件
            super().mousePressEvent(event)

            if event.button() == Qt.LeftButton:
                print(f"Left mouse pressed on 三角形  {self.text}")
            elif event.button() == Qt.RightButton:
                print(f"Right mouse pressed on 三角形  {self.text}")


    def add_item(self, plot):
        """
        将账目项的所有图形元素添加到图表中。

        参数:
        - plot: 图表对象，用于添加图形元素。
        """
        plot.addItem(self.rect)
        plot.addItem(self.triangle_top)
        plot.addItem(self.triangle_bottom)




if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QWidget

    app = QApplication([])

    widget = CustomWidget()
    widget.resize(500, 400)
    widget.show()

    app.exec()
