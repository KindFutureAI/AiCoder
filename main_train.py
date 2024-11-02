# -*- coding: utf-8 -*-
import torch
from torch.utils.data import DataLoader 
from transformers import AutoModelForCausalLM, AutoTokenizer

from main_dataset import OnlineTrainDataset
import sys
import time
from tqdm import tqdm 
import pandas as pd
 



def train_model(model, 
                train_loader, 
                optimizer, 
                device, 
                num_epochs, 
                model_output_dir):
    """
    训练模型
    :param model: 模型
    :param train_loader: 训练数据集
    :param optimizer: 优化器
    :param device: 设备
    :param num_epochs: 训练轮数
    :param model_output_dir: 模型输出路径
    """
    batch_step = 0  # 批处理步数初始置为0, 用于记录训练过程中的步数
    for epoch in range(num_epochs):  # 遍历训练轮数
        start_time = time.time()  # 记录当前时间


        # 训练模型: 设置模型为训练模式
        model.train() 
        for index, data in enumerate(tqdm(train_loader,     # 使用tqdm显示训练进度
                                          file=sys.stdout,  # 将进度条输出到标准输出，那么可以保存到变量中吗？答：可以
                                          # 保存到变量中：
                                          # 1. 使用tqdm.write()方法
                                          # 2. 使用tqdm.write()方法
                                          desc="Train Epoch: " + str(epoch)  # 描述训练进度条
                                          )):
            input_ids = data['input_ids'].to(device)  # 将输入数据移动到指定设备并转换为长整型
            attention_mask = data['attention_mask'].to(device)  # 将注意力掩码移动到指定设备并转换为长整型
            outputs = data['outputs'].to(device)  # 将标签移动到指定设备并转换为长整型：为什么要有标签？答：因为要计算损失

            optimizer.zero_grad()         # 清空梯度
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,  # 注意力掩码
                labels=outputs,           # 标签
            )
            loss = outputs.loss           # 计算损失
            loss.backward()               # 反向传播
            optimizer.step()              # 更新模型参数

            batch_step += 1  # 更新批处理步数

            spend_time = time.time() - start_time
            print(f"当前总 {epoch} 轮, 现在是第 {batch_step} 步, Loss: {loss}, 花费时间: {spend_time}")
        
        # 评估模型: 设置模型为评估模式。设置为评估模式的原因：
        # model.eval()     
    model.save_pretrained(model_output_dir)               # 保存模型 TODO 使用safetensors保存模型这里能不能先不保存？在之后找个时间保存？答：可以

 


def main():
    """
    主函数
    """
    model_name = "_app_src/model_local/Qwen2.5-Coder-1.5B-Instruct"  # 模型路径
    train_data_path = "_app_src/model_train/data_241030.csv"  # 训练数据路径

    max_source_length = 48000            # 最大源序列长度
    max_target_length = 48000            # 最大目标序列长度
    epochs = 5                           # 训练轮数
    batch_size = 1                       # 批处理大小
    lr = 1e-4                            # 学习率

    model_output_dir = model_name        # 模型输出路径 
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 加载分词器和模型
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

    # 加载模型
    model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)
    print("Start Load Train Data...")

    # 初始设置：冻结模型的部分参数：模型的decoder总24层
    for name, param in model.named_parameters():
        """ 示例：
        ...
        model.layers.26.mlp.up_proj.weight               : True
        model.layers.26.mlp.down_proj.weight             : True
        model.layers.26.input_layernorm.weight           : True
        model.layers.26.post_attention_layernorm.weight  : True
        model.layers.27.self_attn.q_proj.weight          : True
        model.layers.27.self_attn.q_proj.bias            : True
        ...
        """
        if "model.layers." in name:
            model_config = name.split(".")
            requires_grad_list = [23, 24, 25, 26, 27]

            # 如果层数不在requires_grad_list中，则冻结参数
            if int(model_config[2]) not in requires_grad_list:
                param.requires_grad = False
        else:
            param.requires_grad = False 
    
    # 加载数据 

    # 配置训练数据集
    train_params = {
        "batch_size": batch_size,  # 批处理大小
        "shuffle": True,           # 是否打乱数据
        "num_workers": 4,          # 工作线程数
    }

    training_set = OnlineTrainDataset(train_data_path, tokenizer, max_source_length, max_target_length)
    training_loader = DataLoader(training_set, **train_params)
    print("Start Load Validation Data...")

    

    # 配置优化器
    optimizer = torch.optim.AdamW(params=filter(lambda p: p.requires_grad, model.parameters()), lr=lr)
    # optimizer = torch.optim.AdamW(params=model.parameters(), lr=lr)
    model = model.to(device)

    # 开始训练
    print("Start Training...")
    train_model(
        model=model,                   # 模型
        train_loader=training_loader,  # 训练数据集 
        optimizer=optimizer,           # 优化器
        device=device,                 # 设备
        num_epochs=epochs,             # 训练轮数
        model_output_dir=model_output_dir,  # 模型输出路径， 这里将模型覆盖原模型地址 
    ) 
    print("Training Finished!")


if __name__ == '__main__':
    main()

