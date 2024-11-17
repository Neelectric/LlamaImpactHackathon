from openai import OpenAI

from vllm.inputs import InputProcessingContext
from vllm.assets.audio import AudioAsset
from vllm.utils import FlexibleArgumentParser

# Modify OpenAI's API key and API base to use vLLM's API server.
openai_api_key = "EMPTY"
openai_api_base = "http://localhost:30000/v1"

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=openai_api_key,
    base_url=openai_api_base,
)

models = client.models.list()
model = models.data[0].id


# MultiModalProcessor
# CUDA_VISIBLE_DEVICES=0 python -m vllm.entrypoints.openai.api_server --gpu-memory-utilization 0.95 --model=meta-llama/Llama-3.2-11B-Vision-Instruct --tokenizer=meta-llama/Llama-3.2-11B-Vision-Instruct --dtype=bfloat16 --device=cuda --host=127.0.0.1 --port=30000 --max-model-len=8192 --quantization="fp8" --enforce_eager --max_num_seqs=8

# Single-image input inference
def run_single_image(prompt, image_path) -> None:
    ## Use image url in the payload
    # image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
    guided_json = {'properties': 
                   [{'chain_of_thought': {'title': 'Chain of Thought', 'type': 'string'}},
                   {"final_judgement_out_of_10": {'title': 'final_judgement_out_of_10', 'type': 'string'}}],
                   'required': ['chain_of_thought', "final_judgement_out_of_10"],
                    'title': 'Chain-of-thought',
                    'type': 'object'}
    chat_completion_from_url = client.chat.completions.create(
        messages=[{
            "role":
            "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt,
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "file://" + image_path
                    },
                },
            ],
        }],
        guided_json=guided_json,
        model=model,
        max_completion_tokens=600,
        temperature=0,
        
    )
    result = chat_completion_from_url.choices[0].message.content
    return result


for i in range(10):
    prompt = """Using the below image, output a 'Natural Disaster Score'. This score goes from 0 to 10, where:
    - 0 refers to 'No apparent indicators of a natural disaster currently taking place'
    - 5 refers to 'Some indicators of a potential natural disaster may be present, though full clarity is not yet available so further investigation is necessary'
    - 10 refers to 'Natural disaster clearly imminent or underway, requiring immediate attention and threatening or having already caused severe loss of life'."""
    result = run_single_image(prompt="What's in this image?", image_path="donald_j_trump.jpg")
    print("Chat completion output from image url:", result)