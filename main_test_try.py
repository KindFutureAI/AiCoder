# Copyright (c) Alibaba Cloud.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

"""A simple command-line interactive chat demo."""

import argparse
import os
import platform
import shutil
from copy import deepcopy
from threading import Thread

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
from transformers.trainer_utils import set_seed
 
# DEFAULT_CKPT_PATH = "_app_src/model_local/Qwen2.5-Coder-1.5B-Instruct"
# DEFAULT_CKPT_PATH = "_app_src/model_local/Qwen2.5-0.5B-Instruct"
DEFAULT_CKPT_PATH = "_app_src/model_local/Qwen2.5-Coder-1.5B-Instruct"

 


def _load_model_tokenizer(args):
    tokenizer = AutoTokenizer.from_pretrained(
        args.checkpoint_path,
        resume_download=True,
    ) 

    model = AutoModelForCausalLM.from_pretrained(
        args.checkpoint_path,
        torch_dtype=torch.bfloat16,
        device_map="auto", 
    ).eval()
    model.generation_config.max_new_tokens = 2048  # For chat.

    return model, tokenizer


def _gc():
    import gc

    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def _clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


def _print_history(history):
    terminal_width = shutil.get_terminal_size()[0]
    print(f"History ({len(history)})".center(terminal_width, "="))
    for index, (query, response) in enumerate(history):
        print(f"User[{index}]: {query}")
        print(f"Qwen[{index}]: {response}")
    print("=" * terminal_width)


def _get_input() -> str:
    while True:
        try:
            message = input("User> ").strip()
        except UnicodeDecodeError:
            print("[ERROR] Encoding error in input")
            continue
        except KeyboardInterrupt:
            exit(1)
        if message:
            return message
        print("[ERROR] Query is empty")


def _chat_stream(model, tokenizer, query, history):
    conversation = []
    for query_h, response_h in history:
        conversation.append({"role": "user", "content": query_h})
        conversation.append({"role": "assistant", "content": response_h})
    conversation.append({"role": "user", "content": query})
    input_text = tokenizer.apply_chat_template(
        conversation,
        add_generation_prompt=True,
        tokenize=False,
    )
    inputs = tokenizer([input_text], return_tensors="pt").to(model.device)
    streamer = TextIteratorStreamer(
        tokenizer=tokenizer, skip_prompt=True, timeout=60.0, skip_special_tokens=True
    )
    generation_kwargs = {
        **inputs,
        "streamer": streamer,
    }
    thread = Thread(target=model.generate, kwargs=generation_kwargs)
    thread.start()

    for new_text in streamer:
        yield new_text


def main():
    parser = argparse.ArgumentParser(
        description="Qwen2.5-Instruct command-line interactive chat demo."
    )
    parser.add_argument(
        "-c",
        "--checkpoint-path",
        type=str,
        default=DEFAULT_CKPT_PATH,
        help="Checkpoint name or path, default to %(default)r",
    )
    parser.add_argument("-s", "--seed", type=int, default=1234, help="Random seed")
    parser.add_argument(
        "--cpu-only", action="store_true", help="Run demo with CPU only"
    )
    args = parser.parse_args()

    history, response = [], ""

    model, tokenizer = _load_model_tokenizer(args)
    orig_gen_config = deepcopy(model.generation_config)

    for name, param in model.named_parameters():
        print(name, param.requires_grad)

  

if __name__ == "__main__":
    main()
