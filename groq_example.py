from groq import Groq
import base64

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your image
image_path = "donald_j_trump.jpg"

# Getting the base64 string
base64_image = encode_image(image_path)

client = Groq()

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": """Using the image, output a 'Natural Disaster Score'. This score goes from 0 to 10, where:
                - 0 refers to 'No apparent indicators of a natural disaster currently taking place'
                - 5 refers to 'Some indicators of a potential natural disaster may be present, though full clarity is not yet available so further investigation is necessary'
                - 10 refers to 'Natural disaster clearly imminent or underway, requiring immediate attention and threatening or having already caused severe loss of life'.
                Do not hallucinate. Consider the risk of false negatives, and return a judgmenet of 0 if no indicators of disasters are present.
                Please output your judgement in json format, with the following fields:
                {
                "CHAIN_OF_THOUGHT": "",
                "FINAL_JUDGEMENT_OUT_OF_10": ,
                }
                The following are examples for you to follow:
                {
                "CHAIN_OF_THOUGHT": "The image shows a man in a black shirt and hat, with a serious expression. The text on his shirt reads 'FAMILY' and 'LIF'. The image also shows a brick wall in the background. There is no clear indication of a natural disaster in the image.",
                "FINAL_JUDGEMENT_OUT_OF_10": 0
                }
                {
                "CHAIN_OF_THOUGHT": "A torrential downpour appears to be taking place in the area, possibly triggering a flood. However, an ambulance has also been spotted near the scene of destruction, which may indicate that the impact is localised, threatening life. A more intense review suggests that the scale of the devastation is too vast for any timely rescue operations, confirming that a disastrous flood has indeed occurred.",
                "FINAL_JUDGEMENT_OUT_OF_10": 7
                }
                 """},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                    },
                },
            ],
        }
    ],
    model="llama-3.2-11b-vision-preview",
    temperature=0.5,
    max_tokens=1024,
    top_p=1,
    stream=False,
    response_format={"type": "json_object"},
    stop=None,
)


message = chat_completion.choices[0].message
content = message.content
print(content)
