#!/bin/sh
#=======================================================================
# 🐳 DOCKER DAEMON INIT SCRIPT 🐳
#=======================================================================
# This script should be placed at /etc/init.d/docker
# It manages Docker daemon startup/shutdown for systems without systemd

### BEGIN INIT INFO
# Provides:          docker
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start daemon at boot time
# Description:       Enable Docker service for systems without systemd
### END INIT INFO

case "$1" in
  start)
    echo """    #=======================================================================
    🚀 STARTING | Launching Docker daemon
    #=======================================================================
    """
    /usr/bin/dockerd &
    ;;
  stop)
    echo """    #=======================================================================
    🛑 STOPPING | Terminating Docker daemon
    #=======================================================================
    """
    killall dockerd
    ;;
  *)
    echo """    #=======================================================================
    ❓ USAGE | Command not recognized
    #=======================================================================
    
    📋 Valid commands: /etc/init.d/docker {start|stop}
    """
    exit 1
    ;;
esac

exit 0

