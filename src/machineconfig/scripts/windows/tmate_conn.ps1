
$sess_name = Get-Content ~/dotfiles/creds/tmate/$args
$user_name = Get-Content ~/dotfiles/creds/tmate/username

echo "Session name: $sess_name"

ssh $user_name/$sess_name@sgp1.tmate.io
