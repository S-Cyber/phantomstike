#!/usr/bin/env python3
import argparse
import time
import dns.resolver
import requests
import socket  # Import socket untuk mendapatkan IP address
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from bs4 import BeautifulSoup  # Untuk mengambil judul halaman

banner = """                                                                                                                                                    
                                @                                     @@                              
                               @@@@@                                @@@@                              
                               @@@@@@@@                          @@@@@@@@                             
                               @@@@   @@@                      @@@   @@@@                             
                              @@  @@    @@@                 @@@@    @@ @@                             
                              @@  @@       @@@            @@@      @@   @                             
                              @@   @@        @@@@@@@@@@@@@@        @@   @@                            
                              @@    @@        @@        @@        @@    @@                            
                             @@     @@        @@        @@        @@     @                            
                             @@      @@       @@        @@       @@      @@                           
                             @@      @@       @@        @@      @@       @@                           
                            @@        @@      @@        @@      @@       @@                           
                            @@   @@@@@@@      @@        @@      @@@@@@   @@                           
                            @@@@              @@        @@             @@@@@                          
                            @                 @@        @@               @@@                          
                            @         @@@@@@@@@          @@@@@@@@        @@@                          
                            @  @@@@@@@@@                        @@@@@@@@ @@@                          
                            @@@                                         @@@                           
                             @                                           @@                           
                             @@      @@@@@@@               @@@@@@@@      @                            
                              @@     @@    @@@            @@    @@@     @@                            
                              @@      @@@@@@@@@          @@@@@@@@      @@                             
                               @@       @@@   @@@      @@@   @@@       @@                             
                                @@@            @@     @@             @@@                              
                                  @@@           @     @@          @@@@                                
                                     @@@        @     @@       @@@                                    
                                       @@@      @     @@     @@@                                      
                                         @@     @@    @@     @@                                       
                                         @@     @@@@@@@@    @@                                        
                                          @@    @@@  @@@   @@@                                        
                                            @@@   @@@@  @@@@                                          
                                               @@@@@@@@@@                                             
                                                  @@@@                                                
                                                                                                                                                                                                            
"""

print(banner)



def check_status_code(url, status_codes, target_domain):
    """
    Memeriksa status kode HTTP dan mengabaikan redirect ke luar domain utama.
    """
    try:
        response = requests.get(url, timeout=5, allow_redirects=False)  # Tidak mengikuti redirect otomatis
        status_code = response.status_code

        # Jika ada redirect (3xx) dan mengarah ke luar domain, abaikan
        if 300 <= status_code < 400 and 'Location' in response.headers:
            redirected_url = response.headers['Location']
            parsed_redirect = urlparse(redirected_url)
            redirected_domain = parsed_redirect.netloc

            if redirected_domain and not redirected_domain.endswith(target_domain):
                return None, None  # Abaikan hasil ini

        if not status_codes or status_code in status_codes:
            return True, status_code
    except requests.RequestException:
        pass

    return None, None

def get_ip_from_subdomain(subdomain):
    """
    Mendapatkan IP dari subdomain menggunakan socket.
    """
    try:
        ip = socket.gethostbyname(subdomain)
        return ip
    except socket.gaierror:
        return None

def get_title_from_subdomain(url):
    """
    Mengambil judul halaman dari subdomain.
    """
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else "No title found"
        return title
    except requests.RequestException:
        return None

