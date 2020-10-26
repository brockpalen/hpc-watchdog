"""Parse and handle cli args."""
import argparse

from environs import Env

from .log import logger

# load in config from .env
env = Env()

# can't load breaks singularity
# env.read_env()  # read .env file, if it exists


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

        globus = self.parser.add_argument_group(
            title="Globus Transfer Options",
            description="Options to setup transfer of data",
        )
        source_default = env.str("WD_SOURCE", default=None)
        globus.add_argument(
            "--source",
            help=f"Source endpoint/collection Default: {source_default}",
            default=source_default,
        )

        dest_default = env.str("WD_DESTINATION", default="umich#flux")
        globus.add_argument(
            "--destination",
            help=f"Destination endpoint/collection Default: {dest_default}",
            default=dest_default,
        )
        dest_path = env.str("WD_DESTINATION_PATH", default=None)
        globus.add_argument(
            "--destination-dir",
            help="Directory on Destination server",
            required=True,
            default=dest_path,
        )
        globus.add_argument(
            "--globus-verbose",
            help="Globus Verbose Logging",
            action="store_true",
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
        logger.info(
            f"Source Server: {self.source} Destination Server: {self.destination} (Personal if None)"
        )
        logger.info(f"Destination Path: {self.destination_dir}")
