"""Profiling utilities for measuring performance in notebooks."""

import functools
import gc
import time
from typing import Any, Callable, TypeVar

import psutil

T = TypeVar("T")


def format_size(size_in_bytes: float) -> str:
    """Convert size in bytes to human readable format.

    Args:
        size_in_bytes: Size in bytes to format

    Returns:
        str: Formatted size with appropriate unit (B, KB, MB, GB)
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024
    return f"{size_in_bytes:.2f} GB"


def measure_read_time(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to measure execution time and memory usage of a function.

    Args:
        func: The function to measure

    Returns:
        Wrapped function that prints timing and memory usage information
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        # Clear memory and garbage collect
        gc.collect()
        process = psutil.Process()

        # Measure initial memory
        start_mem = process.memory_info().rss

        # Time the operation
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        # Measure final memory
        end_mem = process.memory_info().rss

        # Print results once
        print(f"Time taken: {(end_time - start_time):.3f} seconds")
        print(f"Memory usage: {format_size(end_mem - start_mem)}")

        return result

    return wrapper
