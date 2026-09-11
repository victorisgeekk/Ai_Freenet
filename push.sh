#!/bin/bash
echo "[*] Staging all modified files..."
git add .

echo "[*] Committing changes..."
git commit -m "Auto update: Autonomous Network Suite latest changes"
if [ $? -ne 0 ]; then
    echo "[-] Commit failed. Please check your git configuration."
    exit 1
fi

echo "[*] Pushing to GitHub repository..."
git push -u origin main
if [ $? -eq 0 ]; then
    echo "[✓] Successfully pushed to GitHub!"
else
    echo "[-] Push failed. Please check your remote URL and token."
fi

