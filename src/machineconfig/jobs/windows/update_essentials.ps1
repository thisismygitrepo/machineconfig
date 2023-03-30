
$orig_path = $PWD

# updateBegins

cd (python -c "print(__import__('crocodile').__file__[:-12])")
git pull origin # --git-dir $env:USERPROFILE/code/crocodile/.git

cd (python -c "print(__import__('machineconfig').__file__[:-12])")
git pull origin # --git-dir $env:USERPROFILE/code/machineconfig/.git

# updateEnds

cd $orig_path
