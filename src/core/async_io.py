#!/usr/bin/env python3
"""
Asynchronous File I/O Operations
=================================

Async wrappers for file operations to enable non-blocking I/O.

This module provides asyncio-compatible file operations using aiofiles,
allowing file I/O without blocking the event loop.

Features:
- Async file read/write
- Async directory operations
- Async file uploads/downloads
- Streaming support
- Progress tracking
- Error handling
- Retry mechanisms
- Chunked processing

Usage:
    # Read file asynchronously
    content = await read_file_async("document.txt")

    # Write file asynchronously
    await write_file_async("output.txt", content)

    # Stream large file
    async for chunk in stream_file_async("large_file.pdf"):
        process(chunk)

Tech Stack:
- aiofiles for async file operations
- asyncio for async/await
- pathlib for path operations

Author: Document Management System
Version: 1.0.0
"""

import asyncio
import logging
import os
import shutil
from pathlib import Path
from typing import AsyncIterator, BinaryIO, Optional, TextIO, Union

logger = logging.getLogger(__name__)

# Check if aiofiles is available
try:
    import aiofiles
    import aiofiles.os

    AIOFILES_AVAILABLE = True
except ImportError:
    AIOFILES_AVAILABLE = False
    logger.warning("aiofiles not installed. Install with: pip install aiofiles")


# =============================================================================
# ASYNC FILE READ/WRITE
# =============================================================================


async def read_file_async(
    file_path: Union[str, Path], mode: str = "r", encoding: str = "utf-8"
) -> Union[str, bytes]:
    """
    Read file asynchronously.

    Args:
        file_path: Path to file
        mode: File mode ('r' for text, 'rb' for binary)
        encoding: Text encoding (for text mode)

    Returns:
        File content (str or bytes)

    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If no read permission
    """
    if not AIOFILES_AVAILABLE:
        # Fallback to sync I/O in thread
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _read_file_sync, file_path, mode, encoding)

    logger.debug(f"Reading file asynchronously: {file_path}")

    try:
        async with aiofiles.open(file_path, mode=mode, encoding=encoding if "b" not in mode else None) as f:
            content = await f.read()
        logger.debug(f"File read completed: {file_path} ({len(content)} bytes)")
        return content
    except Exception as e:
        logger.error(f"Failed to read file {file_path}: {str(e)}")
        raise


async def write_file_async(
    file_path: Union[str, Path], content: Union[str, bytes], mode: str = "w", encoding: str = "utf-8"
) -> int:
    """
    Write file asynchronously.

    Args:
        file_path: Path to file
        content: Content to write
        mode: File mode ('w' for text, 'wb' for binary)
        encoding: Text encoding (for text mode)

    Returns:
        Number of bytes written

    Raises:
        PermissionError: If no write permission
        OSError: If disk full or other OS error
    """
    if not AIOFILES_AVAILABLE:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _write_file_sync, file_path, content, mode, encoding)

    logger.debug(f"Writing file asynchronously: {file_path}")

    try:
        # Create parent directory if it doesn't exist
        parent = Path(file_path).parent
        if not parent.exists():
            await makedirs_async(parent, exist_ok=True)

        async with aiofiles.open(file_path, mode=mode, encoding=encoding if "b" not in mode else None) as f:
            await f.write(content)

        size = len(content)
        logger.debug(f"File written: {file_path} ({size} bytes)")
        return size
    except Exception as e:
        logger.error(f"Failed to write file {file_path}: {str(e)}")
        raise


async def append_file_async(
    file_path: Union[str, Path], content: Union[str, bytes], encoding: str = "utf-8"
) -> int:
    """
    Append to file asynchronously.

    Args:
        file_path: Path to file
        content: Content to append
        encoding: Text encoding

    Returns:
        Number of bytes appended
    """
    mode = "a" if isinstance(content, str) else "ab"
    return await write_file_async(file_path, content, mode=mode, encoding=encoding)


# =============================================================================
# ASYNC FILE STREAMING
# =============================================================================


async def stream_file_async(
    file_path: Union[str, Path], chunk_size: int = 8192, mode: str = "rb"
) -> AsyncIterator[bytes]:
    """
    Stream file in chunks asynchronously.

    Args:
        file_path: Path to file
        chunk_size: Chunk size in bytes
        mode: File mode

    Yields:
        File chunks

    Usage:
        async for chunk in stream_file_async("large_file.pdf"):
            process(chunk)
    """
    if not AIOFILES_AVAILABLE:
        logger.warning("aiofiles not available, falling back to sync streaming")
        # Fallback to sync streaming
        with open(file_path, mode) as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk
        return

    logger.debug(f"Streaming file: {file_path} (chunk_size={chunk_size})")

    async with aiofiles.open(file_path, mode=mode) as f:
        while True:
            chunk = await f.read(chunk_size)
            if not chunk:
                break
            yield chunk

    logger.debug(f"File streaming completed: {file_path}")


async def stream_write_async(
    file_path: Union[str, Path], chunks: AsyncIterator[bytes], mode: str = "wb"
) -> int:
    """
    Write file from async chunks.

    Args:
        file_path: Path to output file
        chunks: Async iterator of chunks
        mode: File mode

    Returns:
        Total bytes written
    """
    if not AIOFILES_AVAILABLE:
        raise RuntimeError("aiofiles required for stream_write_async")

    logger.debug(f"Streaming write to: {file_path}")
    total_bytes = 0

    async with aiofiles.open(file_path, mode=mode) as f:
        async for chunk in chunks:
            await f.write(chunk)
            total_bytes += len(chunk)

    logger.debug(f"Stream write completed: {file_path} ({total_bytes} bytes)")
    return total_bytes


