# 🚀 Auto Proxy List Updaters (Global & Fast)

Sistem otomatis pengumpulan dan validasi proxy yang diperbarui setiap **30 menit**. Menggunakan GitHub Actions untuk memastikan daftar tetap segar dan aktif.

## 📌 Fitur Utama
* **Multi-Protocol:** Mendukung HTTP, SOCKS4, dan SOCKS5.
* **Filter Ketat:** Hanya menyimpan proxy dengan Status 200 (Aktif) dan timeout < 5 detik.
* **Geo-Location:** Proxy dikelompokkan berdasarkan negara (ID, US, SG, dll).
* **Anonymity Level:** Mendeteksi Elite, Anonymous, dan Transparent proxy.

## 🔗 Endpoint List (Raw)
Anda bisa menggunakan link di bawah ini langsung di aplikasi/bot Anda:

| Kategori | Link Raw (Ganti USERNAME & REPO) |
|----------|----------------------------------|
| **All Proxies** | `https://raw.githubusercontent.com/anutmagang/Free-HighQuality-Proxy-Socks/main/results/all.txt` |
| **HTTP Only** | `https://raw.githubusercontent.com/anutmagang/Free-HighQuality-Proxy-Socks/main/results/http.txt` |
| **SOCKS5 Only** | `https://raw.githubusercontent.com/anutmagang/Free-HighQuality-Proxy-Socks/main/results/socks5.txt` |
| **Indonesia (ID)** | `https://raw.githubusercontent.com/anutmagang/Free-HighQuality-Proxy-Socks/main/results/countries/ID.txt` |

## 🛠️ Cara Kerja
1. **Scrape:** Mengambil data dari sumber provider publik.
2. **Check:** Validasi menggunakan Multithreading (100 threads).
3. **Deploy:** Hasil dikirim kembali ke repositori ini secara otomatis setiap 5 menit.

## 💰 Support This Project
Jika list proxy ini membantu pekerjaan Anda, pertimbangkan untuk mendukung biaya server (kopi) melalui link di bawah ini:

| Scan QR untuk Donasi | Link Alternatif |
| :---: | :---: |
| ![QR](https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://saweria.co/anutmagang) | [Klik di Sini (Saweria)](https://saweria.co/anutmagang) |
---
*Powered by GitHub Actions & Python*
