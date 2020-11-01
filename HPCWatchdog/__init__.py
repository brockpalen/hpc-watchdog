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
from .log import logger, set_debug, set_gt_debug


def main(argv):

    args = Args(sys.argv[1:])

    # now that logging is setup log our settings
    args.log_settings()

    src_path = args.path

    # Did we ask for debug?
    if args.debug:
        set_debug()

    if args.globus_debug:
        set_gt_debug()

    # using globus, init to prompt for endpoiont activation etc
    GlobusTransfer(args.source, args.destination, args.destination_dir, src_path)

    event_handler = Handler(args)

    if args.prepopulate:
        event_handler.prepopulate()

    # observer = watchdog.observers.Observer()
    observer = PollingObserver()
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
