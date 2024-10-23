import os
import sys
from functools import lru_cache
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QWidget, QApplication, QTextEdit, QPushButton, QHBoxLayout, QVBoxLayout,
                             QMainWindow, QSpacerItem, QSizePolicy, QTreeWidget, QTreeWidgetItem, QMessageBox)

from _app_src.utils.app_file_manager import PyFileManager
from _app_src.models.tongyi_api import ModelQwenApi
from git.util import join_path

# 加载配置文件
file_manager = PyFileManager()
files = file_manager.files

# 增加搜索路径：获取当前文件绝对路径
app_path = os.path.abspath(os.path.dirname(__file__))

# 初始化模型api
model = ModelQwenApi()

class CodeWin(QMainWindow):
    def __init__(self, parent=None):
        super(CodeWin, self).__init__(parent)

        self.center_win = QWidget(self)
        self.center_vlayout = QVBoxLayout()
        self.center_win.setLayout(self.center_vlayout)
        self.setCentralWidget(self.center_win)

        self._init_ui()
        self._init_win()
        self._init_signal()

        # 初始化树形控件节点的缓存
        self.itemCache = []

        # 初始化树形控件
        self.generate_tree(self.file_tree.invisibleRootItem(), files, os.path.dirname(__file__))

    def _init_win(self):
        """ 界面数据初始化函数 """
        self.setWindowTitle("代码编辑助手")
        self.setGeometry(800, 400, 1400, 800)
        # self.setStyleSheet("background-color: #2D2D2D;")
        self.file_tree.setMaximumWidth(300)

    def _init_ui_code_board(self):
        """ ui初始化：被选中文件的代码显示窗口 """
        self.code_file_win = QTextEdit()
        self.code_file_win.setPlaceholderText("原代码：\n这是选中文件的代码")

    def _init_ui_send_board(self):
        """ ui初始化：被选中的代码显示窗口"""
        self.code_pick_win = QTextEdit()
        self.code_pick_win.setPlaceholderText("已选代码: \n会将已选择的代码发送到AI")

        # 设置代码发送区的显示 隐藏按钮
        self.btn_describe = QPushButton("需求")
        self.btn_demo = QPushButton("示例")
        self.hlayout_describe = QHBoxLayout()
        self.widget_describe = QWidget()

        self.code_demo = QTextEdit()
        self.code_demo.setFixedHeight(100)
        self.code_demo.setPlaceholderText("示例描述：简要描述示例")

        self.code_description = QTextEdit()
        self.code_description.setFixedHeight(60)
        self.code_description.setPlaceholderText("需求描述：简要描述一下想要让AI做什么")

        self.hlayout_describe.addWidget(self.btn_demo)
        self.hlayout_describe.addWidget(self.btn_describe)
        self.widget_describe.setLayout(self.hlayout_describe)

        # 设置代码发送区
        self.code_pick_widget = QWidget()

        self.code_input_vlayout = QVBoxLayout()
        self.code_input_vlayout.addWidget(self.code_pick_win)
        self.code_input_vlayout.addWidget(self.code_description)
        self.code_input_vlayout.addWidget(self.code_demo)
        self.code_input_vlayout.addWidget(self.widget_describe)
        self.code_pick_widget.setLayout(self.code_input_vlayout)

    def _init_ui_check_board(self):
        """ ui初始化：AI返回的回答显示窗口 """
        self.code_check_win = QTextEdit()
        self.code_check_win.setPlaceholderText("检查代码：\n会将AI的回答显示在这里")

    def _init_ui_bottom_board(self):
        """ ui初始化：底部按钮初始化 """
        self.btn_send = QPushButton("发送")
        self.btn_undo = QPushButton("撤销")

        self.hlayout2 = QHBoxLayout()
        self.hlayout3 = QHBoxLayout()
        self.hlayout4 = QHBoxLayout()

        self.hlayout2.addWidget(self.btn_send)
        self.hlayout2.addWidget(self.btn_undo)
        self.send_board.setLayout(self.hlayout2)

        self.hlayout3.addWidget(self.btn_show_file_tree)
        self.hlayout3.addWidget(self.btn_show_code_file)
        self.hlayout3.addWidget(self.btn_show_code_pick)
        self.hlayout3.addWidget(self.btn_show_code_check)
        self.check_board.setLayout(self.hlayout3)

        # 添加一个水平占位符串
        self.hlayout4.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.hlayout4.addWidget(self.send_board)
        self.hlayout4.addWidget(self.check_board)
        self.hlayout4.setSpacing(24)
        self.bottom_board.setLayout(self.hlayout4)

    def _init_ui(self):
        # 容器
        self.code_board = QWidget()
        self.send_board = QWidget()
        self.check_board = QWidget()
        self.bottom_board = QWidget()

        # 增加树形结构: 显示文件目录
        self.file_tree = QTreeWidget()

        # 第二组：发送区的按钮

        # 第三组：显示详情的按钮
        self.btn_show_file_tree = QPushButton("文件树")
        self.btn_show_code_file = QPushButton("原代码")
        self.btn_show_code_pick = QPushButton("已选代码")
        self.btn_show_code_check = QPushButton("检查代码")


        self._init_ui_code_board()
        self._init_ui_send_board()
        self._init_ui_check_board()
        self._init_ui_bottom_board()
        # 三组容器的布局
        self.hlayout1 = QHBoxLayout()


        for layout in [self.hlayout1, self.hlayout2, self.hlayout3, self.hlayout4,
                       self.hlayout_describe, self.code_input_vlayout]:
            layout.setContentsMargins(0, 0, 0, 0)

        self.code_widgets = [self.file_tree, self.code_file_win,
                             self.code_pick_widget, self.code_check_win]

        for w in self.code_widgets:
            self.hlayout1.addWidget(w)

        self.code_board.setLayout(self.hlayout1)

        self.center_vlayout.addWidget(self.code_board)
        self.center_vlayout.addWidget(self.bottom_board)



    def _init_signal(self):

        self.check_btns = [self.btn_show_file_tree, self.btn_show_code_file,
                           self.btn_show_code_pick, self.btn_show_code_check,
                           self.btn_demo, self.btn_describe]
        for btn in self.check_btns:
            btn: QPushButton
            btn.clicked.connect(self.shift_win)

        self.file_tree.currentItemChanged.connect(self.show_py_file)

        # 将第一个 QTextEdit 的 selectionChanged 信号连接到自定义槽函数
        self.code_file_win.selectionChanged.connect(self.on_selection_changed)

        self.btn_send.clicked.connect(self.send_question_to_ai)


    def send_question_to_ai(self):
        the_input = self.code_pick_win.toPlainText()
        the_description = self.code_description.toPlainText()
        the_demo = self.code_demo.toPlainText()
        query = '\n'.join([the_input, the_description, the_demo])
        if query:
            msgger = QMessageBox(self)
            # 这里需要写一个消息提示：有query时，确认是否要发送消息
            msgger.setText("确定要发送吗？")
            msgger.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            result = msgger.exec()
            if result == QMessageBox.Yes:
                answer = model.get_answer(the_input)
                self.code_pick_win.clear()
                self.code_check_win.setText(str(answer))



    def shift_win(self):
        """ 显示隐藏代码界面 """
        sender = self.sender()

        def detect_text_board():
            """ 判断是否全部都隐藏了：至少得留一个 """
            count_visible = 0
            for w in self.code_widgets:
                if w.isVisible():
                    count_visible += 1
            return count_visible


        if sender == self.btn_show_file_tree:
            if self.file_tree.isVisible():
                if detect_text_board() > 1:
                    self.file_tree.setVisible(False)
            else:
                self.file_tree.setVisible(True)

        elif sender == self.btn_show_code_file:
            if self.code_file_win.isVisible():
                if detect_text_board() > 1:
                    self.code_file_win.setVisible(False)
            else:
                self.code_file_win.setVisible(True)

        elif sender == self.btn_show_code_pick:
            if self.code_pick_widget.isVisible():
                if detect_text_board() > 1:
                    self.code_pick_widget.setVisible(False)
            else:
                self.code_pick_widget.setVisible(True)

        elif sender == self.btn_show_code_check:
            if self.code_check_win.isVisible():
                if detect_text_board() > 1:
                    self.code_check_win.setVisible(False)
            else:
                self.code_check_win.setVisible(True)

        elif sender == self.btn_demo:
            if self.code_demo.isVisible():
                self.code_demo.setVisible(False)
            else:
                self.code_demo.setVisible(True)

        elif sender == self.btn_demo:
            if self.code_demo.isVisible():
                self.code_demo.setVisible(False)
            else:
                self.code_demo.setVisible(True)

        elif sender == self.btn_describe:
            if self.code_description.isVisible():
                self.code_description.setVisible(False)
            else:
                self.code_description.setVisible(True)



    def on_selection_changed(self):
        # 获取选中的文本
        selected_text = self.code_file_win.textCursor().selectedText()

        # 将选中的文本设置到第二个 QTextEdit 中
        self.code_pick_win.setPlainText(selected_text)

    def generate_tree(self, root, files, current_path=""):
        """
        递归地为树形控件加载文件结构。

        :param root: 树形控件的根节点
        :param files: 文件字典，表示文件或目录的结构
        :param current_path: 当前路径，默认为空字符串
        """
        for key, value in files.items():
            if not isinstance(value, dict):
                # 为文件创建树节点
                item = QTreeWidgetItem([key])
                self.itemCache.append(item)
                item.file = current_path + "\\" + value
                root.addChild(item)
            else:
                # 为目录创建子树
                root_next = QTreeWidgetItem([key])
                root.addChild(root_next)
                self.generate_tree(root_next, value, current_path + "\\" + key)

    def show_py_file(self):
        """
        显示文件内容到代码编辑器。

        获取当前选中的文件路径，读取文件内容，并在代码编辑器中显示。
        同时更新文件路径标签和隐藏保存按钮。
        """
        file_path = self.get_tree_item_file()
        text = self.get_file_content(file_path)

        # 设置代码编辑器的字体和内容
        self.code_file_win.setFont(QFont("MicroSoft YaHei", 10))
        self.code_file_win.setPlainText(text)


    def get_tree_item_file(self):
        """
        获取当前选中的文件路径。

        从文件树中获取当前选中的项，如果该项有file属性，则返回该项的文件路径。
        如果没有选中文件或选中的项不是文件，则返回None。
        """
        item = self.file_tree.currentItem()
        if hasattr(item, 'file'):
            return os.path.join(app_path, item.file).replace('\\', "/")
        return None
    @lru_cache(100)
    def get_file_content(self, filename):
        """
        从文件中获取内容。

        使用lru_cache装饰器缓存最近访问的100个文件的内容。
        如果文件路径为None，则清空代码编辑器；
        如果文件路径是一个目录，则寻找并读取目录下的__main__.py文件；
        否则，直接读取文件内容。

        参数: filename -- 文件路径。

        返回: 文件的内容。
        """
        if filename is None:
            self.code_file_win.clear()
            return

        if os.path.isdir(filename):
            # filename = os.path.join(filename, '__main__.py')
            filename = join_path(filename, '__main__.py')
        with open(filename, "r", encoding='utf-8') as currentFile:
            text = currentFile.read()
        return text


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = CodeWin()
    win.show()
    sys.exit(app.exec_())
