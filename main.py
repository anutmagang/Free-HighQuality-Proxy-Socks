import requests
import threading
import queue
import re
import os
import random
import time

# --- KONFIGURASI ---
THREADS = 150
TIMEOUT = 3 
TEST_URL_DETAIL = "http://httpbin.org/get?show_env=1"
TEST_URL_QUALITY = "https://www.google.com"

# DAFTAR SUMBER UTUH (31 SUMBER TANPA DIPOTONG)
SOURCES = [
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http",
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4",
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5",
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt",
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/proxy.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
    "https://raw.githubusercontent.com/Bes-js/public-proxy-list/refs/heads/main/proxies.txt",
    "https://raw.githubusercontent.com/vmheaven/VMHeaven-Free-Proxy-Updated/refs/heads/main/all_proxies.txt",
    "https://raw.githubusercontent.com/r00tee/Proxy-List/refs/heads/main/Socks4.txt",
    "https://raw.githubusercontent.com/r00tee/Proxy-List/refs/heads/main/Socks5.txt",
    "https://raw.githubusercontent.com/stormsia/proxy-list/refs/heads/main/working_proxies.txt",
    "https://raw.githubusercontent.com/dpangestuw/Free-Proxy/refs/heads/main/All_proxies.txt",
    "https://raw.githubusercontent.com/databay-labs/free-proxy-list/refs/heads/master/socks5.txt",
    "https://raw.githubusercontent.com/databay-labs/free-proxy-list/refs/heads/master/http.txt",
    "https://raw.githubusercontent.com/MrMarble/proxy-list/refs/heads/main/all.txt",
    "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/refs/heads/main/proxies/http.txt",
    "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/refs/heads/main/proxies/https.txt",
    "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/refs/heads/main/proxies/socks4.txt",
    "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/refs/heads/main/proxies/socks5.txt",
    "https://raw.githubusercontent.com/iplocate/free-proxy-list/refs/heads/main/all-proxies.txt",
    "https://raw.githubusercontent.com/krokmazagaga/http-proxy-list/refs/heads/main/http.txt",
    "https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/refs/heads/main/all_proxies.txt",
    "https://raw.githubusercontent.com/Mohammedcha/ProxRipper/refs/heads/main/full_proxies/http.txt",
    "https://raw.githubusercontent.com/Mohammedcha/ProxRipper/refs/heads/main/full_proxies/https.txt",
    "https://raw.githubusercontent.com/Mohammedcha/ProxRipper/refs/heads/main/full_proxies/socks4.txt",
    "https://raw.githubusercontent.com/Mohammedcha/ProxRipper/refs/heads/main/full_proxies/socks5.txt",
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/refs/heads/main/proxies/all/data.txt",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/refs/heads/master/proxies.txt"
]

results = {"all": [], "http": [], "socks4": [], "socks5": []}
countries = {}
q = queue.Queue()

# Variabel Monitoring Progress
checked_count = 0
total_to_check = 0
print_lock = threading.Lock()

# LIST USER-AGENTS MAKSIMAL (Anti-Fingerprinting)
UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (AppleWebKit/537.36; Chrome/120.0.0.0; Mobile Safari/537.36)"
]

def get_anon(res_json, my_ip):
    origin = res_json.get('origin', '')
    if my_ip and my_ip in origin: return "Transparent"
    return "Elite" if not res_json.get('headers', {}).get('Via') else "Anonymous"

