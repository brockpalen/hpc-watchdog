# /usr/bin/python3

import logging
import sched
import signal
import sys
import time
from functools import partial

import watchdog.events
import watchdog.observers
from watchdog.observers.polling import PollingObserver as PollingObserver

from GlobusTransfer import GlobusTransfer

from .args import Args
from .handler import Handler
from .log import logger


def main(argv):

    args = Args(sys.argv[1:])

    # get GlobusTransfer Logger
    gt_logger = logging.getLogger("GlobusTransfer")
    gt_logger.setLevel(logging.DEBUG)

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
    gt_logger.addHandler(st_handler)

    # now that logging is setup log our settings
    args.log_settings()

    src_path = args.path
    # using globus, init to prompt for endpoiont activation etc
    GlobusTransfer(args.source, args.destination, args.destination_dir, src_path)

    event_handler = Handler(args)

    if args.prepopulate:
        event_handler.prepopulate()

    observer = watchdog.observers.Observer()
    # observer = watchdog.observers.Observer()
    observer.schedule(event_handler, path=src_path, recursive=True)

    # setup signal handler
    def dump_status(event_handler, signalNumber, frame, details=False):
        """Dump the Handler() status when USR1 is recived."""
        event_handler.status(details=details)

    signal.signal(signal.SIGUSR1, partial(dump_status, event_handler))
    signal.signal(signal.SIGUSR2, partial(dump_status, event_handler, details=True))

    observer.start()
    s = sched.scheduler(time.time, time.sleep)
    logger.info("Starting Main Event Loop")
    try:
        while True:
            logger.info(
                f"Starting iteration {event_handler.iteration} will sleep {args.sleep} seconds"
            )
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
