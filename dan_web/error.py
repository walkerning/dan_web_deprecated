# -*- coding: utf-8 -*-
"""
Exceptions of Dan Web"""

class DanWebError(Exception):
    """
    Dan web internal error!"""

class ExpectedException(Exception):
    """
    Intentionally raised exceptions.
    Will be catched by the web site outter logic,
    and feedback to user when appropriate."""

class AdapterException(ExpectedException):
    """
    Adapter Exception"""

class ConfigException(ExpectedException):
    """
    Config Exception"""

class RunnerException(ExpectedException):
    """
    Job runner exception"""

class ConstraintException(ExpectedException):
    """
    Raised when an operation violate a constraint.
    Such as how many files a user can upload,
    how many jobs can be running at the same time."""
