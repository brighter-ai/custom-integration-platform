import tarfile
from pathlib import Path
from typing import List, Optional


class TarExecutor:
    def __init__(self, image_extenstion: Optional[str] = "png") -> None:
        self._image_extenstion = image_extenstion

    def archive_files(
        self, images_paths: List[Path], out_directory_path: Path, num_files: Optional[int] = 100
    ) -> None:
        segment_lists = [images_paths[x : x + num_files] for x in range(0, len(images_paths), num_files)]  # noqa E203
        for idx, segment in enumerate(segment_lists, start=1):
            segment_tar_file_path = out_directory_path / f"{idx:08d}.tar"
            with tarfile.open(segment_tar_file_path, "w") as archive:
                for filename in segment:
                    archive.add(name=filename, arcname=filename.name)

    def extract_files(self, archives_paths: List[Path], out_directory_path: Path) -> None:
        for archives_path in archives_paths:
            with tarfile.open(archives_path, "r") as archive:
                archive.extractall(path=out_directory_path)
