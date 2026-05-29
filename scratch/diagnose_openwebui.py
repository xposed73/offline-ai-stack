import sys
import socket
import docker
from docker.errors import NotFound

def check_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def diagnose():
    print("=== OpenWebUI Docker Diagnostics ===")
    
    # 1. Connect to Docker
    try:
        client = docker.from_env()
        print("[OK] Successfully connected to Docker daemon.")
    except Exception as e:
        print(f"[ERROR] Failed to connect to Docker daemon: {e}")
        return

    # 2. Inspect open-webui container
    try:
        container = client.containers.get("open-webui")
        status = container.status
        state = container.attrs.get("State", {})
        print(f"\nContainer Name: open-webui")
        print(f"Status: {status.upper()}")
        print(f"Running: {state.get('Running')}")
        print(f"Error (if any): {state.get('Error')}")
        print(f"Exit Code: {state.get('ExitCode')}")
        
        # Ports
        ports = container.attrs.get("HostConfig", {}).get("PortBindings", {})
        print("\nPort Bindings:")
        for container_port, host_bindings in ports.items():
            for binding in host_bindings:
                print(f"  Container {container_port} -> Host {binding.get('HostIp')}:{binding.get('HostPort')}")
                
        # Logs
        print("\nLast 20 lines of Container Logs:")
        print("----------------------------------------")
        logs = container.logs(tail=20).decode('utf-8', errors='replace')
        print(logs if logs.strip() else "(No logs)")
        print("----------------------------------------")
        
    except NotFound:
        print("\n[ERROR] Container 'open-webui' not found in Docker.")
    except Exception as e:
        print(f"\n[ERROR] Failed to inspect container: {e}")

    # 3. Check Host Port 3000
    print("\n=== Host Port 3000 Check ===")
    port_3000_in_use = check_port_in_use(3000)
    print(f"Is host port 3000 responsive? {port_3000_in_use}")
    if port_3000_in_use:
        print("Note: Something on localhost is responding on port 3000.")
    else:
        print("Note: Nothing is responding on localhost port 3000.")

if __name__ == "__main__":
    diagnose()
