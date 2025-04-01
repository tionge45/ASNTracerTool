class NetworkError(Exception):
    """Base class for network-related errors"""
    pass

class CommandNotFoundError(NetworkError):
    """Raised when traceroute command is not found"""
    pass

class HostResolutionError(NetworkError):
    """Raised when hostname cannot be resolved to IP"""
    pass

class InvalidInputError(Exception):
    """Raised when user input is invalid"""
    pass

class ASNLookupError(Exception):
    """Raised when ASN lookup fails"""
    pass