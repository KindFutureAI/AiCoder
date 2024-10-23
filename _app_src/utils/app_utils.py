# _*_ coding: utf-8 _*_
from argparse import Namespace
from collections import OrderedDict
# from app_file_manager import PyFileManager
#
# # Avoid clash with module name
# # examples_ = OrderedDict([
# #     ('Command-line usage', 'CLIexample.py'),
# #     ('Demos', OrderedDict([
# #         ('Optics', 'optics_demos.py'),
# #     ])),
# # ])
# file_manager = PyFileManager()
# examples_ = file_manager.pyfiles_


# don't care about ordering
# but actually from Python 3.7, dict is ordered
others = dict([
    ('logAxis', 'logAxis.py'),
    ('PanningPlot', 'PanningPlot.py'),
    ('MouseSelection', 'MouseSelection.py'),
])


# 3_pyqtgraph_examples that are subsumed into other 3_pyqtgraph_examples
trivial = dict([
    ('LogPlotTest', 'LogPlotTest.py'),  # Plotting.py
    ('ViewLimits', 'ViewLimits.py'),    # ViewBoxFeatures.py
])

# 3_pyqtgraph_examples that are not suitable for CI testing
skiptest = dict([
    ('ProgressDialog', 'ProgressDialog.py'),    # modal dialog
])


if __name__ == '__main__':
    from collections import OrderedDict

    # # 增加元素
    # examples_['New Example'] = 'new_example.py'
    #
    # demos_dict = examples_['Demos']
    # demos_dict['Another Demo'] = 'another_demo.py'
    #
    # # 打印更新后的字典
    # print(examples_)
    #
    # # 删除元素
    # del examples_['Command-line usage']
    #
    # demos_dict = examples_['Demos']
    # del demos_dict['Optics']
    #
    # # 再次打印更新后的字典
    # print(examples_)