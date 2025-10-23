
import typer
from typing import Annotated


def choose_zellij_session():
    cmd = "zellij list-sessions"
    import subprocess
    sessions: list[str] = subprocess.check_output(cmd, shell=True).decode().strip().split("\n")
    sessions.sort(key=lambda s: "EXITED" in s)
    if "current" in sessions:
        print("Already in a Zellij session, avoiding nesting and exiting.")
        raise typer.Exit()
    if len(sessions) == 0:
        print("No Zellij sessions found, creating a new one.")
        result = """zellij --layout st2"""
    elif len(sessions) == 1:
        session = sessions[0].split(" [Created")[0]
        print(f"Only one Zellij session found: {session}, attaching to it.")
        result = f"zellij attach {session}"
    else:
        from machineconfig.utils.options import choose_from_options
        session = choose_from_options(msg="Choose a Zellij session to attach to:", multi=False, options=sessions, fzf=True)
        session = session.split(" [Created")[0]
        result = f"zellij attach {session}"
    from machineconfig.utils.code import exit_then_run_shell_script
    exit_then_run_shell_script(result, strict=True)


def new_zellij_session(kill_all: Annotated[bool, typer.Option("--kill-all", "-k", help="Kill all existing Zellij sessions before creating a new one.", show_default=True)] = False):
    cmd = """
zellij --layout st2
"""
    if kill_all:
        cmd = f"""zellij kill-sessions
{cmd}"""
    from machineconfig.utils.code import exit_then_run_shell_script
    exit_then_run_shell_script(cmd, strict=True)


def main():
    app = typer.Typer(help="🖥️ Terminal utilities", no_args_is_help=True, add_help_option=False)
    app.command(name="choose-zellij-session", no_args_is_help=False, help="[c] Choose a Zellij session to attach to")(choose_zellij_session)
    app.command(name="c", hidden=True, no_args_is_help=False, help="[c] Choose a Zellij session to attach to")(choose_zellij_session)
    app.command(name="new-zellij-session", no_args_is_help=False, help="[n] new zellij session.")(new_zellij_session)
    app.command(name="n", hidden=True, no_args_is_help=False, help="[n] new zellij session.")(new_zellij_session)
    app()


if __name__ == "__main__":
    main()

"""
# adopted from https://zellij.dev/documentation/integration.html
ZJ_SESSIONS=$(zellij list-sessions)


attach=false

while (( "$#" )); do
  case "$1" in
    --attach)
      attach=true
      shift
      ;;
    *)
      shift
      ;;
  esac
done

if $attach; then
  echo "attached"
fi


NO_SESSIONS=$(echo "${ZJ_SESSIONS}" | wc -l)
# if ZJ_SESSIONS is empty, then set NO_SESSIONS to 0
if [ -z "${ZJ_SESSIONS}" ]; then
    NO_SESSIONS=0
fi

# check whether the string "(current)" is in ZJ_SESSIONS
if [[ "${ZJ_SESSIONS}" == *"(current)"* ]]; then
    # if so, then we are in a zellijsession
    echo "already inside a session, existing."
    COMMANDS=$(ls $HOME/.config/machineconfig/settings/zellij/commands)
    # fzf the results
    res="$(echo -e "${COMMANDS}" | fzf --ansi)"
    # run the bash fiZJ_SESSIONSle chosen
    bash $HOME/.config/machineconfig/settings/zellij/commands/$res

else # ==> we are not in a zellijsession
  if [ "${NO_SESSIONS}" -ge 1 ]; then  # sessions do exist

      # remove sessions that have 'EXITED' in them
      ZJ_SESSIONS=$(echo -e "${ZJ_SESSIONS}" | grep -v "EXITED")

      echo "zj_sessions:$ZJ_SESSIONS:end of zj_sessions"

      # if the result has only 1 line in it and $attach is raised, then attach to it and exit the if statement and the script
      NO_SESSIONS=$(echo "${ZJ_SESSIONS}" | wc -l)

      echo "NO_SESSIONS: $NO_SESSIONS"

      # if ZJ_SESSIONS is empty, then set NO_SESSIONS to 0
      if [ -z "${ZJ_SESSIONS}" ]; then
          NO_SESSIONS=0
          zellij --layout st2
          exit 0
      fi
      echo "NO_SESSIONS: $NO_SESSIONS"

      if [ "${NO_SESSIONS}" -eq 1 ] && $attach; then
        chosen_session=$(echo -e "${ZJ_SESSIONS}" | cut -d' ' -f1)
        # remove the ansi colors from chosen_session
        # echo "attaching to $chosen_session exclusively."
        zellij attach "$chosen_session"
        exit 0
      fi

      # add my options to the list of sessions
      # if number of sessions is zero, then exclude ZJ_SESSIONS from the fzf options
      if [ "${NO_SESSIONS}" -eq 0 ]; then
          ZJ_SESSIONS="new_session\nkill_all_and_create_fresh_one\nexit_zellij"
        else
          ZJ_SESSIONS="$ZJ_SESSIONS\nnew_session\nkill_all_and_create_fresh_one\nexit_zellij"
      fi

      res="$(echo -e "${ZJ_SESSIONS}" | fzf --ansi)"
      # split `res` at the first space, and take the first element
      res=$(echo $res | cut -d' ' -f1)
      if [ "${res}" = "exit_zellij" ]; then
          echo "existing zellij."
      elif [ "${res}" = "new_session" ]; then
        zellij --layout st2  # can't specify name here. I can call it "main" only if it is the first, otherwise name conflict! also, can't use attach -c syntax because layout can't be specified.
      elif [ "${res}" = "kill_all_and_create_fresh_one" ]; then
        zellij ka -y
        zellij --layout st2
      else
        zellij attach $res # options --mirror-session false
      fi
  else  # no sessions, create one called main
     zellij --layout st2
  fi

fi

"""