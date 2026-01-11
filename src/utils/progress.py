"""
Professional progress bar utilities using tqdm
Provides consistent progress bars across all CLI applications
"""

from typing import Optional, Callable, Iterable, Any
from tqdm import tqdm
import sys


class ProgressBar:
    """
    Unified progress bar wrapper with consistent styling and features

    Features:
    - Automatic ETA calculation
    - Speed/rate display
    - Clean terminal output
    - Nested progress bars support
    - Custom formatting
    """

    def __init__(
        self,
        total: Optional[int] = None,
        desc: str = "Processing",
        unit: str = "item",
        disable: bool = False,
        leave: bool = True,
        position: int = 0,
        colour: Optional[str] = None
    ):
        """
        Initialize progress bar

        Args:
            total: Total number of items (None for unknown)
            desc: Description text
            unit: Unit name (e.g., "file", "document", "item")
            disable: Disable progress bar (for silent mode)
            leave: Keep progress bar after completion
            position: Position for nested bars (0 = top)
            colour: Bar colour (green, blue, red, etc.)
        """
        self.total = total
        self.desc = desc
        self.unit = unit
        self.disable = disable
        self.leave = leave
        self.position = position
        self.colour = colour or "green"
        self.pbar = None

    def __enter__(self):
        """Context manager entry"""
        self.pbar = tqdm(
            total=self.total,
            desc=self.desc,
            unit=self.unit,
            disable=self.disable,
            leave=self.leave,
            position=self.position,
            colour=self.colour,
            file=sys.stdout,
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
        )
        return self.pbar

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.pbar:
            self.pbar.close()
        return False


def progress_iterator(
    iterable: Iterable,
    desc: str = "Processing",
    unit: str = "item",
    total: Optional[int] = None,
    disable: bool = False,
    colour: str = "green"
) -> Iterable:
    """
    Wrap an iterable with a progress bar

    Args:
        iterable: Iterable to wrap
        desc: Description text
        unit: Unit name
        total: Total items (auto-detected if None)
        disable: Disable progress bar
        colour: Bar colour

    Returns:
        Iterator with progress bar

    Example:
        >>> for item in progress_iterator(files, desc="Processing files", unit="file"):
        ...     process(item)
    """
    return tqdm(
        iterable,
        desc=desc,
        unit=unit,
        total=total,
        disable=disable,
        colour=colour,
        file=sys.stdout
    )


def progress_map(
    func: Callable,
    iterable: Iterable,
    desc: str = "Processing",
    unit: str = "item",
    total: Optional[int] = None,
    disable: bool = False,
    colour: str = "green"
) -> list:
    """
    Apply function to iterable with progress bar

    Args:
        func: Function to apply
        iterable: Iterable to process
        desc: Description text
        unit: Unit name
        total: Total items
        disable: Disable progress bar
        colour: Bar colour

    Returns:
        List of results

    Example:
        >>> results = progress_map(process_file, files, desc="Processing", unit="file")
    """
    results = []
    for item in progress_iterator(iterable, desc, unit, total, disable, colour):
        results.append(func(item))
    return results


class MultiProgress:
    """
    Manager for multiple nested progress bars

    Example:
        >>> mp = MultiProgress()
        >>> with mp.add_bar(total=100, desc="Main", position=0) as pbar1:
        ...     for i in range(100):
        ...         with mp.add_bar(total=10, desc=f"Sub-{i}", position=1) as pbar2:
        ...             for j in range(10):
        ...                 pbar2.update(1)
        ...         pbar1.update(1)
    """

    def __init__(self):
        """Initialize multi-progress manager"""
        self.bars = []

    def add_bar(
        self,
        total: Optional[int] = None,
        desc: str = "Processing",
        unit: str = "item",
        position: int = 0,
        colour: str = "green"
    ) -> ProgressBar:
        """
        Add a new progress bar

        Args:
            total: Total items
            desc: Description
            unit: Unit name
            position: Bar position (0=top, 1=nested, etc.)
            colour: Bar colour

        Returns:
            ProgressBar instance
        """
        bar = ProgressBar(
            total=total,
            desc=desc,
            unit=unit,
            position=position,
            colour=colour,
            leave=False
        )
        self.bars.append(bar)
        return bar

    def close_all(self):
        """Close all progress bars"""
        for bar in self.bars:
            if bar.pbar:
                bar.pbar.close()


