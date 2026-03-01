def close_default_connection() -> None:
    """
    Close the default Django DB connection.

    Useful in multi-threaded tests: Django connections are not thread-safe to
    reuse across threads, and pytest may warn about unhandled thread exceptions
    if a thread keeps an open connection.
    """
    from django.db import connections

    connections["default"].close()
