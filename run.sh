#!/bin/bash

echo "======================================"
echo "      Starting Ai_Freenet System      "
echo "======================================"

# ၁။ Python Virtual Environment စစ်ဆေးခြင်း
if [ ! -d "ai_env" ]; then
    echo "[+] Creating Python Virtual Environment (ai_env)..."
    python3 -m venv ai_env
fi
echo "[+] Activating Virtual Environment..."
source ai_env/bin/activate

# ၂။ လိုအပ်သော Python Library များ သွင်းခြင်း
echo "[+] Installing Required Packages..."
pip install --upgrade pip > /dev/null 2>&1
pip install textual requests

# ၃။ Ollama Server ကို နောက်ကွယ်တွင် Run ခြင်း
echo "[+] Launching Ollama Server..."
nohup ollama serve > /dev/null 2>&1 &
sleep 5

# ၄။ AI Model စစ်ဆေးခြင်းနှင့် ဒေါင်းလုဒ်ဆွဲခြင်း
echo "[+] Checking AI Model (qwen2.5:1.5b)..."
ollama pull qwen2.5:1.5b

# ၅။ Frontend UI ကို စတင်မောင်းနှင်ခြင်း
echo "[+] Launching Main Application (main.py)..."
python3 main.py

