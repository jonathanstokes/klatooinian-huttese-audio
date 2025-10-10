"""
Verbose logging control for Roll20 integration.

This module provides a simple way to control verbose debug output
across the Roll20 integration components.
"""

# Global verbose flag
VERBOSE = False


def set_verbose(enabled: bool) -> None:
    """
    Enable or disable verbose logging.
    
    Args:
        enabled: True to enable verbose output, False to disable
    """
    global VERBOSE
    VERBOSE = enabled


def vprint(*args, **kwargs) -> None:
    """
    Print only if verbose mode is enabled.
    
    Usage: Same as print()
        vprint("Debug message")
        vprint(f"Value: {value}")
    """
    if VERBOSE:
        print(*args, **kwargs)

