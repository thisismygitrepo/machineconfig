
$dir_orig = pwd
if (!(Test-Path $HOME/dotfiles/config/setup/rclone_remote)) {
    echo "Path $HOME/dotfiles/config/setup/rclone_remote does not exist. Aborting"
    exit
}
$rclone_remote = cat $HOME/dotfiles/config/setup/rclone_remote
$repo_root = "$HOME/dotfiles"
$repo_root_rel2home = [System.IO.Path]::GetRelativePath($HOME, $repo_root)

echo ""
echo ""
echo "=============================== Downloading Remote Repo ===================================="
mkdir ~/.machineconfig/remote -ErrorAction SilentlyContinue
rm ~/.machineconfig/remote/$repo_root_rel2home/* -r -force -ErrorAction SilentlyContinue
rm ~/.machineconfig/remote/$repo_root_rel2home -r -force -ErrorAction SilentlyContinue
cloud_rx $rclone_remote myhome/os_specific/$repo_root_rel2home -zew -l ~/.machineconfig/remote/$repo_root_rel2home  # overwrite, zip and encrypt
# mv ~/.machineconfig/dotfiles ~/.machineconfig/remote/dotfiles


echo ""
echo ""
echo "=============================== Pulling Remote Repo ===================================="
cd $repo_root
git remote remove originEnc
git remote add originEnc $HOME/.machineconfig/remote/$repo_root_rel2home


$share = git pull originEnc master

if($?)
{
   echo ""
   echo "Pull succeeded, removing originEnc link and local copy of remote ... "
   git remote remote originEnc
   rm ~/.machineconfig/remote/$repo_root_rel2home/* -r -force -ErrorAction SilentlyContinue
   rm ~/.machineconfig/remote/$repo_root_rel2home -r -force -ErrorAction SilentlyContinue
}
else
{
   echo ""
   echo "Pull failed. Check the remote @ ~/.machineconfig/remote/$repo_root_rel2home"
}

cd $dir_orig

