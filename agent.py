import os
import sys
import re
import time
import subprocess
import requests
import json
import logging
from logging.handlers import RotatingFileHandler

# Configuration via environment for portability
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
MODEL_NAME = os.environ.get("OLLAMA_MODEL", "qwen2.5:1.5b")
# Execution timeout (seconds) for dynamic scripts
EXEC_TIMEOUT = int(os.environ.get("EXEC_TIMEOUT", "40"))
# Opt-in required to execute AI-generated code
ALLOW_EXEC = os.environ.get("AI_FREENET_ALLOW_EXEC", "false").lower() == "true"

# Use repository directory as working directory for portability
WORK_DIR = os.path.dirname(os.path.abspath(__file__))
# Sandbox directory where generated scripts will be written and executed
SANDBOX_DIR = os.path.join(WORK_DIR, "sandbox")
DYNAMIC_SCRIPT = os.path.join(SANDBOX_DIR, "generated_task.py")
BT = "```"

# Ensure work and sandbox directories exist
os.makedirs(WORK_DIR, exist_ok=True)
os.makedirs(SANDBOX_DIR, exist_ok=True)

# Ensure logs directory
LOG_DIR = os.path.join(WORK_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Agent logger (rotating)
agent_logger = logging.getLogger("ai_freenet_agent")
agent_logger.setLevel(logging.INFO)
if not agent_logger.handlers:
    fh = RotatingFileHandler(os.path.join(LOG_DIR, "agent.log"), maxBytes=1024 * 1024, backupCount=3, encoding='utf-8')
    fh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    agent_logger.addHandler(fh)


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
                agent_logger.info("Ollama returned non-json response")
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
            agent_logger.error("Ollama returned status %s: %s", res.status_code, res.text[:200])
            print(f"[!] Ollama returned status {res.status_code}: {res.text[:200]}")
    except Exception as e:
        agent_logger.exception("Ollama Connection Error: %s", e)
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
        agent_logger.exception("Failed to write script: %s", e)
        print(f"[!] Failed to write script: {e}")
        try:
            os.remove(tmp)
        except Exception:
            pass
        return False


def contains_dangerous_patterns(code):
    """Very conservative blacklist for obviously dangerous operations."""
    if not code:
        return False
    patterns = [
        r"\bos\.remove\b",
        r"\bshutil\.rmtree\b",
        r"\bsubprocess\.(Popen|call|run)\s*\(.*shell\s*=\s*True",
        r"\beval\b",
        r"\bexec\b",
        r"\bopen\s*\(.*[,\s]*\'w\'",
        r"\bos\.system\b",
        r"\bfork\b",
        r"\bchmod\b",
        r"\bchown\b",
    ]
    for p in patterns:
        if re.search(p, code):
            return True
    return False


def execute_with_self_healing(code_content, max_retries=3):
    current_code = code_content
    for attempt in range(1, max_retries + 1):
        if not current_code:
            agent_logger.warning("Code extraction failed; stopping retries")
            print("[!] Code extraction failed. Retrying...")
            break

        print(f"\n[+] Prepared Dynamic Task (Attempt {attempt}/{max_retries})...")

        # Safety checks before writing/executing
        if contains_dangerous_patterns(current_code):
            agent_logger.warning("Refusing to execute code due to dangerous patterns. Code snippet logged.")
            agent_logger.info("Raw rejected code:\n%s", current_code[:4000])
            print("[!] Extracted code contains potentially dangerous operations. Execution refused.")
            return None

        ok = write_script_atomic(DYNAMIC_SCRIPT, current_code)
        if not ok:
            print("[!] Could not write dynamic script. Aborting attempt.")
            break

        if not ALLOW_EXEC:
            agent_logger.info("Execution skipped because AI_FREENET_ALLOW_EXEC is not set to true")
            print("[!] Execution is disabled by default. To enable, set AI_FREENET_ALLOW_EXEC=true")
            # Save the generated script path for inspection
            agent_logger.info("Generated script saved to %s", DYNAMIC_SCRIPT)
            return None

        proc = None
        try:
            proc = subprocess.Popen(
                [sys.executable, DYNAMIC_SCRIPT],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=SANDBOX_DIR,
            )
            stdout, stderr = proc.communicate(timeout=EXEC_TIMEOUT)

            agent_logger.info("Executed dynamic script; returncode=%s", proc.returncode)
            if stdout:
                agent_logger.info("Dynamic stdout:\n%s", stdout)
            if stderr:
                agent_logger.error("Dynamic stderr:\n%s", stderr)

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
            agent_logger.warning("Dynamic script timed out; attempting to self-heal")
            print("[!] Script timed out/froze. AI is optimizing code with strict timeouts...")
            timeout_prompt = (
                f"This Python script froze or timed out:\n\n{BT}python\n{current_code}\n{BT}\n\n"
                "Rewrite it to use strict timeouts (max 3 seconds per socket/HTTP connection).\n"
                "Return ONLY valid python code wrapped in triple backticks."
            )
            raw_fixed = call_ollama(timeout_prompt)
            current_code = extract_code(raw_fixed)

        except Exception as e:
            agent_logger.exception("Unexpected exception during script execution: %s", e)
            print(f"[!] Unexpected exception during script execution: {e}")
            break

    agent_logger.error("Max retries reached or execution aborted")
    print("[!] Max retries reached. Task stopped.")
    return None


def main():
    agent_logger.info("Agent started")
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
        agent_logger.warning("No code returned by AI. Raw response logged")
        print("[!] No code returned by AI. Raw AI response (truncated):")
        print(raw_ai[:2000])
        agent_logger.info("Raw AI response:\n%s", raw_ai[:4000])
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
            agent_logger.info("AI did not return runnable next-step code")
            print("[!] AI did not return runnable next-step code. Skipping.")
    else:
        agent_logger.info("Initial dynamic task did not produce output")
        print("[!] Initial dynamic task did not produce output. Stopping.")


if __name__ == "__main__":
    main()
