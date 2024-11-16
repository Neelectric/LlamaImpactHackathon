import litserve as ls
from vllm import LLM
from vllm.sampling_params import SamplingParams

class LlamaAPI(ls.LitAPI):
    def setup(self, device):
        # Load the model
        print("loading llama")
        model_name = "meta-llama/Llama-3.2-11B-Vision-Instruct"
        self.llm = LLM(
            model=model_name, 
            tokenizer_mode="auto", 
            max_model_len=2048
            )

    def decode_request(self, request):
        return (request["image"], request["prompt"])

    def predict(self, input):
        messages = [{"role": "user", "content": [
            {"type": "text", "text": input[1]}, 
            {"type": "image_url", "image_url": {"url": input[0]}}
            ]}]

        sampling_params = SamplingParams(
            max_tokens=2048, 
            temperature=0.7
            )
        outputs = self.llm.chat(
            messages=messages, 
            sampling_params=sampling_params
            )
        return outputs[0].outputs[0].text

    def encode_response(self, result):
        return result

# Start the server
if __name__ == "__main__":
    api = LlamaAPI()
    server = ls.LitServer(api, timeout=False)
    server.run(port=8000)