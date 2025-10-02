import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from src.services.file_classifier_service import FileClassifierService
from src.services.file_deletion_service import FileDeletionService
from src.services.file_transfer_service import FileTransferService
from src.utils.constants import MOVIES_DIR, TV_SHOWS_DIR


class FileMonitorRepository(FileSystemEventHandler):
    def __init__(
        self,
        watch_dir,
        classifier: FileClassifierService,
        transfer_service: FileTransferService,
        deletion_service: FileDeletionService,
        movie_exts,
        skip_files: set,
    ):
        self.watch_dir = watch_dir
        self.classifier = classifier
        self.transfer_service = transfer_service
        self.deletion_service = deletion_service
        self.movie_exts = movie_exts
        self.skip_files = skip_files
        self.observer = Observer()

    def create_directories(self):
        """Ensure watch directory and subfolders exist."""
        movies_dir = os.path.join(self.watch_dir, MOVIES_DIR)
        tv_dir = os.path.join(self.watch_dir, TV_SHOWS_DIR)
        for directory in [self.watch_dir, movies_dir, tv_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Created directory: {directory}")

    def start_monitoring(self):
        """Start monitoring the watch directory."""
        self.observer.schedule(self, self.watch_dir, recursive=True)
        self.observer.start()

    def stop_monitoring(self):
        """Stop monitoring the watch directory."""
        self.observer.stop()
        self.observer.join()

    def on_created(self, event):
        """Handle file/folder creation events."""
        if event.is_directory:
            self.handle_folder(event.src_path)
        else:
            self.handle_file(event.src_path)

    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory:
            self.handle_file(event.src_path)

    def handle_file(self, file_path):
        """Process a file event."""
        if os.path.basename(file_path) in self.skip_files:
            print(f"Skipping file: {file_path}")
            return

        if MOVIES_DIR in file_path.split(os.sep) or TV_SHOWS_DIR in file_path.split(
            os.sep
        ):
            dest_type = "movie" if MOVIES_DIR in file_path.split(os.sep) else "tv"
        else:
            dest_type = self.classifier.classify_file(file_path, self.movie_exts)
        if self.transfer_service.transfer_file(file_path, dest_type):
            self.deletion_service.delete_file(file_path)
        else:
            return

    def handle_folder(self, folder_path):
        """Process a folder event."""
        folder_name = os.path.basename(folder_path)
        if folder_name in [MOVIES_DIR, TV_SHOWS_DIR]:
            return
        dest_type = self.classifier.classify_folder(folder_path)
        if self.transfer_service.transfer_folder(folder_path, dest_type):
            self.deletion_service.delete_folder(folder_path)
        else:
            return
