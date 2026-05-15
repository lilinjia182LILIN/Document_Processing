import requests
from pathlib import Path
import requests

def call_llm_no_stream(content):
    content = content + "/no-think"
    url = "http://192.168.1.2:31434/api/chat"
    payload = {
        "message": [
            {
             "role": "user",
             "content": content
            }
        ],
        "model": "qwen3:32b-5w", # qwn3:32b-5w deepseek-r1:32b
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 10000
        }
    }

if __name__ == '__main__':
    call_llm_no_stream("你好")

    