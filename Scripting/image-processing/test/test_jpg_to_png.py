from pathlib import Path

import pytest
from PIL import Image

from utils.jpg_to_png import jpg_to_png


def _create_jpeg(path: Path) -> None:
    image = Image.new("RGB", (8, 8), color="red")
    image.save(path, format="JPEG")


def test_converts_jpg_and_jpeg_in_source_folder(tmp_path: Path) -> None:
    src = tmp_path / "src"
    src.mkdir()

    _create_jpeg(src / "one.jpg")
    _create_jpeg(src / "two.jpeg")
    _create_jpeg(src / "three.JPG")
    _create_jpeg(src / "four.JPEG")
    (src / "ignore.txt").write_text("not an image", encoding="utf-8")

    converted = jpg_to_png(str(src))

    assert converted == 4
    assert (src / "one.png").exists()
    assert (src / "two.png").exists()
    assert (src / "three.png").exists()
    assert (src / "four.png").exists()
    assert not (src / "ignore.png").exists()


def test_writes_to_destination_folder_and_creates_it(tmp_path: Path) -> None:
    src = tmp_path / "src"
    dst = tmp_path / "nested" / "out"
    src.mkdir()

    _create_jpeg(src / "pikachu.jpg")

    converted = jpg_to_png(str(src), str(dst))

    assert converted == 1
    assert dst.exists()
    assert (dst / "pikachu.png").exists()
    assert not (src / "pikachu.png").exists()


def test_falls_back_to_source_when_destination_not_provided(tmp_path: Path) -> None:
    src = tmp_path / "src"
    src.mkdir()

    _create_jpeg(src / "evee.jpg")

    converted = jpg_to_png(str(src), None)

    assert converted == 1
    assert (src / "evee.png").exists()


def test_trims_valid_source_and_destination_paths(tmp_path: Path) -> None:
    src = tmp_path / "src"
    dst = tmp_path / "out"
    src.mkdir()

    _create_jpeg(src / "charizard.jpg")

    converted = jpg_to_png(f"  {src}  ", f"  {dst}  ")

    assert converted == 1
    assert (dst / "charizard.png").exists()
    assert not (src / "charizard.png").exists()


def test_raises_for_empty_or_invalid_source_path(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        jpg_to_png("   ")

    with pytest.raises(ValueError):
        jpg_to_png(str(tmp_path / "missing"))


def test_raises_when_destination_is_existing_file(tmp_path: Path) -> None:
    src = tmp_path / "src"
    src.mkdir()
    _create_jpeg(src / "one.jpg")

    dest_file = tmp_path / "output.txt"
    dest_file.write_text("not a directory", encoding="utf-8")

    with pytest.raises(FileExistsError):
        jpg_to_png(str(src), str(dest_file))
