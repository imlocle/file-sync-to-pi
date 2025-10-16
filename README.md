# 🌀 PiSync: Automated Media Transfer and File Cleanup System

**PiSync** is a Python-based automation tool that monitors local directory (`~/Transfers`) on your MacBook and automatically transfers media files (movies and TV shows) to a Raspberry Pi 4 running Kodi 20.5 (Nexus). Movies are copied to `/mnt/external/Movies` and TV shows to `/mnt/external/TV_show` on the Pi using SCP over SSH.

Once the transfer is complete, PiSync safely moves the original files into the **Trash** — keeping your system organized while ensuring your Raspberry Pi stays up to date with new media content.

## Prerequisites

- **Hardware**:
  - MacBook
  - Raspberry Pi 4 with Raspberry Pi OS (64-bit, Desktop).
  - External drive on Pi mounted at `/mnt/external` with `Movies` and `TV_show` directories.
- **Software**:
  - Python 3.13.
  - SSH server (`sshd`) running on Pi with port 22 open.
  - Passwordless SSH setup (key-based authentication).
  - Kodi 20.5 (Nexus) installed on Pi.
- **Python Dependencies**:
  - `pydantic-settings`
  - `watchdog`
  - `python-dotenv`
  - `send2trash`
- **Network**: Both devices on the same Wi-Fi network.

## Setup

1. **Clone the Repository**:

   ```bash
   git clone <repository-url>
   cd ~/file_sync_to_pi
   ```

   _(Replace `<repository-url>` with your repo URL or copy files manually.)_

2. **Set Up Python Virtual Environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Passwordless SSH**:

   - Generate SSH key on MacBook (if not already done):
     ```bash
     ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa
     ```
   - Copy key to Pi:
     ```bash
     ssh-copy-id pi@<RPI_IP>
     ```
   - Test SSH:
     ```bash
     ssh pi@<RPI_IP>
     ```

4. **Allow SCP in macOS Firewall**:

   ```bash
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/bin/scp
   ```

5. **Create .env File**:

   - Create `~/file_sync_to_pi/.env`:
     ```bash
     nano ~/file_sync_to_pi/.env
     ```
   - Add:
     ```plaintext
     PI_USER=<RPI_USERNAME>
     PI_IP=<RPI_IP>
     PI_MOVIES=<PATH_TO_RPI_MOVIES_DIR> # Ex: /mnt/external/Movies/
     PI_TV=<PATH_TO_RPI_TV_SHOWS_DIR> # Ex: /mnt/external/TV_shows/
     ```

6. **Ensure Pi Directory Permissions**:

   - On Pi, verify write access:
     ```bash
     ssh pi@<RPI_IP>
     ls -ld /mnt/external/Movies /mnt/external/TV_show
     ```
     - Fix if needed:
       ```bash
       sudo chown pi:pi /mnt/external/Movies /mnt/external/TV_show
       sudo chmod 755 /mnt/external/Movies /mnt/external/TV_show
       ```

7. **Verify Kodi Setup**:
   - Ensure `/mnt/external/Movies` and `/mnt/external/TV_show` are added as media sources in Kodi.
   - Update library after transfers:
     ```bash
     ssh pi@<RPI_IP> "kodi-send --action='UpdateLibrary(video)'"
     ```

## Usage

### **DO NOT OPEN COMMAND LINE FROM IDE FOR USAGE**

- Open command line (Terminal) separately from your IDE so it can inherit your computer settings (SSH).

1. **Start the Program**:

   - Wait 1 minute after Pi reboot to ensure SSH is ready.
   - Run:
     ```bash
     cd ~/file_sync_to_pi
     source venv/bin/activate
     python main.py
     ```
   - The script monitors `~/Transfers` for new files.

2. **Transfer Files**:

   - Place media files in `~/Transfers/Movies` or `~/Transfers/TV_shows`:
     ```bash
     cp ~/Downloads/<YOUR_MEDIA_FILE> ~/Transfers/Movies/
     ```
   - The script detects files, classifies them (movie or TV show), and transfers them to the Pi.
   - Successfully transferred files are deleted from `~/Transfers`.

3. **Stop the Program**:
   - Press `Ctrl+C` to stop monitoring.

## 🚀 Features

- **Automatic Folder Monitoring**

  - Watches designated directories for new Movies and TV Shows.
  - Detects both single files and folders.

- **Smart SCP Transfer**

  - Transfers files and folders directly to your Raspberry Pi using `scp`.
  - Preserves folder structure (e.g. `/TV_shows/<series_name>/episode.mkv`).
  - Includes detailed console logging and optional progress indicators.

- **Safe Cleanup**

  - Automatically moves transferred files/folders to the system Trash using [`send2trash`](https://pypi.org/project/Send2Trash/), avoiding accidental deletions.

- **Robust Error Handling**

  - Skips files already existing on the Raspberry Pi.
  - Retries and logs failed transfers with exit codes.

- **Customizable Paths**
  - Define your local watch folders and remote destinations easily in configuration.

## Troubleshooting

- **Exit Code 255 Error**:

  - Indicates SSH connection or authentication failure.
  - Verify `SSH_AUTH_SOCK`:
    ```bash
    echo $SSH_AUTH_SOCK
    ```
    - If empty, start SSH agent:
      ```bash
      eval $(ssh-agent)
      ssh-add ~/.ssh/id_rsa
      ```
  - Test SCP manually:
    ```bash
    scp ~/Downloads/<YOUR_MEDIA_FILE> pi@<RPI_IP>:/mnt/external/Movies/
    ```

- **Permissions Issues**:

  - Check Pi directory permissions:
    ```bash
    ssh pi@<RPI_IP> "ls -ld /mnt/external/Movies"
    ```
    - Fix:
      ```bash
      ssh pi@<RPI_IP> "sudo chown pi:pi /mnt/external/Movies"
      ```

- **Network Issues**:

  - Ensure both devices are on the same network:
    ```bash
    ping <RPI_IP>
    ```
  - If packet loss, move Pi closer to router or use Ethernet.

- **Kodi Not Showing Files**:
  - Update library:
    ```bash
    ssh pi@<RPI_IP> "kodi-send --action='UpdateLibrary(video)'"
    ```
