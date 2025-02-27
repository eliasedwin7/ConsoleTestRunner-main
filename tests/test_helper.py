import pytest
import json
import zipfile
import tarfile
import io
from pathlib import Path
from console_test_runner.utils.helper import ConsoleTestUtils
import shutil


def test_extract_package_zip(tmp_path):
    # Setup
    zip_file = tmp_path / "test.zip"
    extract_to = tmp_path / "extracted"
    extract_to.mkdir()

    # Create a zip file for testing
    with zipfile.ZipFile(zip_file, "w") as zip_ref:
        zip_ref.writestr("test.txt", "This is a test file")

    # Test
    ConsoleTestUtils.extract_package(zip_file, extract_to)
    assert (extract_to / "test.txt").exists()


def test_extract_package_tar(tmp_path):
    # Setup
    tar_file = tmp_path / "test.tar"
    extract_to = tmp_path / "extracted"
    extract_to.mkdir()

    # Create a tar file for testing
    with tarfile.open(tar_file, "w") as tar_ref:
        tar_ref.addfile(tarfile.TarInfo("test.txt"), io.BytesIO(b"This is a test file"))

    # Test
    ConsoleTestUtils.extract_package(tar_file, extract_to)
    assert (extract_to / "test.txt").exists()


def test_find_executable(tmp_path):
    # Setup
    main_folder = tmp_path / "main"
    main_folder.mkdir()
    executable = main_folder / "test_executable"
    executable.touch()

    # Test
    result = ConsoleTestUtils.find_executable(main_folder, "test_executable")
    assert result == executable


def test_ensure_directory_exists(tmp_path):
    # Setup
    directory = tmp_path / "new_directory"

    # Test
    ConsoleTestUtils.ensure_directory_exists(directory)
    assert directory.exists()


def test_run_conversion():
    # Test a simple echo command
    result = ConsoleTestUtils.run_conversion("cmd", "/c", "echo Hello, World!")
    assert "Hello, World!" in result


def test_get_executable(tmp_path):
    # Setup
    main_folder = tmp_path / "main"
    main_folder.mkdir()
    executable = main_folder / "test_executable"
    executable.touch()
    extract_to = tmp_path / "extracted"
    extract_to.mkdir()

    # Test
    result = ConsoleTestUtils.get_executable(main_folder, extract_to, "test_executable")
    assert result == executable


def test_delete_generated_packages(tmp_path):
    # Setup
    dir1 = tmp_path / "dir1"
    dir2 = tmp_path / "dir2"
    dir1.mkdir()
    dir2.mkdir()

    # Test
    ConsoleTestUtils.delete_generated_packages(True, [dir1, dir2])
    assert not dir1.exists()
    assert not dir2.exists()


def test_read_runspec_file(tmp_path):
    # Setup
    runspec_file = tmp_path / "runspec.json"
    runspec_content = [{"name": "test_case"}]
    runspec_file.write_text(json.dumps(runspec_content))

    # Test
    result = ConsoleTestUtils.read_runspec_file(runspec_file)
    assert result == runspec_content


def test_check_file_exists(tmp_path):
    # Setup
    file_path = tmp_path / "test_file"
    file_path.touch()

    # Test
    ConsoleTestUtils.check_file_exists(file_path)
    assert file_path.exists()

    # Test file not found
    with pytest.raises(FileNotFoundError):
        ConsoleTestUtils.check_file_exists(tmp_path / "non_existent_file")
