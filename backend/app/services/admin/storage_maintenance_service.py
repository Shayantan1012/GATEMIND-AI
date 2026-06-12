from pathlib import Path
from shutil import rmtree


class StorageMaintenanceService:
    PRESERVED_UPLOAD_DIRECTORIES = {"profile-images"}
    LOG_SUFFIXES = {".log", ".err"}

    def __init__(self, upload_folder):
        self.upload_folder = Path(upload_folder).resolve()

    def clear_logs_and_uploaded_documents(self):
        files_deleted = 0
        logs_deleted = 0
        bytes_freed = 0

        self._validate_cleanup_root(self.upload_folder)
        self.upload_folder.mkdir(parents=True, exist_ok=True)

        for item in self.upload_folder.iterdir():
            if item.is_dir() and item.name.lower() in self.PRESERVED_UPLOAD_DIRECTORIES:
                continue
            item_files, item_bytes = self._measure(item)
            logs_deleted += self._count_logs(item)
            if item.is_dir() and item.name.lower() == "logs":
                self._clear_active_logs(item)
            else:
                self._remove(item)
            files_deleted += item_files
            bytes_freed += item_bytes

        return {
            "files_deleted": files_deleted,
            "logs_deleted": logs_deleted,
            "bytes_freed": bytes_freed,
            "mongodb_records_deleted": 0,
            "rag_data_preserved": True,
            "profile_images_preserved": True,
        }

    @staticmethod
    def _validate_cleanup_root(target):
        if target == Path(target.anchor) or len(target.parts) < 2:
            raise ValueError("Unsafe maintenance path")

    @staticmethod
    def _remove(target):
        if target.is_dir():
            rmtree(target)
        else:
            target.unlink()

    @staticmethod
    def _measure(target):
        if target.is_file():
            return 1, target.stat().st_size

        files = [item for item in target.rglob("*") if item.is_file()]
        return len(files), sum(item.stat().st_size for item in files)

    @classmethod
    def _count_logs(cls, target):
        if target.is_file():
            return int(target.suffix.lower() in cls.LOG_SUFFIXES)
        return sum(
            item.suffix.lower() in cls.LOG_SUFFIXES
            for item in target.rglob("*")
            if item.is_file()
        )

    @classmethod
    def _clear_active_logs(cls, log_folder):
        for item in log_folder.rglob("*"):
            if not item.is_file():
                continue
            if item.suffix.lower() in cls.LOG_SUFFIXES:
                item.write_text("", encoding="utf-8")
            else:
                item.unlink()
