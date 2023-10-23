
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

if (!(Test-Path $repo_root)) {
    $repo_root = "$HOME/dotfiles"
}

$repo_root = [System.IO.Path]::GetFullPath($repo_root)
$repo_root_rel2home = [System.IO.Path]::GetRelativePath($HOME, $repo_root)

echo ""
echo "=============================== Committing Local Changes ==================================="
cd $repo_root
git status
git add .
git commit -am $params.Message


echo ""
echo ""
echo "=============================== Downloading Remote Repo ===================================="
mkdir ~/.machineconfig -ErrorAction SilentlyContinue
rm ~/.machineconfig/remote/$repo_root_rel2home/* -r -force -ErrorAction SilentlyContinue
rm ~/.machineconfig/remote/$repo_root_rel2home -r -force -ErrorAction SilentlyContinue
cloud_rx $rclone_remote myhome/os_specific/$repo_root_rel2home -zew -l $HOME/.machineconfig/remote/$repo_root_rel2home  # overwrite, zip and encrypt


if (!(Test-Path $HOME/.machineconfig/remote/$repo_root_rel2home)) {
    echo ""
    echo "💥 Remote doesn't exist, creating it and exiting ... "
    cloud_sx $rclone_remote $repo_root -zer
    exit
}

echo ""
echo ""
echo "=============================== Pulling Latest From Remote ================================"
cd $repo_root
git remote remove originEnc
git remote add originEnc $HOME/.machineconfig/remote/$repo_root_rel2home

$share = git pull originEnc master

if($?)
{
   echo ""
   echo "Pull succeeded, removing originEnc, the local copy of remote & pushing merged repo to remote ... "
   git remote remove originEnc
   rm ~/.machineconfig/remote/$repo_root_rel2home/* -r -force -ErrorAction SilentlyContinue
   rm ~/.machineconfig/remote/$repo_root_rel2home -r -force -ErrorAction SilentlyContinue
   echo ""
   echo ""
   echo "===================================== Pushing new repository to remote ======================================="
   cloud_sx $rclone_remote $repo_root -zer

}
else
{
   echo ""
   echo "Pull failed. Check the remote @ ~/.machineconfig/remote/$repo_root_rel2home"
}

# $confirmation = Read-Host "Did the pull from originEnc merge correctly? [y/n]"
# if ($confirmation -eq 'y') {

cd $dir_orig

