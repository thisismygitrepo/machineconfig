

* I have started a watch-exec server in my terminal and its working now.
* I have set it up to re-run the shell script `.ai/terminal/debug/command_runner.sh` automatically.
    * A re-run is triggered upon any change of any python file in the repo, or, any change in the command_runner.sh script itself.
* The shell script itself runs the python file we are working on using uv.
* The script redirects the output from terminal to the file ./.ai* Run takes 50 ms only. So by the time you finish editing any python file or the command runner script, the new output is ready for you to read in that text file.
* Run takes 50 ms only. So by the time you finish editing any python file or the command runner script, the new output is ready for you to read in that text file.

# Why did I set this up?
* Because this makes it much faster for you to iterate because pulling the terminal and closing it every time is a bit slow.
* You no longer need the terminal.


# What should you do now?
Please iterate like this:
* Please use the terminal_output.txt as your main iteration driver (fix any problems you see there).
* Change `command_runner.sh` if you need to change which python file to run or how to run it.