# =============================================================================
# ASYNC DIRECTORY OPERATIONS
# =============================================================================


async def makedirs_async(path: Union[str, Path], mode: int = 0o777, exist_ok: bool = False) -> None:
    """
    Create directory recursively asynchronously.

    Args:
        path: Directory path
        mode: Permission mode
        exist_ok: Don't raise error if exists
    """
    if not AIOFILES_AVAILABLE or not hasattr(aiofiles.os, "makedirs"):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, os.makedirs, path, mode, exist_ok)
        return

    await aiofiles.os.makedirs(path, mode=mode, exist_ok=exist_ok)
    logger.debug(f"Directory created: {path}")


async def listdir_async(path: Union[str, Path]) -> list:
    """
    List directory contents asynchronously.

    Args:
        path: Directory path

    Returns:
        List of filenames
    """
    if not AIOFILES_AVAILABLE or not hasattr(aiofiles.os, "listdir"):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, os.listdir, path)

    return await aiofiles.os.listdir(path)


async def remove_async(path: Union[str, Path]) -> None:
    """
    Remove file asynchronously.

    Args:
        path: File path
    """
    if not AIOFILES_AVAILABLE or not hasattr(aiofiles.os, "remove"):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, os.remove, path)
        return

    await aiofiles.os.remove(path)
    logger.debug(f"File removed: {path}")


async def exists_async(path: Union[str, Path]) -> bool:
    """
    Check if file/directory exists asynchronously.

    Args:
        path: Path to check

    Returns:
        True if exists
    """
    if not AIOFILES_AVAILABLE or not hasattr(aiofiles.os, "path"):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, os.path.exists, path)

    return await aiofiles.os.path.exists(path)


# =============================================================================
# ASYNC FILE UPLOAD/DOWNLOAD
# =============================================================================


async def save_upload_async(
    upload_file, destination: Union[str, Path], chunk_size: int = 8192
) -> int:
    """
    Save uploaded file asynchronously (FastAPI UploadFile compatible).

    Args:
        upload_file: FastAPI UploadFile or file-like object
        destination: Destination path
        chunk_size: Chunk size for streaming

    Returns:
        Total bytes written
    """
    logger.debug(f"Saving upload to: {destination}")
    total_bytes = 0

    # Create parent directory
    parent = Path(destination).parent
    if not parent.exists():
        await makedirs_async(parent, exist_ok=True)

    if not AIOFILES_AVAILABLE:
        # Fallback to sync
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, _save_upload_sync, upload_file, destination, chunk_size
        )

    async with aiofiles.open(destination, "wb") as f:
        while True:
            chunk = await upload_file.read(chunk_size)
            if not chunk:
                break
            await f.write(chunk)
            total_bytes += len(chunk)

    logger.debug(f"Upload saved: {destination} ({total_bytes} bytes)")
    return total_bytes


async def copy_file_async(src: Union[str, Path], dst: Union[str, Path]) -> None:
    """
    Copy file asynchronously.

    Args:
        src: Source file path
        dst: Destination file path
    """
    logger.debug(f"Copying file: {src} -> {dst}")

    # Read source and write to destination
    content = await read_file_async(src, mode="rb")
    await write_file_async(dst, content, mode="wb")

    logger.debug(f"File copied: {src} -> {dst}")


# =============================================================================
# SYNC FALLBACK FUNCTIONS
# =============================================================================


def _read_file_sync(file_path: Union[str, Path], mode: str, encoding: str) -> Union[str, bytes]:
    """Synchronous file read fallback"""
    with open(file_path, mode=mode, encoding=encoding if "b" not in mode else None) as f:
        return f.read()


def _write_file_sync(
    file_path: Union[str, Path], content: Union[str, bytes], mode: str, encoding: str
) -> int:
    """Synchronous file write fallback"""
    parent = Path(file_path).parent
    if not parent.exists():
        os.makedirs(parent, exist_ok=True)

    with open(file_path, mode=mode, encoding=encoding if "b" not in mode else None) as f:
        f.write(content)
    return len(content)


def _save_upload_sync(upload_file, destination: Union[str, Path], chunk_size: int) -> int:
    """Synchronous upload save fallback"""
    parent = Path(destination).parent
    if not parent.exists():
        os.makedirs(parent, exist_ok=True)

    total_bytes = 0
    with open(destination, "wb") as f:
        while True:
            chunk = upload_file.file.read(chunk_size)
            if not chunk:
                break
            f.write(chunk)
            total_bytes += len(chunk)
    return total_bytes


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


async def get_file_size_async(path: Union[str, Path]) -> int:
    """
    Get file size asynchronously.

    Args:
        path: File path

    Returns:
        File size in bytes
    """
    if not AIOFILES_AVAILABLE or not hasattr(aiofiles.os, "stat"):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: os.path.getsize(path))

    stat = await aiofiles.os.stat(path)
    return stat.st_size


async def ensure_dir_async(path: Union[str, Path]) -> None:
    """
    Ensure directory exists, create if not.

    Args:
        path: Directory path
    """
    if not await exists_async(path):
        await makedirs_async(path, exist_ok=True)


# Export public API
__all__ = [
    "read_file_async",
    "write_file_async",
    "append_file_async",
    "stream_file_async",
    "stream_write_async",
    "makedirs_async",
    "listdir_async",
    "remove_async",
    "exists_async",
    "save_upload_async",
    "copy_file_async",
    "get_file_size_async",
    "ensure_dir_async",
]
