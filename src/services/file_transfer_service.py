import os
import subprocess
import sys
import re


class FileTransferService:
    def __init__(self, pi_user, pi_ip, pi_movies, pi_tv):
        self.pi_user = pi_user
        self.pi_host = pi_ip
        self.pi_movies = pi_movies
        self.pi_tv = pi_tv
        self.env = os.environ.copy()
        # Supported video extensions for folder file progress
        self.video_exts = [".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv"]

    def _print_progress_bar(self, percentage: int, bar_length: int = 30):
        """Draws a dynamic progress bar in the console."""
        filled_len = int(bar_length * percentage // 100)
        bar = "█" * filled_len + "-" * (bar_length - filled_len)
        sys.stdout.write(f"\r📤 [{bar}] {percentage}%")
        sys.stdout.flush()

    def _run_scp(
        self, source_path: str, destination_path: str, recursive: bool = False
    ) -> bool:
        """
        Internal helper to run scp commands with progress logging.
        - recursive: True for folders
        """
        cmd = ["scp", "-v"]
        if recursive:
            cmd.append("-r")
        cmd.append(source_path)
        cmd.append(f"{self.pi_user}@{self.pi_host}:{destination_path}")

        print(f"\n🚀 Starting transfer: {source_path} → {destination_path}")
        print("Command:", " ".join(cmd))

        process = subprocess.Popen(
            cmd,
            env=self.env,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        # Regex to detect percentage output from scp verbose
        progress_pattern = re.compile(r"(\d+)%")

        try:
            for line in process.stderr:
                match = progress_pattern.search(line)
                if match:
                    percent = int(match.group(1))
                    self._print_progress_bar(percent)

            process.wait()
            print()  # move to new line after progress bar

            if process.returncode == 0:
                print(f"✅ Transfer completed: {source_path}")
                return True
            else:
                stderr_output = process.stderr.read()
                print(
                    f"\n❌ SCP failed for {source_path}, exit code {process.returncode}"
                )
                if stderr_output.strip():
                    print("SCP error output:")
                    print(stderr_output.strip())
                return False

        except Exception as e:
            print(f"\n❌ Error during transfer of {source_path}: {e}")
            process.kill()
            return False

    def transfer_file(self, file_path: str, dest_type: str) -> bool:
        """Transfer a single file to the appropriate folder on the Pi."""
        destination = self.pi_movies if dest_type == "movie" else self.pi_tv
        # Optional: skip if file already exists on Pi
        # Could use 'ssh ls' here if you want to implement
        return self._run_scp(file_path, destination, recursive=False)

    def transfer_folder(self, folder_path: str, dest_type: str) -> bool:
        """Transfer a folder recursively to the Pi with per-file progress."""
        destination = self.pi_movies if dest_type == "movie" else self.pi_tv

        # Get all video files in the folder for progress tracking
        video_files = []
        for root, _, files in os.walk(folder_path):
            for f in files:
                if os.path.splitext(f)[1].lower() in self.video_exts:
                    video_files.append(os.path.join(root, f))

        total_files = len(video_files)
        if total_files == 0:
            print(f"⚠️ No video files found in folder: {folder_path}")
            return False

        print(
            f"📁 Folder contains {total_files} video file(s). Transferring each individually for progress..."
        )

        for idx, file in enumerate(video_files, start=1):
            print(f"\n[{idx}/{total_files}] Transferring file: {file}")
            # Use _run_scp for individual file transfer
            if not self.transfer_file(file, dest_type):
                print(f"❌ Failed to transfer file: {file}")
                return False  # Stop on first failure

        print(f"✅ All files in folder '{folder_path}' transferred successfully!")
        return True
