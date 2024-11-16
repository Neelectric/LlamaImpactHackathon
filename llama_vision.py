# system imports
import time
import json

# external imports
import requests
from transformers import AutoModelForCausalLM, AutoTokenizer, MllamaForConditionalGeneration, AutoProcessor
import torch
from tqdm import tqdm
from datasets import load_dataset
from PIL import Image

# local imports

# enivornment setup
torch.manual_seed(42)
torch.cuda.manual_seed(42)
torch.mps.manual_seed(42)

# -------------------------Start of Script------------------------- #

model_id = "meta-llama/Llama-3.2-11B-Vision-Instruct"

model = MllamaForConditionalGeneration.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)
processor = AutoProcessor.from_pretrained(model_id)

url = "https://huggingface.co/datasets/huggingface/documentation-images/resolve/0052a70beed5bf71b92610a43a52df6d286cd5f3/diffusers/rabbit.jpg"
# file = requests.get(url, stream=True).raw

image = Image.open('water_helpers.jpg')

messages = [
    {"role": "user", "content": [
        {"type": "image"},
        {"type": "text", "text": "Describe what is going on in this image."}
    ]}
]
input_text = processor.apply_chat_template(messages, add_generation_prompt=True)
inputs = processor(
    image,
    input_text,
    add_special_tokens=False,
    return_tensors="pt"
).to(model.device)

output = model.generate(
    **inputs, 
    max_new_tokens=300
    )
print(processor.decode(output[0]))
