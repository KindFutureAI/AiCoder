# -*- coding: utf-8 -*-
from torch.utils.data import Dataset
import torch
import json
import numpy as np
import pandas as pd

# 实时训练数据集类
class OnlineTrainDataset(Dataset):
    """
    实时训练数据集类
    
    :param data_path: 数据路径， 示例："ner_data/train.json"
    :param tokenizer: 分词器
    :param max_source_length: 最大源序列长度
    :param max_target_length: 最大目标序列长度
    """
    def __init__(self, data_path, tokenizer, max_source_length=1200, max_target_length=600) -> None:
        super().__init__()
        self.data_path = data_path
        self.tokenizer = tokenizer
        self.max_source_length = max_source_length
        self.max_target_length = max_target_length

        self.data = pd.read_csv(data_path)
    
    def __len__(self):
        return len(self.data)
     
    
    def safe_eval(self, s):
        """
        安全评估字符串
        :param s: 字符串
        :return: 评估结果
        """
        try:
            res = eval(s)  # 这里的eval函数是用来将字符串转换为python对象的，如果字符串是列表，则转换为列表，如果字符串是字典，则转换为字典
        except Exception as e:
            return []
        return res
    
    def __getitem__(self, index):
        sample = self.data.iloc[index]
        history = self.safe_eval(sample['history'])  # 历史对话, 格式：[[user_message, assistant_message], [user_message, assistant_message], ...]
        input = str(sample['input'])  # 输入
        output = str(sample['output'])  # 输出


        messages = []
        for history_message in history:
            if len(history_message) <= 1:
                continue
            messages.append(
                {"role": 'user', "content": str(history_message[0])[:self.max_source_length // 2]}
            )
            messages.append(
                {"role": 'assistant', "content": str(history_message[1])[:self.max_target_length // 2]}
            )

        messages += [
            {"role": "user", "content": input},
            {"role": "assistant", "content": output},
        ]
        new_prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        input_tokens = self.tokenizer(new_prompt)
        input_id = input_tokens.data['input_ids'][:self.max_source_length]
        attention_mask = input_tokens.data['attention_mask'][:self.max_source_length]
     

        # 输入id
        input_id = input_id + [self.tokenizer.pad_token_id]

        # 注意力掩码
        attention_mask = attention_mask + [1]  # 为什么要加1? 答：因为注意力掩码是1表示有效，0表示无效 

        # 转换为numpy数组
        input_id = np.array(input_id)
        X = np.array(input_id[:-1]).astype(np.int64)  # 输入id，这里-1是因为输入id和输出id之间有一个关系，即输入id是输出id的前一个，但是这里的最后一个输入id是padding_len，所以-1
        Y = np.array(input_id[1:]).astype(np.int64)  # 输出id
        attention_mask = np.array(attention_mask[1:]).astype(np.int64)  # 损失掩码

        # 转换为torch.LongTensor类型
        X_tensor = torch.from_numpy(X)
        Y_tensor = torch.from_numpy(Y)
        attention_mask_tensor = torch.from_numpy(attention_mask)
 
    
        return {
            "input_ids": X_tensor,   
            "attention_mask": attention_mask_tensor,   
            "outputs": Y_tensor  
        }


class OnlineTrainDataset2(Dataset):
    def __init__(self, data_path, tokenizer, max_source_length, max_target_length) -> None:
        super().__init__()
        self.tokenizer = tokenizer                  # 分词器    
        self.max_source_length = max_source_length  # 最大源序列长度
        self.max_target_length = max_target_length  # 最大目标序列长度
        self.max_seq_length = self.max_source_length + self.max_target_length  # 最大序列长度

        self.data = []  # 数据集。格式：[{"input": "输入", "output": "标签"}]
        if data_path:
            with open(data_path, "r", encoding='utf-8') as f:
                for line in f:  # 读取数据
                    if not line or line == "":
                        continue
                    json_line = json.loads(line)  # 解析json数据
                    input = json_line["input"]      # 文本
                    output = json_line["output"]    # 标签
                    output = json.dumps(output, ensure_ascii=False)  # 标签转换为json格式, 为什么要转? 答：因为output是字典类型，而模型需要的是字符串类型
                    self.data.append({
                        "input": input,
                        "output": output
                    })
        print("data load ， size：", len(self.data))

    def preprocess(self, input, output):
        """
        预处理数据
        :param input: 输入
        :param output: 标签
        """

        messages = [
            {"role": "user", 
             "content": input},
            {"role": "assistant",
             "content": output},  # 系统提示
        ]
        prompt = self.tokenizer.apply_chat_template(messages,  # 应用聊天模板
                                                    tokenize=False,  # 不进行分词，因为模型已经分词了
                                                    add_generation_prompt=True)  # 添加生成提示
        instruction = self.tokenizer(prompt,  # 编码输入
                                     add_special_tokens=False,  # 不添加特殊标记
                                     max_length=self.max_source_length,  # 最大长度
                                     padding="max_length",  # 填充
                                     pad_to_max_length=True,  # 填充到最大长度
                                     truncation=True)  # 截断
        response = self.tokenizer(output,  # 编码标签
                                 add_special_tokens=False,  # 不添加特殊标记
                                 max_length=self.max_target_length,  # 最大长度
                                 padding="max_length",  # 填充
                                 pad_to_max_length=True,  # 填充到最大长度
                                 truncation=True)  # 截断
        
        # 输入id
        input_ids = instruction["input_ids"] + response["input_ids"] + [self.tokenizer.pad_token_id]

        # 注意力掩码
        attention_mask = (instruction["attention_mask"] + response["attention_mask"] + [1])  # 为什么要加1? 答：因为注意力掩码是1表示有效，0表示无效
        # 标签
        outputs = [-100] * len(instruction["input_ids"]) + response["input_ids"] + [self.tokenizer.pad_token_id]  # 为什么要加-100? 答：因为-100表示忽略该位置的损失

        # 返回输入id、注意力掩码、标签
        return input_ids, attention_mask, outputs

    def __getitem__(self, index):
        """
        获取数据
        :param index: 索引
        """
        item_data = self.data[index]  # 获取数据

        
        
        sample = self.df.iloc[index]
        history = self.safe_eval(sample['history'])
        q = str(sample['q'])
        a = str(sample['a'])

        
        input_ids, attention_mask, outputs = self.preprocess(**item_data)  # 预处理数据

        return {
            "input_ids": torch.LongTensor(np.array(input_ids)),  # 转换为torch.LongTensor类型, 转换成torch.bfloat16类型可以吗？答:不可以，因为模型需要的是torch.LongTensor类型
            "attention_mask": torch.LongTensor(np.array(attention_mask)),  # 转换为torch.LongTensor类型
            "outputs": torch.LongTensor(np.array(outputs))  # 转换为torch.LongTensor类型
        }

    def __len__(self):
        return len(self.data)  # 返回数据集长度
        
