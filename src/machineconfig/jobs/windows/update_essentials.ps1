
$orig_path = $PWD
cd ~/code/crocodile
git pull origin # --git-dir $env:USERPROFILE/code/crocodile/.git
cd ~/code/machineconfig
git pull origin # --git-dir $env:USERPROFILE/code/machineconfig/.git
cd $orig_path