class FileProgressBar:
    """
    Specialized progress bar for file processing
    Shows file count and total size processed
    """

    def __init__(
        self,
        total_files: int,
        total_size: int = 0,
        desc: str = "Processing files",
        disable: bool = False
    ):
        """
        Initialize file progress bar

        Args:
            total_files: Total number of files
            total_size: Total size in bytes (optional)
            desc: Description
            disable: Disable progress bar
        """
        self.total_files = total_files
        self.total_size = total_size
        self.desc = desc
        self.disable = disable
        self.pbar = None
        self.bytes_processed = 0

    def __enter__(self):
        """Context manager entry"""
        if self.total_size > 0:
            postfix = f"0/{self._format_bytes(self.total_size)}"
        else:
            postfix = ""

        self.pbar = tqdm(
            total=self.total_files,
            desc=self.desc,
            unit="file",
            disable=self.disable,
            colour="blue",
            file=sys.stdout,
            postfix=postfix
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.pbar:
            self.pbar.close()
        return False

    def update(self, n: int = 1, bytes_processed: int = 0):
        """
        Update progress

        Args:
            n: Number of files processed
            bytes_processed: Bytes processed in this update
        """
        if self.pbar:
            self.bytes_processed += bytes_processed

            if self.total_size > 0:
                postfix = f"{self._format_bytes(self.bytes_processed)}/{self._format_bytes(self.total_size)}"
                self.pbar.set_postfix_str(postfix)

            self.pbar.update(n)

    def set_description(self, desc: str):
        """Update description"""
        if self.pbar:
            self.pbar.set_description(desc)

    @staticmethod
    def _format_bytes(bytes_count: int) -> str:
        """Format bytes as human-readable string"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.1f}{unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.1f}PB"


class StepProgress:
    """
    Progress bar for multi-step processes
    Shows current step and overall progress
    """

    def __init__(
        self,
        steps: list,
        desc: str = "Processing",
        disable: bool = False
    ):
        """
        Initialize step progress

        Args:
            steps: List of step names
            desc: Overall description
            disable: Disable progress bar
        """
        self.steps = steps
        self.desc = desc
        self.disable = disable
        self.pbar = None
        self.current_step = 0

    def __enter__(self):
        """Context manager entry"""
        self.pbar = tqdm(
            total=len(self.steps),
            desc=self.desc,
            unit="step",
            disable=self.disable,
            colour="cyan",
            file=sys.stdout
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.pbar:
            self.pbar.close()
        return False

    def next_step(self):
        """Move to next step"""
        if self.pbar and self.current_step < len(self.steps):
            step_name = self.steps[self.current_step]
            self.pbar.set_description(f"{self.desc}: {step_name}")
            self.pbar.update(1)
            self.current_step += 1

    def set_step_status(self, status: str):
        """Update current step status"""
        if self.pbar and self.current_step > 0:
            step_name = self.steps[self.current_step - 1]
            self.pbar.set_description(f"{self.desc}: {step_name} - {status}")


# Convenience functions for common use cases

def create_progress(total: int, desc: str = "Processing", **kwargs) -> tqdm:
    """
    Create a simple progress bar (shorthand)

    Args:
        total: Total items
        desc: Description
        **kwargs: Additional tqdm arguments

    Returns:
        tqdm progress bar
    """
    return tqdm(total=total, desc=desc, file=sys.stdout, **kwargs)


def silent_progress(iterable: Iterable, **kwargs) -> Iterable:
    """
    Return iterable without progress bar (for silent mode)

    Args:
        iterable: Iterable to process
        **kwargs: Ignored

    Returns:
        Original iterable
    """
    return iterable


def get_progress_function(verbose: bool = True):
    """
    Get appropriate progress function based on verbosity

    Args:
        verbose: If True, return progress_iterator, else silent_progress

    Returns:
        Progress function
    """
    return progress_iterator if verbose else silent_progress
