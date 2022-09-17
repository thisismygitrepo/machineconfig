# CroShellFTP 1.0
param ($username1="", $hostname1="", $file1="")

croshell -c "
print(r'$username1', r'$hostname1', r'$file1')
ssh = SSH(username=r'$username1', hostname=r'$hostname1')
ssh.copy_from_here(r'$file1', zip_first=True)
ssh.print_summary()
"
