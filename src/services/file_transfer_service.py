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
        # Supported video file extensions
        self.video_exts = [".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv" ".srt"]

    def _print_progress_bar(self, percentage: int, bar_length: int = 30):
        """Draw a dynamic SCP progress bar in the console."""
        filled_len = int(bar_length * percentage // 100)
        bar = "█" * filled_len + "-" * (bar_length - filled_len)
        sys.stdout.write(f"\r📤 [{bar}] {percentage}%")
        sys.stdout.flush()

    def _run_scp(
        self, source_path: str, destination_path: str, recursive: bool = False
    ) -> bool:
        """Run SCP command with verbose output and progress tracking."""
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

        # Regex to detect percentage output from SCP verbose
        progress_pattern = re.compile(r"(\d+)%")

        try:
            for line in process.stderr:
                match = progress_pattern.search(line)
                if match:
                    percent = int(match.group(1))
                    self._print_progress_bar(percent)

            process.wait()
            print()

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

    def _file_exists_on_pi(self, remote_path: str) -> bool:
        """Check if a file already exists on the Pi using SSH."""
        cmd = ["ssh", f"{self.pi_user}@{self.pi_host}", f'ls "{remote_path}"']
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0

    def transfer_file(self, file_path: str, dest_type: str) -> bool:
        """
        Transfer a single file to the Pi.
        - TV shows: preserve subfolder relative to watch_dir
        - Movies: direct under the Movies folder
        """
        # Base destination on Pi
        destination_base = self.pi_movies if dest_type == "movie" else self.pi_tv

        # Determine watch root depending on type
        watch_root = os.path.join(
            os.path.expanduser("~/Transfers"),
            "TV_shows" if dest_type == "tv" else "Movies",
        )

        # Relative path for remote destination
        if dest_type == "tv":
            rel_path = os.path.relpath(file_path, watch_root)
        else:
            # For movies, just include the parent folder
            rel_path = os.path.join(
                os.path.basename(os.path.dirname(file_path)),
                os.path.basename(file_path),
            )

        remote_path = os.path.join(destination_base, rel_path)
        remote_folder = os.path.dirname(remote_path)

        # Skip if already exists on Pi
        if self._file_exists_on_pi(remote_path):
            print(f"⏭️ Skipping existing file on Pi: {file_path}")
            return True

        # Ensure remote folder exists
        mkdir_cmd = (
            f'ssh {self.pi_user}@{self.pi_host} "mkdir -p \\"{remote_folder}\\""'
        )
        subprocess.run(mkdir_cmd, shell=True, check=True)

        return self._run_scp(file_path, remote_folder, recursive=False)

    def transfer_folder(self, folder_path: str, dest_type: str) -> bool:
        """
        Transfer a folder recursively to the Pi.
        - TV shows preserve their subfolder structure relative to watch_dir
        - Movies transfer as a whole under the base folder
        - Skips files that already exist on Pi
        """
        # Base destination on Pi
        destination_base = self.pi_movies if dest_type == "movie" else self.pi_tv

        # Determine root folder for relative paths
        watch_root = os.path.join(
            os.path.expanduser("~/Transfers"),
            "TV_shows" if dest_type == "tv" else "Movies",
        )

        # Gather video files
        video_files = []
        for root, _, files in os.walk(folder_path):
            for f in files:
                if os.path.splitext(f)[1].lower() in self.video_exts:
                    video_files.append(os.path.join(root, f))

        total_files = len(video_files)
        if total_files == 0:
            print(f"⚠️ No video files found in folder: {folder_path}")
            return False

        print(f"📁 Folder contains {total_files} video file(s). Transferring...")

        for idx, file in enumerate(video_files, start=1):
            # Relative path for TV shows; Movies can be direct
            if dest_type == "tv":
                rel_path = os.path.relpath(file, watch_root)
            else:
                # For movies, just use folder name + file
                rel_path = os.path.relpath(file, os.path.dirname(folder_path))

            remote_path = os.path.join(destination_base, rel_path)
            remote_folder = os.path.dirname(remote_path)

            print(f"\n[{idx}/{total_files}] Transferring file: {file} → {remote_path}")

            # Skip if already exists
            if self._file_exists_on_pi(remote_path):
                print(f"⏭️ Skipping existing file on Pi: {file}")
                continue

            # Ensure remote folder exists
            mkdir_cmd = (
                f'ssh {self.pi_user}@{self.pi_host} "mkdir -p \\"{remote_folder}\\""'
            )
            subprocess.run(mkdir_cmd, shell=True, check=True)

            # Transfer the file
            if not self._run_scp(file, remote_folder, recursive=False):
                print(f"❌ Failed to transfer file: {file}")
                return False

        print(f"✅ All files in folder '{folder_path}' transferred successfully!")
        return True
