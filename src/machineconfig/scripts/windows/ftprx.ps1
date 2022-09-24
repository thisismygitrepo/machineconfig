# CroShellFTP 1.0
param ($machine="", $file1="")

croshell -c @"
print(r'$machine', r'$file1')
ssh = SSH(r'$machine')
ssh.copy_to_here(r'$file1', zip_first=True)
ssh.print_summary()
"@

