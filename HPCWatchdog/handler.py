import pathlib
import time

import watchdog.events
import watchdog.observers
from watchdog.observers.polling import PollingObserver as PollingObserver

from GlobusTransfer import GlobusTransfer

from .log import logger


class Handler(watchdog.events.PatternMatchingEventHandler):
    def __init__(self, args):
        # Set the patterns for PatternMatchingEventHandler
        watchdog.events.PatternMatchingEventHandler.__init__(
            self, patterns=["*"], ignore_directories=True, case_sensitive=False
        )
        self.file_list = FileList()
        self.expired_lists = []
        self.globus = GlobusTransfer(
            args.source, args.destination, args.destination_dir, args.path
        )
        self.iteration = 0  # How many round trips have we made

    def on_created(self, event):
        logger.info("Watchdog received created event - % s." % event.src_path)
        self.file_list.files[event.src_path] = time.time()
        # Event is created, you can process it now

    def on_modified(self, event):
        logger.debug("Watchdog received modified event - % s." % event.src_path)
        # Event is modified, you can process it now
        now = time.time()
        self.file_list.files[event.src_path] = now
        if event.src_path in self.file_list.files:
            logger.debug(
                f"Old Stamp: {self.file_list.files[event.src_path]} New Stamp {now}"
            )
        else:
            logger.debug(f"Existing file modifed but not in list inserting {now}")

    def new_iteration(self, dwell_time):
        """
        Start a new pass of the following.

        Create new FileList()
        For each file in main filelist where age > dwell_time move to file list
        If FileList() not empty
        Push onto list and create globus transfer
        """
        new_list = FileList()
        self.iteration += 1
        for path, last_seen in self.file_list.files.items():
            logger.debug(f"Path: {path} last seen: {last_seen}")
            # is now - last_seen > dwell_time add to transfer list
            now = time.time()
            delta = now - last_seen
            if delta > dwell_time:
                logger.debug(f"File {path} Dwell Expired")
                # add path to new list
                new_list.files[path] = last_seen
                # Submit to globus
                logger.debug(
                    f"Adding {path} to transfer for iteration {self.iteration}"
                )
                self.globus.add_item(path, label=f"{self.iteration}")

        # delete from origonal list
        # can't be done as part of above loop for dictionary changed size during iteration error
        for path, last_seen in new_list.files.items():
            del self.file_list.files[path]

        if new_list.files:
            taskid = self.globus.submit_pending_transfer()
            logger.info(f"Submitted Globus TaskID: {taskid}")

            new_list.taskid = taskid

            logger.debug("New List is not empty adding to expired_lists")
            self.expired_lists.append(new_list)

        #  TODO check for each expired_lists.taskid status
        for filelist in self.expired_lists:
            taskid = filelist.taskid
            resp = self.globus.tc.get_task(taskid)
            logger.debug(f"Status of {taskid} is {resp['status']}")

            # Transfer complete
            if resp["status"] == "SUCCEEDED":
                for path in filelist.files:
                    logger.debug(f"Deleting {path}")
                    # TODO: make function and check if atime is younger than stored time
                    pathlib.Path(path).unlink()

                # Delete entry from expired_lists
                self.expired_lists.remove(filelist)

            # not complete but not healthy
            elif resp["nice_status"] != "Queued":
                logger.error(
                    f"Globus TaskID {taskid} unhealthy {resp['nice_status']} : {resp['nice_status_short_description']}"
                )
                logger.error(resp)

    def status(self, details=False):
        """Dump the status of the current handler."""
        logger.info(f"Currently have {len(self.expired_lists)} expired lists in flight")
        logger.info(
            f"Currently watching {len(self.file_list.files)} files under their dwell-time"
        )

        if details:
            for path, value in self.file_list.files.items():
                logger.info(f"Watching File: {path} Last Seen: {value}")

            for filelist in self.expired_lists:
                logger.info(f"Dumping expired list TaskID: {filelist.taskid}")
                for path in filelist.files:
                    logger.info(f"Expired Entry: {filelist.taskid} Path: {path}")


class FileList:
    def __init__(self):
        self.files = {}
        self.taskid = None
