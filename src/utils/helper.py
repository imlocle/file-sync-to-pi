import subprocess


def check_pi_connection(pi_user: str, pi_host: str):
    """Quick connectivity test before starting the service."""
    print(f"🔍 Checking connection to {pi_host}...")
    try:
        subprocess.run(
            ["ssh", f"{pi_user}@{pi_host}", "echo", "connected"],
            check=True,
            capture_output=True,
            text=True,
        )
        print(f"✅ Successfully connected to {pi_host}\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ Cannot connect to {pi_host}. Error:")
        print(e.stderr.strip())
        print("\nPlease check:")
        print("- Is the Raspberry Pi online?")
        print("- Is SSH enabled on the Pi?")
        print("- Is the IP/hostname correct?")
        print("- Are both devices on the same Wi-Fi?")
        exit(1)
