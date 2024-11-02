 # -*- coding: utf-8 -*-
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch


def main():
    model_path = "model_local/Qwen2.5-0.5B-Instruct"
    train_model_path = "output_ner"
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(model_path, trust_remote_code=True)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to(device)

    test_case = [
        "三星WCG2011北京赛区魔兽争霸3最终名次",
        "新华网孟买3月10日电（记者聂云）印度国防部10日说，印度政府当天批准",
        "证券时报记者肖渔"
    ]

    for case in test_case:
        messages = [
            {"role": "system",
             "content": "你的任务是做Ner任务提取, 根据用户输入提取出完整的实体信息, 并以JSON格式输出。"},
            {"role": "user", "content": case}
        ]
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = tokenizer([text], return_tensors="pt").to(device)
        generated_ids = model.generate(
            model_inputs.input_ids,
            max_new_tokens=140,
            top_k=1
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        print("----------------------------------")
        print(f"input: {case}\nresult: {response}")


if __name__ == '__main__':
    main()

