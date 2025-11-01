"""Gource visualization tool for git repositories."""

from pathlib import Path
from typing import Annotated, Optional
import subprocess
import platform
import zipfile
import typer


def get_gource_install_dir() -> Path:
    """Get the installation directory for portable Gource."""
    if platform.system() == "Windows":
        appdata = Path.home() / "AppData" / "Local"
        return appdata / "gource"
    else:
        return Path.home() / ".local" / "bin" / "gource"


def get_gource_executable() -> Path:
    """Get the path to the gource executable (inside the extracted directory with DLLs)."""
    install_dir = get_gource_install_dir()
    if platform.system() == "Windows":
        possible_paths = [
            install_dir / "gource.exe",
            install_dir / f"gource-{get_default_version()}.win64" / "gource.exe",
        ]
        for path in possible_paths:
            if path.exists():
                return path
        return install_dir / f"gource-{get_default_version()}.win64" / "gource.exe"
    else:
        return install_dir / "gource"


def get_default_version() -> str:
    """Get the default gource version."""
    return "0.53"


def install_gource_windows(version: Optional[str] = None) -> None:
    """Install portable Gource on Windows by downloading and extracting the zip archive."""
    if platform.system() != "Windows":
        raise OSError(f"This installer is for Windows only. Current OS: {platform.system()}")

    from machineconfig.utils.path_extended import PathExtended
    from machineconfig.utils.source_of_truth import INSTALL_TMP_DIR

    print("\n" + "=" * 80)
    print("🚀 GOURCE PORTABLE INSTALLATION 🚀")
    print("=" * 80 + "\n")

    version_str = version or get_default_version()
    portable_url = f"https://github.com/acaudwell/Gource/releases/download/gource-{version_str}/gource-{version_str}.win64.zip"
    install_dir = get_gource_install_dir()

    print(f"📥 Downloading portable Gource from: {portable_url}")
    downloaded_zip = PathExtended(portable_url).download(folder=INSTALL_TMP_DIR)
    print(f"✅ Downloaded to: {downloaded_zip}")

    print(f"\n� Extracting to: {install_dir}")
    install_dir.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(downloaded_zip, 'r') as zip_ref:
            zip_ref.extractall(install_dir)
        print(f"✅ Extracted successfully to: {install_dir}")
        print(f"   (The zip contains gource-{version_str}.win64/ directory with exe and DLL dependencies)")
    except Exception as e:
        print(f"❌ Extraction failed with error: {e}")
        raise

    print("\n🗑️  Cleaning up zip file...")
    try:
        downloaded_zip.unlink()
        print(f"✅ Removed zip file: {downloaded_zip}")
    except Exception as e:
        print(f"⚠️  Warning: Could not remove zip file: {e}")

    gource_exe = get_gource_executable()
    if gource_exe.exists():
        print(f"\n✅ Gource executable found at: {gource_exe}")
        dll_dir = gource_exe.parent
        dll_count = len(list(dll_dir.glob("*.dll")))
        print(f"   Found {dll_count} DLL dependencies in: {dll_dir}")
    else:
        print(f"\n⚠️  Warning: Expected executable not found at: {gource_exe}")
        print(f"   Contents of {install_dir}:")
        for item in install_dir.rglob("*"):
            if item.is_file():
                print(f"     - {item.relative_to(install_dir)}")

    print("\n" + "=" * 80)
    print("✅ GOURCE PORTABLE INSTALLATION COMPLETED")
    print("=" * 80)
    print(f"\n📌 Gource installed to: {install_dir}")
    print(f"   Executable: {gource_exe}")
    print("   All DLL dependencies are kept together in the same directory.")
    print("   This script will automatically use the portable version.")


