# src/services/file_transfer_service.py
import os
import subprocess
import sys
import re


class FileTransferService:
    def __init__(self, pi_user, pi_ip, pi_movies, pi_tv):
        self.pi_user = pi_user
        self.pi_host = pi_ip  # can be IP or hostname (e.g. raspberrypi.local)
        self.pi_movies = pi_movies
        self.pi_tv = pi_tv
        self.env = os.environ.copy()

    def _print_progress_bar(self, percentage: int, bar_length: int = 30):
        """Draws a dynamic progress bar in the console."""
        filled_len = int(bar_length * percentage // 100)
        bar = "█" * filled_len + "-" * (bar_length - filled_len)
        sys.stdout.write(f"\r📤 [{bar}] {percentage}%")
        sys.stdout.flush()

    def _run_scp(
        self, source_path: str, destination_path: str, recursive: bool = False
    ) -> bool:
        """Internal helper to run scp commands with progress logging."""
        cmd = ["scp", "-v"]  # verbose mode to get progress output
        if recursive:
            cmd.append("-r")
        cmd.append(source_path)
        cmd.append(f"{self.pi_user}@{self.pi_host}:{destination_path}")

        print(f"\n🚀 Starting transfer: {source_path} → {destination_path}")
        print("Command:", " ".join(cmd))

        # Start SCP process
        process = subprocess.Popen(
            cmd,
            env=self.env,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        progress_pattern = re.compile(
            r"(\d+)%"
        )  # SCP progress lines contain percentages

        try:
            for line in process.stderr:
                # Look for progress percentage in stderr
                match = progress_pattern.search(line)
                if match:
                    percent = int(match.group(1))
                    self._print_progress_bar(percent)

                # Optional: print verbose messages for debugging (comment out if noisy)
                # else:
                #     print(line.strip())

            process.wait()
            print()  # move to new line after progress bar

            if process.returncode == 0:
                print(f"✅ Transfer completed: {source_path}")
                return True
            else:
                # Read any remaining stderr output
                stderr_output = process.stderr.read()
                print(
                    f"\n❌ SCP failed for {source_path}, exit code {process.returncode}"
                )
                if stderr_output.strip():
                    print("SCP error output:")
                    print(stderr_output.strip())
                else:
                    print("No additional error output from SCP.")
                return False

        except Exception as e:
            print(f"\n❌ Error during transfer of {source_path}: {e}")
            process.kill()
            return False

    def transfer_file(self, file_path: str, dest_type: str) -> bool:
        """Transfer a single file to the appropriate folder on the Pi."""
        destination = self.pi_movies if dest_type == "movie" else self.pi_tv
        return self._run_scp(file_path, destination, recursive=False)

    def transfer_folder(self, folder_path: str, dest_type: str) -> bool:
        """Transfer a folder recursively to the appropriate folder on the Pi."""
        destination = self.pi_movies if dest_type == "movie" else self.pi_tv
        return self._run_scp(folder_path, destination, recursive=True)
