"""Application-wide rate limiter (slowapi).

Import ``limiter`` and apply it per-route with ``@limiter.limit("5/minute")``.
The limiter is wired into the app (state + exception handler) in ``app.main``.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
