import time

import watchdog.events
import watchdog.observers
from watchdog.observers.polling import PollingObserver as PollingObserver

from .log import logger


class Handler(watchdog.events.PatternMatchingEventHandler):
    def __init__(self):
        # Set the patterns for PatternMatchingEventHandler
        watchdog.events.PatternMatchingEventHandler.__init__(
            self, patterns=["*.csv"], ignore_directories=True, case_sensitive=False
        )
        self.file_list = FileList()
        self.expired_lists = []

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
        for path, last_seen in self.file_list.files.items():
            logger.debug(f"Path: {path} last seen: {last_seen}")
            # is now - last_seen > dwell_time add to transfer list
            now = time.time()
            delta = now - last_seen
            if delta > dwell_time:
                logger.debug(f"File {path} Dwell Expired")
                # add path to new list
                new_list.files[path] = last_seen

        # delete from origonal list
        # can't be done as part of above loop for dictionary changed size during iteration error
        for path, last_seen in new_list.files.items():
            del self.file_list.files[path]

        if new_list.files:
            logger.debug("New List is not empty adding to expired_lists")
            self.expired_lists.append(new_list)
            #  TODO Submit to globus

        #  TODO check for each expired_lists.taskid status


class FileList:
    def __init__(self):
        self.files = {}
        self.taskid = None
