"""Gource visualization tool for git repositories."""

from pathlib import Path
from typing import Optional
import subprocess
import platform
import typer


def install_gource_windows(version: Optional[str] = None) -> None:
    """Install Gource on Windows by downloading and running the official installer."""
    if platform.system() != "Windows":
        raise OSError(f"This installer is for Windows only. Current OS: {platform.system()}")

    from machineconfig.utils.path_extended import PathExtended
    from machineconfig.utils.source_of_truth import INSTALL_TMP_DIR

    print("\n" + "=" * 80)
    print("🚀 GOURCE WINDOWS INSTALLATION 🚀")
    print("=" * 80 + "\n")

    version_str = version or "0.53"
    installer_url = f"https://github.com/acaudwell/Gource/releases/download/gource-{version_str}/gource-{version_str}.win64-setup.exe"

    print(f"📥 Downloading Gource installer from: {installer_url}")
    downloaded_installer = PathExtended(installer_url).download(folder=INSTALL_TMP_DIR)
    print(f"✅ Downloaded to: {downloaded_installer}")

    print("\n🔧 Running Gource installer...")
    print("⚠️  Note: The installer will launch in GUI mode. Please follow the installation wizard.")

    try:
        result = subprocess.run([str(downloaded_installer), "/SILENT"], capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print("✅ Gource installed successfully (silent mode)")
        else:
            print("⚠️  Silent installation not supported, launching interactive installer...")
            subprocess.run([str(downloaded_installer)], check=True)
            print("✅ Gource installer launched. Please complete the installation manually.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed with error: {e}")
        raise
    except Exception as e:
        print(f"❌ Unexpected error during installation: {e}")
        raise

    print("\n🗑️  Cleaning up installer file...")
    try:
        downloaded_installer.delete(sure=True)
        print(f"✅ Removed installer: {downloaded_installer}")
    except Exception as e:
        print(f"⚠️  Warning: Could not remove installer file: {e}")

    print("\n" + "=" * 80)
    print("✅ GOURCE INSTALLATION COMPLETED")
    print("=" * 80)
    print("\n📌 Gource should now be available in your PATH.")
    print("   You can verify by running: gource --version")


def visualize(
    repo_path: Path = typer.Option(Path.cwd(), "--repo-path", "-r", help="Path to git repository to visualize"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output video file (e.g., output.mp4). If specified, gource will render to video."),
    resolution: str = typer.Option("1920x1080", "--resolution", "-res", help="Video resolution (e.g., 1920x1080, 1280x720)"),
    seconds_per_day: float = typer.Option(0.1, "--seconds-per-day", "-spd", help="Speed of simulation (lower = faster)"),
    auto_skip_seconds: float = typer.Option(1.0, "--auto-skip-seconds", "-as", help="Skip to next entry if nothing happens for X seconds"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Title for the visualization"),
    hide_items: list[str] = typer.Option([], "--hide", "-h", help="Items to hide: bloom, date, dirnames, files, filenames, mouse, progress, root, tree, users, usernames"),
    key_items: bool = typer.Option(False, "--key", "-k", help="Show file extension key"),
    fullscreen: bool = typer.Option(False, "--fullscreen", "-f", help="Run in fullscreen mode"),
    viewport: Optional[str] = typer.Option(None, "--viewport", "-v", help="Camera viewport (e.g., '1000x1000')"),
    start_date: Optional[str] = typer.Option(None, "--start-date", help="Start date (YYYY-MM-DD)"),
    stop_date: Optional[str] = typer.Option(None, "--stop-date", help="Stop date (YYYY-MM-DD)"),
    user_image_dir: Optional[Path] = typer.Option(None, "--user-image-dir", help="Directory with user avatar images"),
    max_files: int = typer.Option(0, "--max-files", help="Maximum number of files to show (0 = no limit)"),
    max_file_lag: float = typer.Option(5.0, "--max-file-lag", help="Max time files remain on screen after last change"),
    file_idle_time: int = typer.Option(0, "--file-idle-time", help="Time in seconds files remain idle before being removed"),
    framerate: int = typer.Option(60, "--framerate", help="Frames per second for video output"),
    background_color: str = typer.Option("000000", "--background-color", help="Background color in hex (e.g., 000000 for black)"),
    font_size: int = typer.Option(22, "--font-size", help="Font size"),
    camera_mode: str = typer.Option("overview", "--camera-mode", help="Camera mode: overview or track"),
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

    cmd = ["gource", str(repo_path)]

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
                print("   Run: python grource.py install")
            raise typer.Exit(1)

    print("\n" + "=" * 80)
    print("✅ VISUALIZATION COMPLETED")
    print("=" * 80)


def install(
    version: Optional[str] = typer.Option("0.53", "--version", "-v", help="Gource version to install"),
) -> None:
    """Install Gource on Windows."""
    if platform.system() == "Windows":
        install_gource_windows(version=version)
    else:
        print(f"❌ This installer currently supports Windows only. Current OS: {platform.system()}")
        print("For Linux/Mac, please use your package manager:")
        print("  - Ubuntu/Debian: sudo apt install gource")
        print("  - macOS: brew install gource")
        print("  - Fedora: sudo dnf install gource")
        raise typer.Exit(1)


if __name__ == "__main__":
    app = typer.Typer(help="Gource visualization tool for git repositories")
    app.command()(install)
    app.command()(visualize)
    app()
