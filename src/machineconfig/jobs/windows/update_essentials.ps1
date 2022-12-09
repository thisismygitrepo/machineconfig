
$orig_path = $PWD

# updateBegins

cd ~/code/crocodile
git pull origin # --git-dir $env:USERPROFILE/code/crocodile/.git

cd ~/code/machineconfig
git pull origin # --git-dir $env:USERPROFILE/code/machineconfig/.git

# updateEnds

cd $orig_path
