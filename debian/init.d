#!/bin/bash
#
### BEGIN INIT INFO
# Provides:		bricklayer
# Required-Start:	$network $local_fs $remote_fs
# Required-Stop:	$network $local_fs $remote_fs
# Should-Start:		$network
# Should-Stop:		$network
# Default-Start:	2 3 4 5
# Default-Stop:		0 1 6
# Short-Description:	start and stop Bricklayer Package Builder
# Description:		The Bricklayer Package Builder builds packages to
# 			help you automate builds and upload packages to repositories.
### END INIT INFO

PATH=/usr/bin:/usr/sbin:/bin:/sbin
DAEMON=/usr/bin/twistd
RUNDIR=/var/run
PIDFILE=/var/run/bricklayer.pid
PIDFILE_REST=/var/run/bricklayer-rest.pid
LOGFILE=/var/log/bricklayer.log
LOGFILE_REST=/var/log/bricklayer-rest.log

# Include bricklayer defaults if available
if [ -r /etc/default/bricklayer ]; then
	. /etc/default/bricklayer
fi

test -x ${DAEMON} || exit 0

case "$1" in
  start)
	echo -n "Starting bricklayer"
	${DAEMON} --pidfile=${PIDFILE} --logfile=${LOGFILE} bricklayer 2>&1 > /dev/null &
	${DAEMON} --pidfile=${PIDFILE_REST} --logfile=${LOGFILE_REST} bricklayer_web 2>&1 > /dev/null &
	echo "."	
	;;
  stop)
	echo -n "Stopping bricklayer"
	cat ${PIDFILE} | xargs kill
	cat ${PIDFILE_REST} | xargs kill

	echo "."
	;;
  restart)
	${0} stop
	sleep 1
	${0} start
	;;
  force-reload)
	${0} restart
	;;
  *)
	echo "Usage: ${0} {start|stop|restart|force-reload}" >&2
	exit 1
	;;
esac

exit 0

