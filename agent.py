import socket
import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5"

def check_network():
    print("[*] Probing network... Host: localhost")
    try:
        # Local socket connection check
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect(('127.0.0.1', 11434))
        s.close()
        print("[Success] Network active on 127.0.0.1:11434 (Ollama is reachable)")
        return True
    except Exception as e:
        print(f"[Error] Network probe failed: {str(e)}")
        return False

def ask_ollama(prompt):
    print("[*] Consulting Ollama AI backend...")
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json().get("response", "No response from model.")
            print(f"\n[AI Healing Suggestion]:\n{result}")
        else:
            print(f"[Error] Ollama returned status code {response.status_code}")
    except Exception as e:
        print(f"[Error] Failed to connect to Ollama API: {str(e)}")

if __name__ == "__main__":
    print("=== Autonomous Network Suite Agent Initialized ===")
    is_online = check_network()
    
    if is_online:
        ask_ollama("Network probe is successful. Give a brief operational status check for the autonomous network suite.")
    else:
        ask_ollama("Network probe failed on local port 11434. Provide troubleshooting steps to fix Ollama service.")

