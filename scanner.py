import requests
import threading
import queue
import ipaddress
import os
import re
import random
import time

# --- KONFIGURASI HUNTER (ULTIMATE NO LIMIT) ---
THREADS_SCAN = 150       
TIMEOUT_SCAN = 3         
TEST_URL_DETAIL = "http://httpbin.org/get?show_env=1"
TEST_URL_QUALITY = "https://www.google.com"

# SEMUA PORT AKTIF - GAK ADA YANG DIKURANGIN
PORTS = [80, 8080, 3128, 1080, 8888, 7890, 9050, 5678]

hunted_results = []
q_scan = queue.Queue()
print_lock = threading.Lock()
deep_scanned_subnets = set() # Biar gak looping selamanya di subnet yang sama

# Variabel Baru untuk Tracking (Biar gak stuck)
checked_hunted = 0

UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"
]

def get_anon(res_json, my_ip):
    origin = res_json.get('origin', '')
    if my_ip and my_ip in origin: return "Transparent"
    return "Elite" if not res_json.get('headers', {}).get('Via') else "Anonymous"

def hunter_worker(my_ip):
    global checked_hunted
    session = requests.Session()
    while not q_scan.empty():
        proxy = q_scan.get()
        for proto in ['http', 'socks5']:
            try:
                px = {"http": f"{proto}://{proxy}", "https": f"{proto}://{proxy}"}
                headers = {"User-Agent": random.choice(UA_LIST)}
                
                # Tahap 1: Validasi Detail
                r = session.get(TEST_URL_DETAIL, proxies=px, timeout=TIMEOUT_SCAN, headers=headers)
                if r.status_code == 200:
                    # Tahap 2: Validasi Kualitas Google
                    g = session.get(TEST_URL_QUALITY, proxies=px, timeout=5, headers=headers)
                    if g.status_code == 200:
                        ip_only = proxy.split(':')[0]
                        
                        # Tahap 3: ISP & Country Detection
                        try:
                            geo_url = f"http://ip-api.com/json/{ip_only}?fields=status,countryCode,isp"
                            c_req = session.get(geo_url, timeout=5)
                            c_data = c_req.json()
                            if c_data.get('status') == 'success':
                                cc = c_data.get('countryCode', 'UN')
                                isp = c_data.get('isp', 'Unknown ISP')
                                isp_name = (isp[:25] + '..') if len(isp) > 25 else isp
                            else:
                                cc, isp_name = "UN", "Private/Unknown"
                        except:
                            cc, isp_name = "UN", "Lookup Error"
                        
                        anon = get_anon(r.json(), my_ip)
                        result_entry = f"{proxy} | {proto.upper()} | {cc} | {anon} | {isp_name}"
                        
                        with print_lock:
                            print(f"[HUNTED SUCCESS] {result_entry}")
                        hunted_results.append(result_entry)

                        # --- LOGIKA INSTINCT DEEP SCAN (RE-ENGAGE) ---
                        subnet = ".".join(ip_only.split('.')[:3])
                        if anon != "Transparent" and subnet not in deep_scanned_subnets:
                            with print_lock:
                                print(f"[*] ALERT: Nemu {anon} di {isp_name}! Melakukan Deep Scan Masif Subnet {subnet}...")
                            
                            deep_scanned_subnets.add(subnet)
                            for d in range(1, 255):
                                for port in PORTS:
                                    q_scan.put(f"{subnet}.{d}:{port}")
                        
                        time.sleep(1.2) 
                        break
            except:
                continue
        
        # --- PROGRESS INDICATOR (BIAR GAK BERASA STUCK) ---
        with print_lock:
            checked_hunted += 1
            if checked_hunted % 500 == 0:
                print(f"--- Hunter Progress: {checked_hunted} Checked | Sisa Antrean: {q_scan.qsize()} ---")
        
        q_scan.task_done()

def main():
    output_dir = 'results/hunted'
    if not os.path.exists(output_dir): os.makedirs(output_dir, exist_ok=True)
    
    try: 
        my_ip = requests.get("https://api.ipify.org", timeout=10).text
    except: 
        my_ip = None

    if not os.path.exists('results/all.txt'):
        print("Data all.txt tidak ditemukan!")
        return

    print("--- MEMULAI TOTAL WAR + INSTINCT OVERDRIVE (PROGRESS UPDATED) ---")
    
    active_subnets = set()
    with open('results/all.txt', 'r') as f:
        for line in f:
            match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
            if match:
                parts = match.group(1).split('.')
                active_subnets.add(f"{parts[0]}.{parts[1]}.{parts[2]}")

    print(f"Ditemukan {len(active_subnets)} Subnet Potensial. Hajar Total!")

    for subnet in active_subnets:
        for d in range(1, 255):
            target_ip = f"{subnet}.{d}"
            for port in PORTS: 
                q_scan.put(f"{target_ip}:{port}")

    print(f"Total target serangan: {q_scan.qsize()} kombinasi unik.")

    for _ in range(THREADS_SCAN):
        threading.Thread(target=hunter_worker, args=(my_ip,), daemon=True).start()
    
    q_scan.join()

    if hunted_results:
        file_path = f"{output_dir}/hunted_elite.txt"
        old_data = []
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                old_data = f.read().splitlines()
        
        merged_data = old_data + hunted_results
        unique_final = list(set(merged_data))
        
        with open(file_path, "w") as f:
            f.write("\n".join(unique_final))
            
        print(f"--- SELESAI: Database diperbarui dengan {len(unique_final)} Proxy Unik! ---")

if __name__ == "__main__":
    main()
