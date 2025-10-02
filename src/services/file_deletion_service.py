import os
from send2trash import send2trash


class FileDeletionService:
    def delete_file(self, file_path: str):
        """Move a file to the Trash instead of permanently deleting."""
        try:
            if os.path.isfile(file_path):
                send2trash(file_path)
                print(f"🗑️ Moved file to Trash: {file_path}")
                return True
            else:
                print(f"⚠️ File not found: {file_path}")
                return False
        except Exception as e:
            print(f"❌ Error moving file to Trash {file_path}: {e}")
            return False

    def delete_folder(self, folder_path: str):
        """Move a folder to the Trash instead of permanently deleting."""
        try:
            if os.path.isdir(folder_path):
                send2trash(folder_path)
                print(f"🗑️ Moved folder to Trash: {folder_path}")
                return True
            else:
                print(f"⚠️ Folder not found: {folder_path}")
                return False
        except Exception as e:
            print(f"❌ Error moving folder to Trash {folder_path}: {e}")
            return False
