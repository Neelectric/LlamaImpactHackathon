from openai import OpenAI

client = OpenAI(base_url="http://localhost:3000/v1")

# get the available models
# model_list = client.models.list()
# print(model_list)

response = client.chat.completions.create(
  model="meta-llama/Llama-3.2-11B-Vision-Instruct",
  messages=[
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "What’s in this image?"},
        {
          "type": "image_url",
          "image_url": {
            "url": "https://upload.wikimedia.org/wikipedia/commons/e/ea/Bento_at_Hanabishi%2C_Koyasan.jpg",
          },
        },
      ],
    }
  ],
  max_tokens=300,
)

print(response.choices[0])
