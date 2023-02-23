
$dir_orig = pwd
if (!(Test-Path $HOME/dotfiles/config/setup/rclone_remote)) {
    echo "Path $HOME/dotfiles/config/setup/rclone_remote does not exist. Aborting"
    exit
}
$rclone_remote = cat $HOME/dotfiles/config/setup/rclone_remote

echo ""
echo ""
echo "=============================== Downloading Remote Repo ===================================="
mkdir ~/.machineconfig -ErrorAction SilentlyContinue
rm ~/.machineconfig/sync_dotfiles/* -r -force -ErrorAction SilentlyContinue
rm ~/.machineconfig/sync_dotfiles -r -force -ErrorAction SilentlyContinue
cloud_rx $rclone_remote myhome/generic_os/dotfiles -zew -l ~/.machineconfig/sync_dotfiles  # overwrite, zip and encrypt
mv ~/.machineconfig/dotfiles ~/.machineconfig/sync_dotfiles


echo ""
echo ""
echo "=============================== Pulling Remote Repo ===================================="
cd ~/dotfiles
git remote remove origin
git remote add origin $HOME/.machineconfig/sync_dotfiles



$share = git pull origin master

if($?)
{
   echo ""
   echo "Pull succeeded, removing local copy of remote ... "
   rm ~/.machineconfig/sync_dotfiles/* -r -force -ErrorAction SilentlyContinue
   rm ~/.machineconfig/sync_dotfiles -r -force -ErrorAction SilentlyContinue
}
else
{
   echo ""
   echo "Pull failed. Check the remote @ ~/.machineconfig/sync_dotfiles"
}

cd $dir_orig