def worker(my_ip):
    global checked_count
    # Gunakan satu session per thread untuk efisiensi koneksi (Keep-Alive)
    session = requests.Session()
    while not q.empty():
        proxy = q.get()
        for proto in ['http', 'socks4', 'socks5']:
            try:
                px = {"http": f"{proto}://{proxy}", "https": f"{proto}://{proxy}"}
                headers = {"User-Agent": random.choice(UA_LIST)}
                
                # Tahap 1: Validasi Anonimitas & Header
                r = session.get(TEST_URL_DETAIL, proxies=px, timeout=TIMEOUT, headers=headers)
                if r.status_code == 200:
                    data_json = r.json()
                    
                    # Tahap 2: Validasi Kualitas Nyata (Tembus Google)
                    g = session.get(TEST_URL_QUALITY, proxies=px, timeout=5, headers=headers)
                    if g.status_code == 200:
                        ip_only = proxy.split(':')[0]
                        try:
                            # Cek Lokasi Negara dengan headers lengkap
                            c_data = session.get(f"http://ip-api.com/json/{ip_only}?fields=countryCode", timeout=5, headers=headers).json()
                            cc = c_data.get('countryCode', 'UN')
                        except: cc = "UN"
                        
                        anon = get_anon(data_json, my_ip)
                        full_proxy = f"{proto}://{proxy}"
                        
                        # Simpan ke memori hasil
                        results["all"].append(f"{proxy} | {proto.upper()} | {cc} | {anon}")
                        results[proto].append(proxy)
                        
                        if cc not in countries: countries[cc] = []
                        countries[cc].append(full_proxy)
                        
                        with print_lock:
                            print(f"[SUCCESS] {proto.upper()} - {proxy} ({cc})")
                        break
            except: continue
        
        with print_lock:
            checked_count += 1
            if checked_count % 150 == 0: 
                print(f"--- Progress: {checked_count}/{total_to_check} Checked ---")
        q.task_done()

def main():
    global total_to_check
    # Siapkan folder output
    if not os.path.exists('results/countries'): os.makedirs('results/countries', exist_ok=True)
    
    scraper = requests.Session()
    try: 
        my_ip = scraper.get("https://api.ipify.org", timeout=10).text
    except: 
        my_ip = None

    print("--- Scraping Data dengan Proteksi Rate Limit MAKSIMAL ---")
    unique_proxies_set = set()
    
    for s in SOURCES:
        # Percobaan ulang (retry) 3 kali per sumber jika gagal
        for attempt in range(3):
            try:
                current_headers = {
                    "User-Agent": random.choice(UA_LIST),
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Upgrade-Insecure-Requests": "1"
                }
                
                res = scraper.get(s, timeout=25, headers=current_headers)
                
                if res.status_code == 200:
                    found = re.findall(r'\d+\.\d+\.\d+\.\d+:\d+', res.text)
                    if found:
                        before = len(unique_proxies_set)
                        unique_proxies_set.update(found)
                        added = len(unique_proxies_set) - before
                        print(f"Sumber: {s[:35]}... (+{added} unik)")
                        # Jeda adaptif agar sumber tidak memblokir IP kita
                        time.sleep(random.uniform(1.5, 3.0))
                        break
                elif res.status_code == 429:
                    # Backoff otomatis jika terkena rate limit
                    wait_time = (attempt + 1) * 5
                    print(f"! Rate Limit 429 di {s[:35]}... Tidur {wait_time}s")
                    time.sleep(wait_time)
                else:
                    time.sleep(2)
            except:
                time.sleep(2)

    total_to_check = len(unique_proxies_set)
    print(f"\nTotal Akhir Unik: {total_to_check} proxy.")
    print(f"Memulai Validasi Ganda dengan {THREADS} Threads...\n")

    for p in unique_proxies_set: q.put(p)
    # Jalankan worker threads
    for _ in range(THREADS):
        threading.Thread(target=worker, args=(my_ip,), daemon=True).start()
    q.join()

    # Ekspor Final ke file .txt
    for k, v in results.items():
        with open(f"results/{k}.txt", "w") as f: f.write("\n".join(v))
    for cc, v in countries.items():
        with open(f"results/countries/{cc}.txt", "w") as f: f.write("\n".join(v))
    
    print("--- SCRAPER SELESAI. SIAP UNTUK HUNTING ---")

if __name__ == "__main__":
    main()
