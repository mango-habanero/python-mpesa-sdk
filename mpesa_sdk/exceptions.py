"""This module contains the exceptions used in the SDK."""


class AuthError(Exception):
    """Raised when a high-level error occurs in the auth server."""


class EncodingError(Exception):
    """Raised when an error occurs in the system's encoding patterns."""


class AuthenticationError(Exception):
    """Raised when an attempt to retrieve an external authentication token fails."""


class NoResponse(Exception):
    """Raised when an expected response object is not returned or resolves to None."""


class UnsupportedMethodError(Exception):
    """Raised when the method passed to the make request function is unsupported."""
