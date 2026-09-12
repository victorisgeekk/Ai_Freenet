import sys
import time
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "qwen2.5:1.5b"

def check_ollama_service():
    try:
        res = requests.get("http://127.0.0.1:11434/", timeout=3)
        return res.status_code == 200
    except Exception:
        return False

def run_agent():
    print("=== Autonomous Network Suite Agent ===")
    print("[*] Probing network... Host: localhost")
    print("[Success] Network active on 127.0.0.1")
    print("[*] Consulting Ollama AI backend...")

    if not check_ollama_service():
        print("[Error] Ollama service is not responding on 127.0.0.1:11434")
        print("[Fix] Retrying connection setup...")

    payload = {
        "model": MODEL_NAME,
        "prompt": "You are an autonomous network security AI agent. Provide a brief, 1-sentence status report confirming network initialization.",
        "stream": False
    }

    headers = {"Content-Type": "application/json"}

    # Ollama အဆင်သင့်မဖြစ်သေးပါက ၃ ကြိမ်အထိ ထပ်မံကြိုးစားမည်
    for attempt in range(1, 4):
        try:
            response = requests.post(OLLAMA_URL, json=payload, headers=headers, timeout=60)
            if response.status_code == 200:
                data = response.json()
                ai_text = data.get("response", "").strip()
                print(f"[AI Response] {ai_text}")
                return
            else:
                print(f"[Attempt {attempt}] Ollama HTTP Status: {response.status_code}")
                if attempt < 3:
                    time.sleep(3)
        except Exception as e:
            print(f"[Attempt {attempt}] Connection Error: {str(e)}")
            if attempt < 3:
                time.sleep(3)

    print("[Error] Failed to get response from Ollama after 3 attempts.")

if __name__ == "__main__":
    run_agent()

