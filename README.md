# AiCoder
使用pyqt5做的代码注释工具Demo. 

功能介绍：检索项目文件夹下面的目录，对目前文件中的代码进行手动选取，发送至Qwen2 等api进行代码注释

## 快速开始
1. **安装依赖包**
   - 主要是pyqt5、opanai少数几个包，根据运行提示安装
2. **配置密钥**
```python
# 在 _app_src/models/tongyi_api.py 写入api信息
# 也可以在models中新增api
import os
from openai import OpenAI


class ModelQwenApi:
    def __init__(self):
        self.client = OpenAI(
            # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
            # api_key=os.getenv("DASHSCOPE_API_KEY"),
            api_key="",  # 必填，请配置你的API Key
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

    def get_answer(self, your_input: str):
        """ 传入字符，经通义千问api 完成处理后，返回答案
        :param your_input: 这是发送给AI的输入。
        """
        if not your_input:
            return
        try:
            completion = self.client.chat.completions.create(
                model="qwen-turbo",
                # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
                messages=[
                    {'role': 'system',
                     'content': '你是高级软件工程师，擅长解决各类编程问题，我需要你帮助我编写代码。'},
                    {'role': 'user', 'content': your_input}
                ]
            )
            answer = completion.choices[0].message.content
            return answer

        except Exception as e:
            msg = f"请求回答时出现错误，错误内容为:\n+ {e})"
            return msg

if __name__ == "__main__":
    qwen_api = ModelQwenApi()
    print(qwen_api.get_answer("请帮我写一个冒泡排序的python代码"))
```
3. **运行 main.py**
4. **界面显示**

![img.png](_app_src/images/mainWindow1.png)

![img.png](_app_src/images/img.png)