def visualize(
    repo: Annotated[str, typer.Option("--repo", "-r", help="Path to git repository to visualize")] = ".",
    output_file: Annotated[Optional[Path], typer.Option("--output", "-o", help="Output video file (e.g., output.mp4). If specified, gource will render to video.")] = None,
    resolution: Annotated[str, typer.Option("--resolution", "-res", help="Video resolution (e.g., 1920x1080, 1280x720)")] = "1920x1080",
    seconds_per_day: Annotated[float, typer.Option("--seconds-per-day", "-spd", help="Speed of simulation (lower = faster)")] = 0.1,
    auto_skip_seconds: Annotated[float, typer.Option("--auto-skip-seconds", "-as", help="Skip to next entry if nothing happens for X seconds")] = 1.0,
    title: Annotated[Optional[str], typer.Option("--title", "-t", help="Title for the visualization")] = None,
    hide_items: Annotated[list[str], typer.Option("--hide", "-h", help="Items to hide: bloom, date, dirnames, files, filenames, mouse, progress, root, tree, users, usernames")] = [],
    key_items: Annotated[bool, typer.Option("--key", "-k", help="Show file extension key")] = False,
    fullscreen: Annotated[bool, typer.Option("--fullscreen", "-f", help="Run in fullscreen mode")] = False,
    viewport: Annotated[Optional[str], typer.Option("--viewport", "-v", help="Camera viewport (e.g., '1000x1000')")] = None,
    start_date: Annotated[Optional[str], typer.Option("--start-date", help="Start date (YYYY-MM-DD)")] = None,
    stop_date: Annotated[Optional[str], typer.Option("--stop-date", help="Stop date (YYYY-MM-DD)")] = None,
    user_image_dir: Annotated[Optional[Path], typer.Option("--user-image-dir", help="Directory with user avatar images")] = None,
    max_files: Annotated[int, typer.Option("--max-files", help="Maximum number of files to show (0 = no limit)")] = 0,
    max_file_lag: Annotated[float, typer.Option("--max-file-lag", help="Max time files remain on screen after last change")] = 5.0,
    file_idle_time: Annotated[int, typer.Option("--file-idle-time", help="Time in seconds files remain idle before being removed")] = 0,
    framerate: Annotated[int, typer.Option("--framerate", help="Frames per second for video output")] = 60,
    background_color: Annotated[str, typer.Option("--background-color", help="Background color in hex (e.g., 000000 for black)")] = "000000",
    font_size: Annotated[int, typer.Option("--font-size", help="Font size")] = 22,
    camera_mode: Annotated[str, typer.Option("--camera-mode", help="Camera mode: overview or track")] = "overview",
) -> None:
    """
    Visualize git repository history using Gource with reasonable defaults.
    
    Examples:
        # Basic visualization of current directory
        python grource.py visualize
        
        # Visualize specific repository
        python grource.py visualize --repo-path /path/to/repo
        
        # Create video output
        python grource.py visualize --output output.mp4
        
        # Fast visualization with custom title
        python grource.py visualize --seconds-per-day 0.01 --title "My Project"
        
        # Hide specific elements
        python grource.py visualize --hide filenames --hide date
        
        # Custom resolution and viewport
        python grource.py visualize --resolution 2560x1440 --viewport 1200x1200
    """
    print("\n" + "=" * 80)
    print("🎬 GOURCE VISUALIZATION 🎬")
    print("=" * 80 + "\n")
    repo_path: Path = Path(repo).expanduser().resolve()
    if not repo_path.exists():
        print(f"❌ Error: Repository path does not exist: {repo_path}")
        raise typer.Exit(1)

    if not repo_path.joinpath(".git").exists():
        print(f"❌ Error: Not a git repository: {repo_path}")
        raise typer.Exit(1)

    print(f"📁 Repository: {repo_path}")
    print("⚙️  Configuration:")
    print(f"   - Resolution: {resolution}")
    print(f"   - Speed: {seconds_per_day} seconds per day")
    print(f"   - Auto-skip: {auto_skip_seconds} seconds")
    if output_file:
        print(f"   - Output: {output_file}")
    print()

    gource_exe: Path = get_gource_executable()
    if not gource_exe.exists():
        if platform.system() == "Windows":
            print(f"⚠️  Portable gource not found at {gource_exe}, installing...")
            install_gource_windows()
            # Check again after installation
            if gource_exe.exists():
                print(f"✅ Gource installed successfully at: {gource_exe}")
                gource_cmd: str = str(gource_exe)
            else:
                print("❌ Installation failed, falling back to system gource")
                raise typer.Exit(1)
        else:
            raise FileNotFoundError(f"Gource executable not found at {gource_exe}. Please install gource using your package manager.")
    else:
        gource_cmd = str(gource_exe)

    cmd: list[str] = [gource_cmd, str(repo_path)]

    cmd.extend(["--seconds-per-day", str(seconds_per_day)])
    cmd.extend(["--auto-skip-seconds", str(auto_skip_seconds)])

    if resolution:
        width, height = resolution.split("x")
        cmd.extend(["-{}x{}".format(width, height)])

    if title:
        cmd.extend(["--title", title])
    elif not title and not output_file:
        cmd.extend(["--title", repo_path.name])

    for hide_item in hide_items:
        cmd.extend(["--hide", hide_item])

    if key_items:
        cmd.append("--key")

    if fullscreen and not output_file:
        cmd.append("--fullscreen")

    if viewport:
        cmd.extend(["--viewport", viewport])

    if start_date:
        cmd.extend(["--start-date", start_date])

    if stop_date:
        cmd.extend(["--stop-date", stop_date])

    if user_image_dir and user_image_dir.exists():
        cmd.extend(["--user-image-dir", str(user_image_dir)])

    if max_files > 0:
        cmd.extend(["--max-files", str(max_files)])

    cmd.extend(["--max-file-lag", str(max_file_lag)])

    if file_idle_time > 0:
        cmd.extend(["--file-idle-time", str(file_idle_time)])

    cmd.extend(["--background-colour", background_color])
    cmd.extend(["--font-size", str(font_size)])
    cmd.extend(["--camera-mode", camera_mode])

    if output_file:
        cmd.extend(["-r", str(framerate)])
        if platform.system() == "Windows":
            cmd.extend(["-o", "-"])
            ffmpeg_cmd: list[str] = [
                "ffmpeg",
                "-y",
                "-r", str(framerate),
                "-f", "image2pipe",
                "-vcodec", "ppm",
                "-i", "-",
                "-vcodec", "libx264",
                "-preset", "medium",
                "-pix_fmt", "yuv420p",
                "-crf", "23",
                str(output_file),
            ]
            print("🎥 Rendering video...")
            print(f"   Command: {' '.join(cmd)} | {' '.join(ffmpeg_cmd)}")
            print()
            try:
                gource_proc: subprocess.Popen[bytes] = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                ffmpeg_proc: subprocess.Popen[bytes] = subprocess.Popen(ffmpeg_cmd, stdin=gource_proc.stdout)
                if gource_proc.stdout:
                    gource_proc.stdout.close()
                ffmpeg_proc.communicate()
                print(f"\n✅ Video saved to: {output_file}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Error during video rendering: {e}")
                raise typer.Exit(1)
            except FileNotFoundError:
                print("❌ Error: ffmpeg not found. Please install ffmpeg to create video output.")
                print("   Download from: https://ffmpeg.org/download.html")
                raise typer.Exit(1)
        else:
            cmd.extend(["-o", "-"])
            ffmpeg_cmd = [
                "ffmpeg",
                "-y",
                "-r", str(framerate),
                "-f", "image2pipe",
                "-vcodec", "ppm",
                "-i", "-",
                "-vcodec", "libx264",
                "-preset", "medium",
                "-pix_fmt", "yuv420p",
                "-crf", "23",
                str(output_file),
            ]
            print("🎥 Rendering video...")
            print(f"   Command: {' '.join(cmd)} | {' '.join(ffmpeg_cmd)}")
            print()
            try:
                gource_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                ffmpeg_proc = subprocess.Popen(ffmpeg_cmd, stdin=gource_proc.stdout)
                if gource_proc.stdout:
                    gource_proc.stdout.close()
                ffmpeg_proc.communicate()
                print(f"\n✅ Video saved to: {output_file}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Error during video rendering: {e}")
                raise typer.Exit(1)
            except FileNotFoundError:
                print("❌ Error: ffmpeg not found. Please install ffmpeg to create video output.")
                raise typer.Exit(1)
    else:
        print("🎬 Launching interactive visualization...")
        print(f"   Command: {' '.join(cmd)}")
        print()
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running gource: {e}")
            raise typer.Exit(1)
        except FileNotFoundError:
            print("❌ Error: gource not found. Please install gource first.")
            if platform.system() == "Windows":
                print("   Run: uv run python src/machineconfig/scripts/python/grource.py install")
            else:
                print("   For Linux/Mac, use your package manager:")
                print("     - Ubuntu/Debian: sudo apt install gource")
                print("     - macOS: brew install gource")
                print("     - Fedora: sudo dnf install gource")
            raise typer.Exit(1)

    print("\n" + "=" * 80)
    print("✅ VISUALIZATION COMPLETED")
    print("=" * 80)


def install(
    version: Annotated[Optional[str], typer.Option(..., "--version", "-v", help="Gource version to install")] = "0.53",
) -> None:
    """Install portable Gource on Windows (no admin privileges required)."""
    if platform.system() == "Windows":
        install_gource_windows(version=version)
    else:
        print(f"❌ Portable installer currently supports Windows only. Current OS: {platform.system()}")
        print("For Linux/Mac, please use your package manager:")
        print("  - Ubuntu/Debian: sudo apt install gource")
        print("  - macOS: brew install gource")
        print("  - Fedora: sudo dnf install gource")
        raise typer.Exit(1)


if __name__ == "__main__":
    app = typer.Typer(help="Gource visualization tool for git repositories", add_help_option=False, add_completion=False)
    app.command()(install)
    app.command()(visualize)
    app()
