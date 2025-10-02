import time
import subprocess
from src.config.settings import Settings
from src.services.file_classifier_service import FileClassifierService
from src.services.file_transfer_service import FileTransferService
from src.services.file_deletion_service import FileDeletionService
from src.repositories.file_monitor_repository import FileMonitorRepository


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


def main():
    settings = Settings()

    # ✅ Check network connection to the Pi before doing anything else
    check_pi_connection(settings.pi_user, settings.pi_ip)

    classifier = FileClassifierService()
    transfer_service = FileTransferService(
        settings.pi_user,
        settings.pi_ip,
        settings.pi_movies,
        settings.pi_tv,
    )
    deletion_service = FileDeletionService()
    monitor_repo = FileMonitorRepository(
        settings.watch_dir,
        classifier,
        transfer_service,
        deletion_service,
        settings.movie_exts,
        settings.skip_files,
    )

    monitor_repo.create_directories()
    print(f"📂 Monitoring directory: {settings.watch_dir}")
    monitor_repo.start_monitoring()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor_repo.stop_monitoring()
        print("\n🛑 Stopped monitoring")


if __name__ == "__main__":
    main()
