
# Parse command-line arguments
$params = @{
    Message = "a new version"
}
#$args | ForEach-Object {
#    switch -Regex ($_ -split '=') {
#        '--message' { $params.Message = $_.Split('=')[1] }
#        '-m' { $params.Message = $_.Split('=')[1] }
#        default { Write-Warning "Unknown parameter: $_" }
#    }
#}


$dir_orig = pwd
if (!(Test-Path $HOME/dotfiles/config/setup/rclone_remote)) {
    echo "Path $HOME/dotfiles/config/setup/rclone_remote does not exist. Aborting"
    exit
}
$rclone_remote = cat $HOME/dotfiles/config/setup/rclone_remote

echo ""
echo "=============================== Committing Local Changes ==================================="
cd ~/dotfiles
git status
git add .
git commit -am $params.Message


echo ""
echo ""
echo "=============================== Downloading Remote Repo ===================================="
mkdir ~/.machineconfig -ErrorAction SilentlyContinue
rm ~/.machineconfig/remote/dotfiles/* -r -force -ErrorAction SilentlyContinue
rm ~/.machineconfig/remote/dotfiles -r -force -ErrorAction SilentlyContinue
cloud_rx $rclone_remote myhome/generic_os/dotfiles -zew -l ~/.machineconfig/remote/dotfiles  # overwrite, zip and encrypt
mv ~/.machineconfig/dotfiles ~/.machineconfig/remote/dotfiles

# if remote doesn't exist
# rclone lsf odg1:myhome/generic_os/dotfiles.zip.encf
# if remot doesn't exists, push it for first time cloud_sx $rclone_remote ~/dotfiles -zer

echo ""
echo ""
echo "=============================== Pulling Latest From Remote ================================"
cd ~/dotfiles
git remote remove origin
git remote add origin $HOME/.machineconfig/remote/dotfiles
git pull origin master


$share = git pull origin master

if($?)
{
   echo ""
   echo "Pull succeeded, removing local copy of remote & pushing merged repo to remote ... "
   rm ~/.machineconfig/remote/dotfiles/* -r -force -ErrorAction SilentlyContinue
   rm ~/.machineconfig/remote/dotfiles -r -force -ErrorAction SilentlyContinue
   echo ""
   echo ""
   echo "===================================== Pushing new repository to remote ======================================="
   cloud_sx $rclone_remote ~/dotfiles -zer

}
else
{
   echo ""
   echo "Pull failed. Check the remote @ ~/.machineconfig/remote/dotfiles"
}

# $confirmation = Read-Host "Did the pull from origin merge correctly? [y/n]"
# if ($confirmation -eq 'y') {

cd $dir_orig

