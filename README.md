<p align="center">
  <img src="https://github.com/S-Cyber/phantomstike/blob/main/main/Icon/PhantomStrike-ICO.png" >
</p>

<p align="center">
# Phantom Strike 
</p>
This Python-based subdomain scanner tool allows you to perform DNS resolution and HTTP/HTTPS status code validation on subdomains. It supports multi-threading, external wordlist integration, delay management, and advanced checks like CNAME verification and page title extraction. The tool is designed to help ethical hackers and security researchers discover and analyze subdomains efficiently.

## Features

- **Multi-threading**: Scans subdomains concurrently for faster results.
- **DNS Resolution**: Resolves DNS records to identify valid subdomains.
- **HTTP/HTTPS Validation**: Checks the HTTP/HTTPS status codes of subdomains and filters based on the desired status codes.
- **CNAME Checking**: Optionally checks for CNAME records of subdomains.
- **IP and Title Extraction**: Optionally retrieves the IP address and page title of valid subdomains.
- **Progress Tracking**: Displays scanning progress with a progress bar.
- **Output Options**: Saves valid subdomains and associated information (IP, title) to a file.

## Installation

To install the required dependencies, run the following:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python3 subdomain_scanner.py <domain> -w <wordlist_path> [options]
```

### Arguments:
- `domain`: The target domain to scan (e.g., example.com).
- `-w, --wordlist`: Path to the external wordlist file containing subdomain names.
- `-d, --delay`: Delay (in seconds) between each thread (default: 0).
- `-t, --threads`: Number of threads to use (default: 10).
- `--cname`: Enable CNAME checking for each subdomain (optional).
- `--status-code, -sc`: Specify desired HTTP status codes (e.g., 200, 301).
- `--ip`: Display the subdomain along with its IP address.
- `--ip-only`: Display only the IP addresses of valid subdomains.
- `--output`: Save valid results to an output file.
- `--title`: Display the title of the page for valid subdomains.

## Example

```bash
python3 subdomain_scanner.py example.com -w subdomains.txt --status-code 200 --ip --output results.txt
```

This will scan the subdomains listed in `subdomains.txt` for the domain `example.com`, check for HTTP status code 200, fetch the IP address, and save the valid subdomains along with their IPs to `results.txt`.

## License

This project is licensed under the GPL-3.0 License.

---
