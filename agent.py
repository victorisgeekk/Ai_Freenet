import os
import sys
import re
import time
import subprocess
import requests
import json

# Configuration via environment for portability
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
MODEL_NAME = os.environ.get("OLLAMA_MODEL", "qwen2.5:1.5b")
# Execution timeout (seconds) for dynamic scripts
EXEC_TIMEOUT = int(os.environ.get("EXEC_TIMEOUT", "40"))

# Use repository directory as working directory for portability
WORK_DIR = os.path.dirname(os.path.abspath(__file__))
DYNAMIC_SCRIPT = os.path.join(WORK_DIR, "generated_task.py")
BT = "```"

# Ensure work directory exists (safe no-op for repo root)
os.makedirs(WORK_DIR, exist_ok=True)


def call_ollama(prompt):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    try:
        res = requests.post(OLLAMA_URL, json=payload, timeout=120)
        if res.ok:
            # Try parsing JSON, fall back to raw text
            try:
                data = res.json()
            except ValueError:
                return res.text.strip()

            # Flexible parsing for different LLM response schemas
            if isinstance(data, dict):
                # Common Ollama-like schema
                if "response" in data:
                    return data.get("response", "").strip()
                # Some models return results/text
                if "results" in data and isinstance(data["results"], list) and data["results"]:
                    first = data["results"][0]
                    if isinstance(first, dict):
                        return (first.get("text") or first.get("content") or str(first)).strip()
                    return str(first).strip()
                if "text" in data:
                    return data.get("text", "").strip()
            # Fallback: stringify
            return json.dumps(data)
        else:
            print(f"[!] Ollama returned status {res.status_code}: {res.text[:200]}")
    except Exception as e:
        print(f"[!] Ollama Connection Error: {str(e)}")
    return ""


def extract_code(raw_response):
    """Extract the most likely python code block from an LLM response.
    Accepts fences like ```python, ```py, or plain ``` and picks the largest block when multiple exist.
    Falls back to heuristic line filtering if no fence is found.
    """
    if not raw_response:
        return ""

    # Find all triple-backtick blocks with optional language label
    blocks = re.findall(r'```(?:py(?:thon)?\s*)?\n?(.*?)```', raw_response, re.DOTALL | re.IGNORECASE)
    if blocks:
        # Prefer the longest block (likely the full code)
        candidate = max((b.strip() for b in blocks), key=len)
        if candidate:
            return candidate

    # Some models omit fences; try to find code-like regions by indentation or 'def'/'import'
    lines = raw_response.split('\n')
    # Heuristic: include lines that look like code
    code_lines = [l for l in lines if l.startswith('    ') or l.startswith('\t') or re.match(r'^(import |from |def |class |if |for |while |print\()', l.strip())]
    if code_lines:
        return '\n'.join(l.lstrip() for l in code_lines).strip()

    # fallback: try to remove common assistant preamble lines
    valid_lines = [l for l in lines if not l.strip().startswith(("Here", "Sure", "Certainly", "Note:", "This script"))]
    return "\n".join(valid_lines).strip()


def write_script_atomic(path, content):
    # Write via temporary file then rename for atomicity
    import tempfile
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        return True
    except Exception as e:
        print(f"[!] Failed to write script: {e}")
        try:
            os.remove(tmp)
        except Exception:
            pass
        return False


def execute_with_self_healing(code_content, max_retries=3):
    current_code = code_content
    for attempt in range(1, max_retries + 1):
        if not current_code:
            print("[!] Code extraction failed. Retrying...")
            break

        print(f"\n[+] Executing Dynamic Task (Attempt {attempt}/{max_retries})...")

        ok = write_script_atomic(DYNAMIC_SCRIPT, current_code)
        if not ok:
            print("[!] Could not write dynamic script. Aborting attempt.")
            break

        proc = None
        try:
            proc = subprocess.Popen(
                [sys.executable, DYNAMIC_SCRIPT],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = proc.communicate(timeout=EXEC_TIMEOUT)

            if proc.returncode == 0:
                print("\n[SUCCESS] Execution Output:")
                print(stdout)
                return stdout
            else:
                error_msg = stderr if stderr else stdout
                print(f"[!] Execution Error Detected:\n{error_msg}")
                print("[*] AI is analyzing error log and self-healing script...")

                fix_prompt = (
                    f"Fix this Python code that failed to run on Termux/Ubuntu.\n\n"
                    f"Code:\n{BT}python\n{current_code}\n{BT}\n\n"
                    f"Error:\n{error_msg}\n\nReturn ONLY valid python code wrapped in triple backticks."
                )
                raw_fixed = call_ollama(fix_prompt)
                current_code = extract_code(raw_fixed)

        except subprocess.TimeoutExpired:
            if proc:
                try:
                    proc.kill()
                except Exception:
                    pass
            print("[!] Script timed out/froze. AI is optimizing code with strict timeouts...")
            timeout_prompt = (
                f"This Python script froze or timed out:\n\n{BT}python\n{current_code}\n{BT}\n\n"
                "Rewrite it to use strict timeouts (max 3 seconds per socket/HTTP connection).\n"
                "Return ONLY valid python code wrapped in triple backticks."
            )
            raw_fixed = call_ollama(timeout_prompt)
            current_code = extract_code(raw_fixed)

        except Exception as e:
            print(f"[!] Unexpected exception during script execution: {e}")
            break

    print("[!] Max retries reached. Task stopped.")
    return None


def main():
    print("=== Ai_Freenet Autonomous Self-Healing Engine ===")
    print("[*] AI is dynamically deciding network discovery tasks...")

    initial_prompt = (
        "Write a python script to inspect local network environment (Local IP, default gateway, DNS status, "
        "and scan ports 80, 443, 8080, 53, 11434).\nPrint all diagnostic results clearly. Use only the Python standard library. "
        "Do not run privileged commands (no sudo). Wrap the script output in clear markers."
    )
    raw_ai = call_ollama(initial_prompt)
    initial_code = extract_code(raw_ai)

    if not initial_code:
        print("[!] No code returned by AI. Raw AI response (truncated):")
        print(raw_ai[:2000])
        return

    output = execute_with_self_healing(initial_code)

    if output:
        print("\n[*] AI is deciding next diagnostic/bypass step based on live scan results...")
        next_prompt = (
            f"Based on these live network diagnostic results:\n{output}\n\n"
            "Write a python script to test available bypass tricks, tools, or DNS/proxy connections suitable for this network. "
            "Prefer standard library usage and avoid privileged operations. Return ONLY valid python code wrapped in triple backticks."
        )
        raw_next = call_ollama(next_prompt)
        next_code = extract_code(raw_next)
        if next_code:
            execute_with_self_healing(next_code)
        else:
            print("[!] AI did not return runnable next-step code. Skipping.")
    else:
        print("[!] Initial dynamic task did not produce output. Stopping.")


if __name__ == "__main__":
    main()
