# -*- coding: utf-8 -*-
import torch
from torch.utils.data import DataLoader 
from transformers import AutoModelForCausalLM, AutoTokenizer

from main_dataset import OnlineTrainDataset
import sys
import time
from tqdm import tqdm 
import pandas as pd
import logging
import time

from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget
import sys

logger = logging.getLogger(__name__)
# 将logger的输出打印到终端
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)



model_name = "_app_src/model_local/Qwen2.5-0.5B-Instruct"  # 模型路径

model2_name = "_app_src/model_local/Qwen2.5-0.5B-Instruct_2"  # 模型路径
model3_name = "_app_src/model_local/Qwen2.5-0.5B-Instruct_3"  # 模型路径
model4_name = "_app_src/model_local/Qwen2.5-Coder-1.5B-Instruct"  # 模型路径


def get_model_answer(args):

    model, input_text, history = args
    return model.get_answer(input_text, history)

def get_answer_from_local_model(models):
    time1 = time.time()
    logger.info("获取回答")
    
    # 使用多进程并行获取答案
        
    # 创建进程池
    pool = Pool(processes=4)
    
    # 并行执行get_answer
    results = pool.map(get_model_answer, models)
    
    # 关闭进程池
    pool.close()
    pool.join()
    time2 = time.time() - time1
    logger.warning(f"运行模型的回答，花费了这些时间 {time2}")
    return results

