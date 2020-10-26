"""Parse and handle cli args."""
import argparse

from .log import logger


class Args:
    """Arg parser class."""

    def __init__(self, args):
        """CLI options."""
        self.parser = argparse.ArgumentParser(
            description="Drain Directory continously",
            epilog="Brock Palen brockp@umich.edu",
        )

        self.parser.add_argument(
            "-p",
            "--path",
            help="Path to monitor for new files",
            type=str,
            required=True,
        )
        self.parser.add_argument(
            "--sleep",
            help="Interval (sec) before checking creation of new Globus Transfer and Deletes Default 900 seconds",
            type=int,
            default=15 * 60,
        )
        self.parser.add_argument(
            "--dwell-time",
            help="Interval (sec) with no file updates before submitting for transfer, Default 600 seconds",
            type=int,
            default=10 * 60,
        )

        self.args = self.parser.parse_args(args)

        #  push the argparser args onto the main object
        for key, value in vars(self.args).items():
            setattr(self, key, value)

    def log_settings(self):
        """Log to handlers common settings."""
        logger.info(f"Will monitor path {self.path}")
        logger.info(f"Will sleep for {self.sleep} seconds between iterations")
        logger.info(
            f"Files must not be modified for {self.dwell_time} seconds before becoming candidates"
        )
