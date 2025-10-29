#!/usr/bin/env nu

def wrap-in-shell-script [command: string ...args: string] -> nothing {
  # ANSI color/style codes
  let bold = (char ansi_reset | str append "\e[1m")
  let reset = "\e[0m"
  let green = "\e[32m"
  let yellow = "\e[33m"
  let blue = "\e[34m"
  let red = "\e[31m"

  let random_name = (date now | format date "%s%N" | sha256sum | str substring 0..16)
  let op_dir = $"($env.HOME)/tmp_results/tmp_scripts/machineconfig"
  let op_program_path = $"($op_dir)/($random_name).sh"
  
  $env.OP_PROGRAM_PATH = $op_program_path
  
  let timestamp = (date now --utc | format date "%Y-%m-%d %H:%M:%SZ")
  
  print $"($bold)($blue)🛠️  machineconfig — running ($command)($reset)"
  print $"($blue)Timestamp:($reset) ($timestamp)"
  print $"($blue)Op program path:($reset) ($op_program_path)"

  # Forward arguments to the command
  let result = (
    try {
      nu -c $"($command) ($args | str join ' ')"
    } catch {
      $"Error running command: ($in)"
    }
  )

  if ($op_program_path | path exists) {
    print $"($green)🚀 Taking over from python script @ ($op_program_path)($reset)"
    
    if (which bat | is-empty | not) {
      bat --style=plain --paging=never $op_program_path
    } else {
      open $op_program_path
    }
    
    print $"($green)▶ Running...($reset)"
    
    let status = (
      try {
        bash $op_program_path
        0
      } catch {
        1
      }
    )
    
    if ($status == 0) {
      print $"($green)✅ '($command)' execution completed.($reset)"
    } else {
      print $"($yellow)⚠️  Program exited with status ($status)($reset)"
    }
  } else {
    print $"($green)✅ '($command)' execution completed.($reset)"
  }
}

def main [] {
  if ($nu.env.args | length) > 0 {
    wrap-in-shell-script ...$nu.env.args
  }
}

main
