# Autonomous Network Suite

Android ပလက်ဖောင်း (Termux) အတွက် တည်ဆောက်ထားသော အလိုအလျောက် Network Bypass၊ Fingerprinting နှင့် AI Self-Healing စွမ်းရည်များ ပါဝင်သည့် ပညာရပ်ဆိုင်ရာ ပရောဂျက်တစ်ခု ဖြစ်ပါသည်။

## Project Features

* **Multi-Environment Fingerprinting:** Atom Mobile Data၊ Standard Wi-Fi နှင့် UniFi Captive Hotspot များကို အလိုအလျောက် ခွဲခြားထောက်လှမ်းခြင်း။
* **Parallel Mesh Probing:** WebSocket နှင့် HTTP Vector များကို ThreadPoolExecutor ဖြင့် တစ်ပြိုင်နက် အမြန်ဆုံး စမ်းသပ်ခြင်း။
* **AI Runtime Self-Healing:** Local Ollama (Qwen2.5) ကို အသုံးပြု၍ Runtime Error များကို အလိုအလျောက် ပြင်ဆင်ခြင်း (Self-patch/Fallback)။
* **TUN Mode & VpnService Bridge:** Non-root Android ပတ်ဝန်းကျင်တွင် System Traffic များကို Local Port သို့ မှန်ကန်စွာ လမ်းကြောင်းလွှဲပေးခြင်း။
* **Automated CI/CD APK Generation:** GitHub Actions ကို အသုံးပြု၍ ကုဒ်တင်လိုက်သည်နှင့် Android APK ကို အလိုအလျောက် တည်ဆောက်ပေးခြင်း။

## Directory Structure

```text
autonomous-network-suite/
├── .github/
│   └── workflows/
│       └── build_apk.yml     # GitHub Actions CI/CD pipeline for APK building
├── agent.py                  # Core autonomous intelligence and network logic
├── main.py                   # Kivy-based Cyber-Terminal graphical interface
├── buildozer.spec            # Android packaging configuration
├── requirements.txt          # Python dependencies
├── setup.sh                  # Automated project structure setup script
└── push.sh                   # Automated Git synchronization script
