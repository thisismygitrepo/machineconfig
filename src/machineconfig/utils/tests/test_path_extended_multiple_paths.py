from machineconfig.utils.path_extended import PathExtended
from pathlib import Path

def test_path_extended_multiple_paths():
    # Setup a dummy directory and file
    dummy_dir = Path('dummy_dir')
    dummy_dir.mkdir(exist_ok=True)
    dummy_file = dummy_dir / 'dummy_file.txt'
    dummy_file.touch()

    # Test case 1: Initialize with a single path string
    p1 = PathExtended('dummy_dir')
    assert p1.is_dir()

    # Test case 2: Initialize with a single Path object
    p2 = PathExtended(dummy_dir)
    assert p2.is_dir()

    # Test case 3: Initialize with a list of path strings
    p3 = PathExtended(['dummy_dir', str(dummy_file)])
    # This should not raise an error, and p3 should probably represent the first valid path,
    # or handle multiple paths gracefully.
    # Current behavior: raises an AttributeError.
    # Desired behavior: p3 represents 'dummy_dir' or handles multiple paths.
    assert p3.is_dir()

    # Test case 4: Initialize with a list of Path objects
    p4 = PathExtended([dummy_dir, dummy_file])
    assert p4.is_dir()

    # Cleanup
    dummy_file.unlink()
    dummy_dir.rmdir()
