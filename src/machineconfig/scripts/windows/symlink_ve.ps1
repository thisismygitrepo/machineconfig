


$ve_name = Read-Host "Enviroment name (ve)"

if ( $ve_name -eq "" )
{
    $ve_name = "ve"
}

$to = "~/venvs/" + $ve_name
~/scripts/activate_ve.ps1

python -c "import crocodile.toolbox as tb; tb.P(r'$pwd').joinpath('venv').symlink_to(r'$to'); tb.P('.gitignore').modify_text('venv', 'venv', newline=True)"

