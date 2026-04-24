pkg update && pkg upgrade -y
pkg install git python -y

git clone https://github.com/zaazouamouad/jammer.git

cd jammer
ls

chmod +x install.sh

./install.sh

python3 safe_simulator.py
