import logging

from urbasys.log_utils import to_log_level


def test_to_log_level_default():
    assert logging.WARNING == to_log_level(verbose=0, quiet=0)


def test_to_log_level_verbose():
    assert logging.INFO == to_log_level(verbose=1, quiet=0)


def test_to_log_level_max_verbose():
    assert logging.DEBUG == to_log_level(verbose=9001, quiet=0)


def test_to_log_level_quiet():
    assert logging.ERROR == to_log_level(verbose=0, quiet=1)


def test_to_log_level_max_quiet():
    assert logging.FATAL == to_log_level(verbose=0, quiet=9001)
