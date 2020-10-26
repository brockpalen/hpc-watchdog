# /usr/bin/python3

import logging
import sched
import sys
import time
from pathlib import Path

import watchdog.events
import watchdog.observers
from watchdog.observers.polling import PollingObserver as PollingObserver

from .args import Args
from .handler import Handler
from .log import logger


def main(argv):

    args = Args(sys.argv[1:])

    # Set default level for all handlers
    logger.setLevel(logging.DEBUG)

    # stream / stderr handler
    st_handler = logging.StreamHandler()

    # set stream log format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    st_handler.setFormatter(formatter)

    logger.addHandler(st_handler)

    # now that logging is setup log our settings
    args.log_settings()

    src_path = args.path
    event_handler = Handler()
    observer = watchdog.observers.Observer()
    # observer = watchdog.observers.Observer()
    observer.schedule(event_handler, path=src_path, recursive=True)
    observer.start()
    s = sched.scheduler(time.time, time.sleep)
    logger.info("Starting Main Event Loop")
    try:
        while True:
            logger.info(f"In Main Event Loop will sleep {args.sleep} seconds")
            s.enter(
                args.sleep,
                1,
                event_handler.new_iteration,
                argument=(args.dwell_time,),
            )
            s.run()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
