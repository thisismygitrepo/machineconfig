
$dir_orig = pwd
if (!(Test-Path $HOME/dotfiles/config/setup/rclone_remote)) {
    echo "Path $HOME/dotfiles/config/setup/rclone_remote does not exist. Aborting"
    exit
}
$rclone_remote = cat $HOME/dotfiles/config/setup/rclone_remote

echo ""
echo ""
echo "=============================== Downloading Remote Repo ===================================="
mkdir ~/.machineconfig/remote -ErrorAction SilentlyContinue
rm ~/.machineconfig/remote/dotfiles/* -r -force -ErrorAction SilentlyContinue
rm ~/.machineconfig/remote/dotfiles -r -force -ErrorAction SilentlyContinue
cloud_rx $rclone_remote myhome/generic_os/dotfiles -zew -l ~/.machineconfig/remote/dotfiles  # overwrite, zip and encrypt
mv ~/.machineconfig/dotfiles ~/.machineconfig/remote/dotfiles


echo ""
echo ""
echo "=============================== Pulling Remote Repo ===================================="
cd ~/dotfiles
git remote remove origin
git remote add origin $HOME/.machineconfig/remote/dotfiles



$share = git pull origin master

if($?)
{
   echo ""
   echo "Pull succeeded, removing local copy of remote ... "
   rm ~/.machineconfig/remote/dotfiles/* -r -force -ErrorAction SilentlyContinue
   rm ~/.machineconfig/remote/dotfiles -r -force -ErrorAction SilentlyContinue
}
else
{
   echo ""
   echo "Pull failed. Check the remote @ ~/.machineconfig/remote/dotfiles"
}

cd $dir_orig

