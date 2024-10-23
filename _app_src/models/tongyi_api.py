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