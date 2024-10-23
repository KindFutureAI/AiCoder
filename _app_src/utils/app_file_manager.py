# _*_ coding: utf-8 _*_
import os
from collections import OrderedDict
from pprint import pprint

import yaml
import yamlordereddictloader

from _app_src.utils.app_function import join_path


class PyFileManager:
    """
    PyFileManager类用于管理Python文件。

    将代码文件夹下的Python文件名添加到files属性中。
    """

    def __init__(self):

        # 配置文件的路径
        self.file_name = "files_manager.yaml"
        self.file_path = join_path(os.path.dirname(__file__), self.file_name)
        # self.file_path = os.path.join(os.path.dirname(__file__), self.file_name)

        # 保持文件路径，到files属性中
        self.files = {}

        # 初始化文件管理器属性
        self._init_files()

    def _init_files(self):
        """
        初始化文件管理器属性，将当前文件夹下的Python文件名添加到files中。
        """

        file_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # 当前文件夹路径
        files = os.listdir(file_dir)  # 当前文件夹下的文件列表

        # exclude_files = self.load_yaml(os.path.join(file_dir, "_app_src/utils", "files_exclude.yaml"))
        exclude_files = self.load_yaml(join_path(file_dir, "_app_src/utils", "files_exclude.yaml"))


        def _list_file_dir(_files, _file_dir):
            """
            递归筛选list_file中的文件， 并添加文件到file_list中

            :param _files: 文件名列表
            :param _file_dir: 文件夹路径
            :return: file_list
            """
            filtered_files = {}

            for _name in _files:
                # 排除指定的文件、文件夹
                if not exclude_files or _name in exclude_files['exclude']:
                    continue

                # 如果是目录，则递归添加其内容
                # _dir = os.path.join(_file_dir, _name)
                _dir = join_path(_file_dir, _name)

                # print(f"________file_dir: {_dir}  {os.path.isdir(_dir)}")
                if os.path.isdir(_dir):  # 递归的添加文件路径信息
                    filtered_files[_name] = _list_file_dir(os.listdir(_dir), _dir)
                else:
                    filtered_files[_name] = _name
            return filtered_files

        self.files = _list_file_dir(files, file_dir)
        self.save_yaml(self.files)

    def add_pyfile(self, pyfile, file_path, dir_name=None):
        """
        添加Python文件到管理器中。

        :param pyfile: python文件的名称
        :param file_path: 文件的路径, 通常就是文件名pyfile_name
        :param dir_name: 文件所属的类别，默认为'None', 即当前文件夹。以文件夹的形式出现
        """
        # 直接添加到当前文件夹下
        if dir_name is None:
            self.files[pyfile] = file_path
            return

        if dir_name in self.files:
            # 如果类别已存在且是嵌套字典，则添加到该类别下
            self.files[dir_name][pyfile] = file_path

    def remove_pyfile(self, pyfile, dir_name=None):
        """
        从python文件列表中移除Python文件。

        :param dir_name: 文件所属的类别
        :param pyfile: python文件的名称
        """

        # 如果没有dir_name， 即要删除的文件在当前文件夹
        if dir_name is None:
            if pyfile in self.files:
                del self.files[pyfile]
            return

        # 如果有dir_name， 即要删除的文件在指定文件夹
        if dir_name in self.files:

            # 如果类别存在且为嵌套字典，则尝试从该类别中移除示例
            if pyfile in self.files[dir_name]:
                del self.files[dir_name][pyfile]

    def move_pyfile(self, pyfile, source_dir_name=None, target_dir_name='to_be_manage'):
        """
        将Python文件从一个类别移动到另一个类别。

        :param pyfile: 文件名
        :param source_dir_name: 当前文件夹
        :param target_dir_name: 目标文件夹
        """
        if not source_dir_name:
            if pyfile in self.files:

                # 如果文件存在，则从当前文件夹中移除，并添加到目标类别下
                value = self.files.pop(pyfile)
                if target_dir_name not in self.files:
                    # 如果目标类别不存在，则创建它
                    self.files[target_dir_name] = {}
                self.files[target_dir_name][pyfile] = value
            return

        if source_dir_name in self.files:

            # 检查源类别是否存在并确认它是嵌套字典
            if pyfile in self.files[source_dir_name]:

                # 如果文件存在，则从源类别中移除，并添加到目标类别下
                value = self.files[source_dir_name].pop(pyfile)
                if target_dir_name not in self.files:
                    # 如果目标类别不存在，则创建它
                    self.files[target_dir_name] = {}
                self.files[target_dir_name][pyfile] = value

    def load_yaml(self, file_path=None):
        """
        加载yaml文件。

        :param file_path: yaml配置文件的路径，默认为类的配置文件路径
        :return: 加载后的数据
        """
        if not file_path:
            file_path = self.file_path
        with open(file_path, 'r') as f:
            pyfiles = yaml.safe_load(f)

        return pyfiles

    def save_yaml(self, data: dict):
        """
        保存数据到yaml文件::

        from collections import OrderedDict
        a = OrderedDict({'one':1,'tow':{'w':'w', 's':'s'}})
        path = XXX
        with open(path, 'w+', encoding='utf-8') as f:
             yaml.dump(a, f, Dumper=yamlordereddictloader.Dumper, default_flow_style=False, allow_unicode=True)


        :param data: 需要保存的数据
        """
        with open(self.file_path, 'w') as f:
            yaml.dump(data, f, Dumper=yamlordereddictloader.Dumper, default_flow_style=False, allow_unicode=True)


if __name__ == '__main__':
    # 使用示例
    manager = PyFileManager()

    # # 添加示例
    # manager.add_pyfiles('New Category', 'new_pyfiles.py', 'new_pyfiles.py')
    # manager.add_pyfiles('Demos', 'Another Demo', 'another_demo.py')
    # print(manager.file_attr)
    #
    # # 删除示例
    # manager.remove_pyfiles('Command-line usage', 'CLIpyfiles.py')  # 对于一级目录示例
    # manager.remove_pyfiles('Demos', 'Optics')  # 对于嵌套目录下的示例
    # print(manager.file_attr)
    #
    # # 输出更新后的示例列表
    # print(manager.file_attr)

    # # 移动示例
    # manager.move_pyfile('Command-line usage', target_dir_name='demo1')
    #
    # # 输出更新后的示例列表
    # print(manager.file_attr)
    # 原始字典内容
    # examples_ = OrderedDict([
    #     ('Command-line usage', 'CLIexample.py'),
    #     ('Demos', OrderedDict([
    #         ('Optics', 'optics_demos.py'),
    #     ])),
    # ])
    # manager.save_yaml(examples_)
    print(manager.load_yaml("files_exclude.yaml"))
    print(manager.files)
