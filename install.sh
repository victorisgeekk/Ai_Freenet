#!/bin/bash

clear
echo "=================================================="
echo "    Ai_Freenet One-Click Auto Installer & Runner  "
echo "=================================================="

# ၁။ Termux အခြေခံ Package များ သွင်းခြင်း
echo "[+] Updating Termux environment..."
pkg update -y && pkg upgrade -y -o Dpkg::Options::="--force-confnew"
pkg install proot-distro git wget curl nano -y

# ၂။ Ubuntu ရှိ/မရှိ စစ်ဆေးပြီး သွင်းခြင်း
if ! proot-distro list | grep -q "ubuntu.*installed"; then
    echo "[+] Installing Ubuntu OS..."
    proot-distro install ubuntu
fi

# ၃။ နောက်တစ်ကြိမ် Termux ဖွင့်လျှင် တန်း run နိုင်ရန် Home တွင် run.sh Shortcut ဖန်တီးပေးခြင်း
cat << 'EOF' > ~/run.sh
#!/bin/bash
proot-distro login ubuntu -- bash -c "cd /root/Ai_Freenet && ./run.sh"
EOF
chmod +x ~/run.sh

# ၄။ Ubuntu ထဲသို့ ဝင်ရောက်ပြီး စနစ်တစ်ခုလုံး အလိုအလျောက် သွင်းယူခြင်း
proot-distro login ubuntu -- bash -c "
    export DEBIAN_FRONTEND=noninteractive
    
    echo '[+] Updating Ubuntu packages...'
    apt update -y && apt install python3 python3-venv python3-pip git curl -y

    # Ollama မရှိသေးပါက သွင်းခြင်း
    if ! command -v ollama &> /dev/null; then
        echo '[+] Installing Ollama Server...'
        curl -fsSL https://ollama.com/install.sh | sh
    fi

    # GitHub Repository ကို Clone ဆွဲခြင်း (သို့) Update လုပ်ခြင်း
    cd /root
    if [ ! -d 'Ai_Freenet' ]; then
        echo '[+] Cloning Ai_Freenet repository...'
        git clone https://github.com/victorisgeekk/Ai_Freenet.git
    else
        echo '[+] Repository already exists. Pulling latest code...'
        cd Ai_Freenet && git pull && cd ..
    fi

    cd /root/Ai_Freenet

    # အတွင်းပိုင်း run.sh ကို ခွင့်ပြုချက်ပေးပြီး မောင်းနှင်ခြင်း
    if [ -f 'run.sh' ]; then
        chmod +x run.sh
        ./run.sh
    else
        echo '[!] Error: run.sh file not found in repository!'
    fi
"

