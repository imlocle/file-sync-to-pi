import os


class FileClassifierService:
    def classify_file(self, file_path, movie_exts):
        """Determine if file is a movie or TV show based on extension or name."""
        _, ext = os.path.splitext(file_path.lower())
        filename = os.path.basename(file_path).lower()
        if ext in movie_exts:
            return "movie"
        if (
            "s0" in filename
            or "e0" in filename
            or "episode" in filename
            or ".tvshow" in ext
        ):
            return "tv"
        return "movie"

    def classify_folder(self, folder_path):
        """Determine if folder is for movies or TV shows based on name."""
        folder_name = os.path.basename(folder_path).lower()
        if "season" in folder_name or "episode" in folder_name:
            return "tv"
        return "movie"
