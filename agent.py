import os
import sys
import re
import time
import subprocess
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "qwen2.5:1.5b"
WORK_DIR = "/root/Ai_Freenet"
DYNAMIC_SCRIPT = os.path.join(WORK_DIR, "generated_task.py")
BT = "```"  # Markdown Code Block မပျက်စေရန် String Variable အဖြစ် သုံးထားသည်

def call_ollama(prompt):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    try:
        res = requests.post(OLLAMA_URL, json=payload, timeout=120)
        if res.status_code == 200:
            return res.json().get("response", "").strip()
    except Exception as e:
        print(f"[!] Ollama Connection Error: {str(e)}")
    return ""

def extract_code(raw_response):
    """AI တုံ့ပြန်ချက်ထဲမှ Python Code ကို တိကျစွာ ခွဲထုတ်ယူခြင်း"""
    match = re.search(r'```(?:python)?\s*(.*?)\s*```', raw_response, re.DOTALL)
    if match:
        return match.group(1).strip()
    lines = raw_response.split('\n')
    valid_lines = [l for l in lines if not l.strip().startswith(("Here", "Sure", "Certainly", "Note:", "This script"))]
    return "\n".join(valid_lines).strip()

def execute_with_self_healing(code_content, max_retries=3):
    current_code = code_content
    for attempt in range(1, max_retries + 1):
        if not current_code:
            print("[!] Code extraction failed. Retrying...")
            break

        print(f"\n[+] Executing Dynamic Task (Attempt {attempt}/{max_retries})...")
        
        with open(DYNAMIC_SCRIPT, "w") as f:
            f.write(current_code)

        try:
            proc = subprocess.Popen(
                [sys.executable, DYNAMIC_SCRIPT],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = proc.communicate(timeout=40)

            if proc.returncode == 0:
                print("\n[SUCCESS] Execution Output:")
                print(stdout)
                return stdout
            else:
                error_msg = stderr if stderr else stdout
                print(f"[!] Execution Error Detected:\n{error_msg}")
                print("[*] AI is analyzing error log and self-healing script...")
                
                fix_prompt = f"Fix this Python code that failed to run on Termux/Ubuntu.\n\nCode:\n{BT}python\n{current_code}\n{BT}\n\nError:\n{error_msg}\n\nReturn ONLY valid python code wrapped in {BT}python ... {BT} markdown block. No conversational text."
                raw_fixed = call_ollama(fix_prompt)
                current_code = extract_code(raw_fixed)

        except subprocess.TimeoutExpired:
            proc.kill()
            print("[!] Script timed out/froze. AI is optimizing code with strict timeouts...")
            timeout_prompt = f"This Python script froze or timed out:\n\n{BT}python\n{current_code}\n{BT}\n\nRewrite it to use strict timeouts (max 3 seconds per socket/HTTP connection).\nReturn ONLY valid python code wrapped in {BT}python ... {BT} markdown block."
            raw_fixed = call_ollama(timeout_prompt)
            current_code = extract_code(raw_fixed)

    print("[!] Max retries reached. Task stopped.")
    return None

def main():
    print("=== Ai_Freenet Autonomous Self-Healing Engine ===")
    print("[*] AI is dynamically deciding network discovery tasks...")
    
    initial_prompt = f"Write a python script to inspect local network environment (Local IP, default gateway, DNS status, and scan ports 80, 443, 8080, 53, 11434).\nPrint all diagnostic results clearly.\nReturn ONLY valid python code inside a {BT}python ... {BT} block."
    raw_ai = call_ollama(initial_prompt)
    initial_code = extract_code(raw_ai)

    output = execute_with_self_healing(initial_code)
    
    if output:
        print("\n[*] AI is deciding next diagnostic/bypass step based on live scan results...")
        next_prompt = f"Based on these live network diagnostic results:\n{output}\n\nWrite a python script to test available bypass tricks, tools, or DNS/proxy connections suitable for this network condition.\nReturn ONLY valid python code inside a {BT}python ... {BT} block."
        raw_next = call_ollama(next_prompt)
        next_code = extract_code(raw_next)
        execute_with_self_healing(next_code)

if __name__ == "__main__":
    main()

