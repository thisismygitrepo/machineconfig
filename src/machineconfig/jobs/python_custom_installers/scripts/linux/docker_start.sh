#!/bin/sh

### BEGIN INIT INFO
# Provides:          docker
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start daemon at boot time
# Description:       Enable service provided by daemon.
### END INIT INFO
# this file must be placed @ /etc/init.d/docker

case "$1" in
  start)
    echo "Starting Docker..."
    /usr/bin/dockerd &
    ;;
  stop)
    echo "Stopping Docker..."
    killall dockerd
    ;;
  *)
    echo "Usage: /etc/init.d/docker {start|stop}"
    exit 1
    ;;
esac

exit 0