class ModelLocal:

    train_data_path = "_app_src/model_train/data_241030.csv"  # 训练数据路径
    

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    max_source_length = 48000            # 最大源序列长度
    max_target_length = 48000            # 最大目标序列长度
    epochs = 5                           # 训练轮数
    batch_size = 1                       # 批处理大小
    lr = 1e-4                            # 学习率

    model_local = None

    def __init__(self, model_path):
        logger.info("初始化模型")
        self.model_name = model_path
        self.model_output_dir = self.model_name        # 模型输出路径 
        self.init_model()

 
    def init_model(self):
        logger.info(f"加载模型: {self.model_name}")

        # 加载分词器和模型
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
        # 加载模型
        self.model_local = AutoModelForCausalLM.from_pretrained(self.model_name, 
                                                                device_map=self.device,
                                                                trust_remote_code=True)

        print("Start Load Train Data...")
        # self.train_online()

    def get_answer(self, query, history):
        logger.info("获取回答(ModelLocal 的 get_answer 方法)")
        conversation = []
        for query_h, response_h in history:
            conversation.append({"role": "user", "content": query_h})
            conversation.append({"role": "assistant", "content": response_h})
        conversation.append({"role": "user", "content": query})
        input_text = self.tokenizer.apply_chat_template(
            conversation,
            add_generation_prompt=True,
            tokenize=False,
        )
        logger.info(f"device 是： {self.model_local.device}")
        inputs = self.tokenizer([input_text], return_tensors="pt").to(self.model_local.device)
        generated_ids = self.model_local.generate(
            **inputs,
            max_new_tokens=64000,
            # top_k=1
            # top_p=0.5
        )

        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(inputs.input_ids, generated_ids)
        ]
        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        logger.info(f"input: {query}\nresult: {response}")
        return response
    

    def train_online(self):

        if not self.model_local:
            print(f"debug: 出错，模型没有加载。")

        # 检测模型有多少层
        layer_set = set()
        for name, param in self.model_local.named_parameters():
            if "model.layers." in name:
                layer_set.add(int(name.split(".")[2]))

        layer_count = len(layer_set)
        requires_grad_list = list(range(layer_count - 5, layer_count))
        print(f"debug: 模型有 {layer_count} 层, 取最后 {len(requires_grad_list)} 层再训练")

        # 初始设置：冻结模型的部分参数：模型的decoder总24层，需要从训练最后5层
        for name, param in self.model_local.named_parameters():
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

                # 如果层数不在requires_grad_list中，则冻结参数
                if int(model_config[2]) not in requires_grad_list:
                    param.requires_grad = False
            else:
                param.requires_grad = False 
        

        # 配置训练数据集
        train_params = {
            "batch_size": self.batch_size,  # 批处理大小
            "shuffle": True,           # 是否打乱数据
            "num_workers": 4,          # 工作线程数
        }

        training_set = OnlineTrainDataset(self.train_data_path, 
                                          self.tokenizer, 
                                          self.max_source_length, 
                                          self.max_target_length)
        training_loader = DataLoader(training_set, **train_params)
        print("Start Load Validation Data...")

        

        # 配置优化器
        optimizer = torch.optim.AdamW(params=filter(lambda p: p.requires_grad, self.model_local.parameters()), 
                                      lr=self.lr)
        # optimizer = torch.optim.AdamW(params=self.model_local.parameters(), lr=self.lr)
        self.model_local = self.model_local.to(self.device)

        # 开始训练
        print("Start Training...")
        self.train_model(
            model=self.model_local,                   # 模型
            train_loader=training_loader,  # 训练数据集 
            optimizer=optimizer,           # 优化器
            device=self.device,                 # 设备
            num_epochs=self.epochs,             # 训练轮数
            model_output_dir=self.model_output_dir,  # 模型输出路径， 这里将模型覆盖原模型地址 
        ) 
        print("Training Finished!")
 
    
    def save_model(self):
        self.model_local.eval()     
        self.model_local.save_pretrained(self.model_output_dir)




    def train_model(self,
            model, 
            train_loader, 
            optimizer, 
            device, 
            num_epochs):
        """
        训练模型
        :param model: 模型
        :param train_loader: 训练数据集
        :param optimizer: 优化器
        :param device: 设备
        :param num_epochs: 训练轮数 
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
        # model.save_pretrained(model_output_dir)               # 保存模型 TODO 使用safetensors保存模型这里能不能先不保存？在之后找个时间保存？答：可以

    

 




class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.init_singal()
        self.model_local = ModelLocal(model_name)
        self.model_local2 = ModelLocal(model2_name)
        # self.model_local3 = ModelLocal(model3_name)
        self.model_local4 = ModelLocal(model4_name)

        self.user_input = ""
        self.sys_output = ""

    def initUI(self):
        self.setWindowTitle('Main App')
        self.setGeometry(1400, 400, 1200, 800)
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        self.layout = QHBoxLayout(self.main_widget) 

        self.input_user = QTextEdit(placeholderText="请输入你的问题, 点击按钮提交")
        self.output_sys = QTextEdit(placeholderText="AI的回答")
        self.btn_submit = QPushButton('发送')

        self.sub_vlayout = QVBoxLayout()
        self.sub_vlayout.addWidget(self.output_sys)
        self.sub_vlayout.addWidget(self.input_user)
        self.sub_vlayout.addWidget(self.btn_submit)
        self.layout.addLayout(self.sub_vlayout)

        self.history_list = []  # 历史对话
        self.history_board = QTextEdit(placeholderText="历史对话显示")
        self.layout.addWidget(self.history_board)
    
    def init_singal(self):  # 绑定信号
        self.btn_submit.clicked.connect(self.btn_submit_clicked)

        # 为按钮添加快捷键
        self.btn_submit.setShortcut("Ctrl+Enter")

    def get_answer(self, input):  # 或模型回答

        # 准备参数
        models = [(self.model_local, input, self.history_list),
                  (self.model_local2, input, self.history_list),
                #   (self.model_local3, input, self.history_list),
                  (self.model_local4, input, self.history_list)]
                    
        results = get_answer_from_local_model(models)
        
        # 获取结果
        self.sys_output1, self.sys_output2, self.sys_output3, self.sys_output4 = results
        
        # 合并输出
        self.sys_output = f"助手1:\n{self.sys_output1}\n助手2:\n{self.sys_output2}\n助手3:\n{self.sys_output3}\n总助手:\n{self.sys_output4}\n\n"

        logger.info(f"获取回答完成")

    def btn_submit_clicked(self):  # 按钮点击时间
        logger.info("按钮点击事件")
        self.user_input = self.input_user.toPlainText()
        if not self.user_input:
            return

        self.get_answer(self.user_input)
        self.input_user.clear()
        self.output_sys.setText(self.sys_output)
        self.update_history(self.user_input, self.sys_output) 

    def update_history(self, input, output):
        self.history_list.append({"usr": input, "sys": output})
        # 取历史记录中的最后10个对话
        self.history_list = self.history_list[-10:] if len(self.history_list) > 10 else self.history_list

        history_text = "\n".join([f"用户: {item['usr']}\n助手: {item['sys']}\n" for item in self.history_list])
        # 取历史对话显示的最后5000个字符
        self.history_board.setPlainText(history_text[-5000:])

if __name__ == '__main__':

    from multiprocessing import Pool, Manager 
    import multiprocessing
    multiprocessing.set_start_method('spawn')  

    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec_())