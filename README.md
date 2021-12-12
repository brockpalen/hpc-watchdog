# HPCWatchdog

Uses system specific kernel level support to monitor for file creation/changes to automtically transfer and delete.

## Intended Use

In lab environments where data are collected at increasingly high rates the longer data accumulates in the lab the larger buffer storage is required in the lab, and the higher burst network capacity would be required to move a given amount of data.

## Workflow

 * Monitor a given folder using python watchdog
 * Every `sleep` seconds look at list of all files that have been created/modified sense script started
 * If any file has not be modified in `dwell-time` seconds build a list of files and submit to globus to transfer
 * Once a transfer completes without error delete same list of files

## Basic Usage

```
# currently requires full path to folder not relative
hpc-watchdog --path <absolutepath> --prepopulate \
--sleep 900 --dwell-time 600 \
--source <GLOBUS-UUID> --destination <GLOBUS-UUID> \
--destination-dir <path>  --notify on
```

## logging

Currently logging is very basic and will log to the `log` folder in the source
tree. Logs will rotate nightly for 30 days.

You can force the watchdog to dump it's current status by sending the running
process signals

```
# force logging of basic status of watchdog
killall -SIGUSR1 hpc-watchdog

# force loging of detailed status of watchdog
killall -SIGUSR2 hpc-watchdog
```

## TODO

  * Transfer and delete first list then startup
 * Optionally don't delete files
 * Monitor for files only matching a pattern
 * Very verbose logging
  * Syslog
  * Dedicated log file
