
# the patch is caleld zzzzzzellij.sh to make sure it is the last one to be sourced at the end of the .bashrc
# adopted from https://zellij.dev/documentation/integration.html
# eval "$(zellij setup --generate-auto-start bash)"
if [[ $(zellij list-sessions) != *"(current)"* ]]; then
  z_ls
# this statement prevents running z_ls script which is already not going to do anything except echoing that its already inside a session and will therefore not do anything.
# until programmatic detach functionality is implemented in zellij, this script will continue to not do anything if run inside a session.
fi
