# _*_ coding: utf-8 _*_
import os
import re
import sys
import keyword
import pyqtgraph as pg
from pprint import pprint


# 增加搜索路径
path = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, path)

def join_path(*path_str):
    return '/'.join(path_str) if path_str else ""
