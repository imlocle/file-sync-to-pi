import time
from src.config.settings import Settings
from src.services.file_classifier_service import FileClassifierService
from src.services.file_transfer_service import FileTransferService
from src.services.file_deletion_service import FileDeletionService
from src.repositories.file_monitor_repository import FileMonitorRepository
from src.utils.helper import check_pi_connection


def main():
    settings = Settings()

    # ✅ Check network connection to the Pi before doing anything else
    check_pi_connection(settings.pi_user, settings.pi_ip)

    classifier_service = FileClassifierService()
    transfer_service = FileTransferService(
        settings.pi_user,
        settings.pi_ip,
        settings.pi_movies,
        settings.pi_tv,
    )
    deletion_service = FileDeletionService()
    monitor_repo = FileMonitorRepository(
        settings.watch_dir,
        classifier_service,
        transfer_service,
        deletion_service,
        settings.file_exts,
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
