

# ==== Fancy shell:
winget install JanDeDobbeleer.OhMyPosh
cd ~/code/dotfiles

& ~/venvs/$ve_name/Scripts/Activate.ps1

python -m fire ./jobs/backup_retrieve.py retrieve_dotfiles  # assuming key.zip is in Downloads folder.
python -m fire "./create_symlinks.py" main
python -m fire "./create_symlinks.py" add_scripts_to_path  # croshell is available, along with all scripts via $profile adding script path to env.Path

python -m fire "windows_terminal_setup/change_terminal_settings.py" main
python -m fire "windows_terminal_setup/fancy_prompt_themes.py" install
python -m fire "windows_terminal_setup/fancy_prompt_themes.py" choose

croshell -c "P(r'https://download.sysinternals.com/files/ZoomIt.zip').download(P.home().joinpath('Downloads')).unzip(inplace=True).joinpath('ZoomIt.exe').move(folder=P.env().WindowsApps)"
