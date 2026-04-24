pkg update && pkg upgrade -y
pkg install git python -y

git clone https://github.com/zaazouamouad/jammer.git

cd jammer
ls

chmod +x install.sh

./install.sh

python3 safe_simulator.py




1) 📡 WiFi mode
$ python3 safe_simulator.py wifi

2) 📶 Bluetooth mode
$ python3 safe_simulator.py bluetooth

3) simulation
$ python3 safe_simulator.py all



4)
$ python3 safe_simulator.py wifi -t 192.168.1.1 -p 5 -d 10
