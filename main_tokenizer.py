import json 
from transformers import AutoTokenizer  
import numpy as np  
import matplotlib.pyplot as plt  # 导入matplotlib.pyplot模块
plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置字体为SimHei

def get_token_distribution(file_path, tokenizer):
    """
    获取token分布
    :param file_path: 文件路径
    :param tokenizer: 分词器
    """
    input_num_tokens, outout_num_tokens = [], []  # 初始化输入和输出token数量列表
    with open(file_path, "r", encoding="utf-8") as r:  
        for line in r:  # 遍历文件中的每一行
            line = json.loads(line)  # 将每行解析为json对象
            text = line['text']  # 获取文本内容
            label = line['label']  # 获取标签
            label = json.dumps(label, ensure_ascii=False)  # 将标签转换为json格式
            input_num_tokens.append(len(tokenizer(text).input_ids))  # 计算输入token数量并添加到列表
            outout_num_tokens.append(len(tokenizer(label).input_ids))  # 计算输出token数量并添加到列表
    return min(input_num_tokens), max(input_num_tokens), np.mean(input_num_tokens),\
        min(outout_num_tokens), max(outout_num_tokens), np.mean(outout_num_tokens)  # 返回token数量的统计信息

def main():
    model_path = "model/Qwen2.5-0.5B-Instruct"  # 模型路径
    train_data_path = "ner_data/train.json"  # 训练数据路径
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)  # 加载预训练tokenizer
    i_min, i_max, i_avg, o_min, o_max, o_avg = get_token_distribution(train_data_path, tokenizer)  # 获取token分布信息
    print(i_min, i_max, i_avg, o_min, o_max, o_avg)  # 打印token分布信息

    plt.figure(figsize=(8, 6))  # 设置图形大小
    bars = plt.bar([  # 绘制柱状图
        "input_min_token",  # 输入最小token
        "input_max_token",  # 输入最大token
        "input_avg_token",  # 输入平均token
        "ouput_min_token",  # 输出最小token
        "ouput_max_token",  # 输出最大token
        "ouput_avg_token",  # 输出平均token
    ], [
        i_min, i_max, i_avg, o_min, o_max, o_avg  # 对应的token数量
    ])
    plt.title('训练集Token分布情况')  # 设置图表标题
    plt.ylabel('数量')  # 设置y轴标签
    for bar in bars:  # 遍历每个柱状图
        yval = bar.get_height()  # 获取柱子的高度
        plt.text(bar.get_x() + bar.get_width() / 2, yval, int(yval), va='bottom')  # 在柱子上方显示数量
    plt.show()  # 显示图表

if __name__ == '__main__':
    main()  # 运行主函数