#!/bin/bash

echo "======================================"
echo "      Starting Ai_Freenet System      "
echo "======================================"

# 1. Python Virtual Environment စစ်ဆေးခြင်း
if [ ! -d "ai_env" ]; then
    echo "[+] Creating Python Virtual Environment (ai_env)..."
    python3 -m venv ai_env
fi
source ai_env/bin/activate

# 2. Package များ သွင်းခြင်း
echo "[+] Checking Required Packages..."
pip install --upgrade pip > /dev/null 2>&1
pip install textual requests > /dev/null 2>&1

# 3. Ollama Service မပွင့်သေးပါက ပွင့်အောင် ဖွင့်ပြီး စောင့်ပေးခြင်း
echo "[+] Ensuring Ollama Background Service is Active..."
if ! pgrep -x "ollama" > /dev/null; then
    nohup ollama serve > /dev/null 2>&1 &
    echo "[+] Waiting for Ollama server to initialize..."
    sleep 8
else
    echo "[+] Ollama service is already running."
fi

# 4. Model စစ်ဆေးခြင်း
echo "[+] Verifying AI Model (qwen2.5:1.5b)..."
ollama pull qwen2.5:1.5b

# 5. Main App မောင်းနှင်ခြင်း
echo "[+] Launching Main Application (main.py)..."
python3 main.py

