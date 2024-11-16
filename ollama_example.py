import ollama
from tqdm import tqdm
import time

response = ollama.chat(
    model='llama3.2-vision',
    messages=[{
        'role': 'user',
        'content': 'What is in this image?',
        'images': ['water_helpers.jpg']
    }],
    options={
    "temperature": 0
  },
)

# for key, value in response.items():
#     print(f"key = {key}")
#     print(f"value = {value}")
response_text = response["message"]["content"]

print(response_text)
# print(response)
