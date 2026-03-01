"""
Project domain exceptions.

They are intentionally framework-agnostic and must be translated into HTTP
responses at the API adapter layer (api.v1.projects).
"""


class InvalidTaskStatus(Exception):
    """
    Raised when a client attempts to transition a task to an invalid status.
    """

    pass


class TaskConcurrencyError(Exception):
    """
    Raised when a task status transition conflicts with another in-flight
    transition.
    """

    pass
