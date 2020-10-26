# HPCWatchdog

Uses system specific kernel level support to monitor for file creation/changes to automtically transfer and delete.

## Intended Use

In lab environments where data are collected at increasingly high rates the longer data accumulates in the lab the larger buffer storage is required in the lab, and the higher burst network capacity would be required to move a given amount of data.

## Workflow

 * Monitor a given folder using python watchdog
 * Every `sleep` seconds look at list of all files that have been created/modified sense script started
 * If any file has not be modified in `dwell-time` seconds build a list of files and submit to globus to transfer
 * Once a transfer completes without error delete same list of files

## TODO

 * Walk monitored filesystem on startup to pre-populate list of files
  * Transfer and delete first list then startup
 * Optionally don't delete files
 * Email / Plugable notification if globus transfer errors
 * Monitor for files only matching a pattern
 * Very verbose logging
  * Syslog
  * Dedicated log file
