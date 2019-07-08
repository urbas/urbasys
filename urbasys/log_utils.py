import logging


def setup_logging(verbose, quiet):
    logging.basicConfig(
        format="[%(levelname)s %(asctime)s|%(filename)s:%(lineno)d] %(message)s",
        level=to_log_level(verbose, quiet),
    )


def to_log_level(verbose, quiet):
    return min(
        max(logging.DEBUG, logging.WARNING - verbose * 10 + quiet * 10),
        logging.CRITICAL,
    )
