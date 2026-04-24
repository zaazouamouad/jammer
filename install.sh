#!/bin/bash

echo "=============================="
echo "   Installing Project"
echo "=============================="

if command -v pkg >/dev/null 2>&1; then
    echo "[+] Termux detected"
    pkg update -y && pkg upgrade -y
    pkg install git python -y
else
    echo "[+] Linux detected"
    sudo apt update -y && sudo apt install git python3 python3-pip -y
fi

echo "[+] Installing dependencies..."
pip install -r requirements.txt 2>/dev/null

echo "[+] Done!"
echo "[+] Run: python3 main.py"
