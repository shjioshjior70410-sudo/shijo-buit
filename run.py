"""
BuildPulse - Server Startup Script with Android & Network Access.
Starts FastAPI uvicorn server on 0.0.0.0:8000 accessible from localhost and Android devices on the local Wi-Fi.
"""
import sys
import socket

# Ensure UTF-8 output if possible
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def get_local_ip():
    """Detects the primary local network IP address of this machine."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        # Connect to an external address to get routing interface
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"


import uvicorn

if __name__ == "__main__":
    local_ip = get_local_ip()
    port = 8000

    print("=" * 68)
    print(" [BuildPulse] - Intelligent Construction Project Management")
    print("=" * 68)
    print(" Local Desktop URL:   http://localhost:8000/")
    print(" Local Desktop Login: http://localhost:8000/login")
    print(" API Documentation:   http://localhost:8000/docs")
    print("-" * 68)
    print(" [ANDROID ACCESS INSTRUCTIONS]")
    print(" 1. Make sure your Android device is on the same Wi-Fi network.")
    print(f" 2. Open Google Chrome on your Android phone and visit:")
    print(f"    --> http://{local_ip}:{port}/")
    print("=" * 68)

    # Listen on 0.0.0.0 so external devices on the LAN can connect
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
