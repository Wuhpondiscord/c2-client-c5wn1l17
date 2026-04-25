# hf_space_client/client.py - ETHICAL DEMO CLIENT
import requests, socket, time, json, os, random, string
from datetime import datetime

# Configuration
SERVER = os.getenv("SERVER_URL", "https://wuhp-notac2.hf.space")
DEFAULT_ALLOWED_TARGETS = {"127.0.0.1", "localhost"}
ALLOWED_TARGETS_HF = set(DEFAULT_ALLOWED_TARGETS)

def validate_target_ip(ip):
    if ip.startswith("127."): return True
    return ip in ALLOWED_TARGETS_HF

def log_client_message(msg):
    print(f"[{datetime.now().isoformat()}] HF-Client: {msg}")

def exec_fetch_http_flood(ip, port, sim_headers):
    url = f"http://{ip}:{port}/"
    try:
        t0 = time.time()
        res = requests.get(url, headers=sim_headers, timeout=3)
        return {"status": f"status_{res.status_code}", "latency_ms": round((time.time()-t0)*1000, 2), "bytes": len(res.content), "protocol": "http"}
    except Exception as e:
        return {"status": "error", "detail": str(e), "protocol": "http"}

def exec_fetch_cache_bypass(ip, port, sim_headers):
    key = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
    url = f"http://{ip}:{port}/?_cache_bust={key}&_={int(time.time()*1000)}"
    try:
        t0 = time.time()
        res = requests.get(url, headers=sim_headers, timeout=3)
        return {"status": "success", "latency_ms": round((time.time()-t0)*1000, 2), "bytes": len(res.content), "cache_key": key, "protocol": "http"}
    except Exception as e:
        return {"status": "error", "detail": str(e), "protocol": "http"}

def exec_fetch_custom_headers(ip, port, sim_headers):
    url = f"http://{ip}:{port}/"
    custom_headers = { **sim_headers, "X-Custom-Test": "sim_payload", "Accept": "application/json" }
    try:
        t0 = time.time()
        res = requests.get(url, headers=custom_headers, timeout=3)
        return {"status": f"status_{res.status_code}", "latency_ms": round((time.time()-t0)*1000, 2), "bytes": len(res.content), "protocol": "http"}
    except Exception as e:
        return {"status": "error", "detail": str(e), "protocol": "http"}

def exec_socket_tcp_probe(ip, port):
    try:
        t0 = time.time()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect((ip, port))
            s.sendall(b"SIM_PKT_TCP_01_HEARTBEAT")
        return {"status": "tcp_connected", "latency_ms": round((time.time()-t0)*1000, 2), "bytes_sent": 24, "protocol": "tcp"}
    except Exception as e:
        return {"status": "tcp_failed", "detail": str(e), "protocol": "tcp"}

def exec_socket_udp_probe(ip, port):
    try:
        t0 = time.time()
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(2)
            sent = s.sendto(b"SIM_PKT_UDP_01_HEARTBEAT", (ip, port))
        return {"status": "udp_sent", "latency_ms": round((time.time()-t0)*1000, 2), "bytes_sent": sent, "protocol": "udp"}
    except Exception as e:
        return {"status": "udp_failed", "detail": str(e), "protocol": "udp"}

EXECUTORS = {
    "fetch_http_flood": exec_fetch_http_flood,
    "fetch_cache_bypass": exec_fetch_cache_bypass,
    "fetch_custom_headers": exec_fetch_custom_headers,
    "socket_tcp_probe": exec_socket_tcp_probe,
    "socket_udp_probe": exec_socket_udp_probe
}

def run():
    log_client_message("="*50)
    log_client_message("HUGGING FACE SPACE CLIENT (ETHICAL DEMO)")
    log_client_message("="*50)
    log_client_message(f"Polling Control Server: {SERVER}")
    log_client_message("Educational simulation only - no malicious activity")
    log_client_message("="*50)

    while True:
        try:
            cmd_response = requests.get(f"{SERVER}/api/poll_command", timeout=5).json()
            if cmd_response.get("status") == "idle":
                time.sleep(2); continue

            cmd = cmd_response
            cmd_type, ip, port = cmd["type"], cmd["ip"], int(cmd["port"])
            sim_headers = cmd.get("simulation_headers", {"X-Simulation": "true", "User-Agent": "EduSimClient/1.0"})

            log_client_message(f"Command (ID={cmd['id']}): {cmd_type} -> {ip}:{port}")

            if not validate_target_ip(ip):
                report = {"client": "hf_space", "command_id": cmd["id"], "status": "blocked_by_client_allowlist", "target": f"{ip}:{port}", "timestamp": time.time()}
            elif cmd_type in EXECUTORS:
                if cmd_type.startswith("fetch_"):
                    res = EXECUTORS[cmd_type](ip, port, sim_headers)
                else:
                    res = EXECUTORS[cmd_type](ip, port)
                report = {"client": "hf_space", "command_id": cmd["id"], "type": cmd_type, "target": f"{ip}:{port}", "requests_sent": 1, "result": res, "timestamp": time.time()}
            else:
                report = {"client": "hf_space", "command_id": cmd["id"], "status": "unsupported_command_type", "type": cmd_type, "target": f"{ip}:{port}", "timestamp": time.time()}

            requests.post(f"{SERVER}/api/report", json=report, timeout=5)
        except Exception as e:
            log_client_message(f"Error: {e}")
        time.sleep(2)

if __name__ == "__main__":
    run()