def scan_subdomain(subdomain, domain, delay, check_cname, status_codes, progress, ip_only, ip_option, output_file, title_option):
    """
    Melakukan resolusi DNS dan pengecekan HTTP/HTTPS pada subdomain.
    """
    full_domain = f"{subdomain.strip()}.{domain}"

    # Resolusi DNS untuk memeriksa A record
    try:
        dns.resolver.resolve(full_domain, 'A')
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.Timeout):
        progress.update(1)  # Update progress bar
        return None  # Subdomain tidak ditemukan di DNS

    # Pengecekan CNAME jika --cname diaktifkan
    if check_cname:
        try:
            cname_result = dns.resolver.resolve(full_domain, 'CNAME')
            cname = cname_result[0].to_text()
            tqdm.write(f"[+] CNAME ditemukan untuk {full_domain}: {cname}")
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            pass

    # Verifikasi HTTP/HTTPS dan pengecekan status kode
    for protocol in ["http", "https"]:
        url = f"{protocol}://{full_domain}"
        valid, status_code = check_status_code(url, status_codes, domain)
        if valid:
            ip = get_ip_from_subdomain(full_domain)
            title = None
            if title_option:  # Jika opsi --title diaktifkan
                title = get_title_from_subdomain(url)
            progress.update(1)  # Update progress bar
            if ip_option:  # Jika opsi --ip diaktifkan
                result = f"{full_domain} --> {ip}"
                if title:
                    result += f" (Title: {title})"
                tqdm.write(f"[+] {result}")
                if output_file:
                    with open(output_file, 'a') as f:
                        f.write(result + '\n')
                return full_domain, ip
            elif ip_only:  # Jika opsi --ip-only diaktifkan
                if ip:
                    result = f"{ip}"
                    tqdm.write(f"[+] {result}")
                    if output_file:
                        with open(output_file, 'a') as f:
                            f.write(result + '\n')
                    return ip
                else:
                    return None
            else:  # Jika hanya subdomain yang valid
                result = f"{full_domain}"
                if title:
                    result += f" (Title: {title})"
                tqdm.write(f"[+] {result}")
                if output_file:
                    with open(output_file, 'a') as f:
                        f.write(result + '\n')
                return full_domain, ip

    progress.update(1)  # Update progress bar jika tidak ditemukan hasil valid
    return None

def main():
    parser = argparse.ArgumentParser(
        description="Tools pencari subdomain dengan wordlist eksternal, delay, multithreading, dan verifikasi subdomain."
    )
    parser.add_argument("domain", help="Domain target (contoh: example.com)")
    parser.add_argument("-w", "--wordlist", required=True, help="Path ke file wordlist yang berisi daftar subdomain")
    parser.add_argument("-d", "--delay", type=float, default=0, help="Delay (dalam detik) per scanning pada setiap thread (default: 0 detik)")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Jumlah thread yang digunakan untuk scanning (default: 10)")
    parser.add_argument("--cname", action="store_true", help="Aktifkan pengecekan CNAME pada setiap subdomain (opsional)")
    parser.add_argument("--status-code", "-sc", type=int, nargs='*', default=[], help="Kode status HTTP yang diinginkan (misalnya 200, 204, 301, dll). Default: Semua status diterima")
    parser.add_argument("--ip", action="store_true", help="Tampilkan subdomain dan IP-nya")
    parser.add_argument("--ip-only", action="store_true", help="Tampilkan hanya IP tanpa subdomain")
    parser.add_argument("--output", type=str, help="File untuk menyimpan hasil output yang valid")
    parser.add_argument("--title", action="store_true", help="Tampilkan judul halaman dari subdomain yang valid")

    args = parser.parse_args()

    # Membaca wordlist dari file dan membersihkan baris kosong
    try:
        with open(args.wordlist, "r") as f:
            subdomains = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: File {args.wordlist} tidak ditemukan!")
        return

    # Menulis header jika output file ditentukan
    if args.output:
        with open(args.output, 'w') as f:
            f.write("Hasil subdomain yang valid:\n")

    # Menggunakan ThreadPoolExecutor untuk menjalankan scanning secara paralel
    with ThreadPoolExecutor(max_workers=args.threads) as executor, tqdm(total=len(subdomains), desc="Scanning Progress", position=0, leave=True) as progress:
        futures = []
        for subdomain in subdomains:
            futures.append(executor.submit(scan_subdomain, subdomain, args.domain, args.delay, args.cname, args.status_code, progress, args.ip_only, args.ip, args.output, args.title))
        
        # Menunggu hasil dan menampilkan subdomain yang valid
        for future in as_completed(futures):
            future.result()  # Memastikan semua proses selesai

if __name__ == "__main__":
    main()
