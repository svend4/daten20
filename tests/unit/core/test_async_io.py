"""
Comprehensive tests for core.async_io module
"""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

pytestmark = pytest.mark.unit


class TestAsyncFileReadWrite:
    """Tests for async file read/write operations"""

    @pytest.mark.asyncio
    async def test_read_file_async_text(self, tmp_path):
        """Test reading text file asynchronously"""
        from src.core.async_io import write_file_async, read_file_async

        # Create test file
        test_file = tmp_path / "test.txt"
        content = "Hello, async world!"

        # Write and read
        await write_file_async(str(test_file), content, mode="w")
        result = await read_file_async(str(test_file), mode="r")

        assert result == content

    @pytest.mark.asyncio
    async def test_read_file_async_binary(self, tmp_path):
        """Test reading binary file asynchronously"""
        from src.core.async_io import write_file_async, read_file_async

        test_file = tmp_path / "test.bin"
        content = b"Binary content\x00\x01\x02"

        await write_file_async(str(test_file), content, mode="wb")
        result = await read_file_async(str(test_file), mode="rb")

        assert result == content

    @pytest.mark.asyncio
    async def test_write_file_async_creates_parent_dir(self, tmp_path):
        """Test write_file_async creates parent directories"""
        from src.core.async_io import write_file_async, read_file_async

        test_file = tmp_path / "nested" / "dirs" / "file.txt"
        content = "Content in nested dir"

        bytes_written = await write_file_async(str(test_file), content)

        assert bytes_written == len(content)
        assert test_file.exists()

    @pytest.mark.asyncio
    async def test_append_file_async(self, tmp_path):
        """Test appending to file asynchronously"""
        from src.core.async_io import write_file_async, append_file_async, read_file_async

        test_file = tmp_path / "append.txt"

        await write_file_async(str(test_file), "Line 1\n")
        await append_file_async(str(test_file), "Line 2\n")
        await append_file_async(str(test_file), "Line 3\n")

        content = await read_file_async(str(test_file))
        assert content == "Line 1\nLine 2\nLine 3\n"


class TestAsyncFileStreaming:
    """Tests for async file streaming"""

    @pytest.mark.asyncio
    async def test_stream_file_async(self, tmp_path):
        """Test streaming file in chunks"""
        from src.core.async_io import write_file_async, stream_file_async

        test_file = tmp_path / "large.bin"
        content = b"0123456789" * 1000  # 10KB

        await write_file_async(str(test_file), content, mode="wb")

        chunks = []
        async for chunk in stream_file_async(str(test_file), chunk_size=1024):
            chunks.append(chunk)

        reconstructed = b"".join(chunks)
        assert reconstructed == content
        assert len(chunks) > 1  # Should have multiple chunks

    @pytest.mark.asyncio
    async def test_stream_write_async(self, tmp_path):
        """Test writing from async chunks"""
        from src.core.async_io import stream_write_async, read_file_async

        # Skip if aiofiles not available
        try:
            import aiofiles
        except ImportError:
            pytest.skip("aiofiles not installed")

        test_file = tmp_path / "streamed.bin"

        # Create async chunk generator
        async def chunk_generator():
            for i in range(10):
                await asyncio.sleep(0.01)
                yield f"chunk{i}\n".encode()

        total_bytes = await stream_write_async(str(test_file), chunk_generator())

        assert total_bytes > 0
        assert test_file.exists()


class TestAsyncDirectoryOperations:
    """Tests for async directory operations"""

    @pytest.mark.asyncio
    async def test_makedirs_async(self, tmp_path):
        """Test creating directories asynchronously"""
        from src.core.async_io import makedirs_async, exists_async

        new_dir = tmp_path / "new" / "nested" / "directory"

        await makedirs_async(str(new_dir), exist_ok=True)

        assert await exists_async(str(new_dir))

    @pytest.mark.asyncio
    async def test_makedirs_async_exist_ok(self, tmp_path):
        """Test makedirs_async with exist_ok=True"""
        from src.core.async_io import makedirs_async

        new_dir = tmp_path / "existing"
        new_dir.mkdir()

        # Should not raise error
        await makedirs_async(str(new_dir), exist_ok=True)

    @pytest.mark.asyncio
    async def test_listdir_async(self, tmp_path):
        """Test listing directory contents asynchronously"""
        from src.core.async_io import listdir_async, write_file_async

        # Create test files
        await write_file_async(str(tmp_path / "file1.txt"), "content1")
        await write_file_async(str(tmp_path / "file2.txt"), "content2")
        await write_file_async(str(tmp_path / "file3.txt"), "content3")

        files = await listdir_async(str(tmp_path))

        assert len(files) >= 3
        assert "file1.txt" in files
        assert "file2.txt" in files
        assert "file3.txt" in files

    @pytest.mark.asyncio
    async def test_remove_async(self, tmp_path):
        """Test removing file asynchronously"""
        from src.core.async_io import write_file_async, remove_async, exists_async

        test_file = tmp_path / "to_delete.txt"
        await write_file_async(str(test_file), "content")

        assert await exists_async(str(test_file))

        await remove_async(str(test_file))

        assert not await exists_async(str(test_file))

    @pytest.mark.asyncio
    async def test_exists_async_true(self, tmp_path):
        """Test exists_async returns True for existing file"""
        from src.core.async_io import write_file_async, exists_async

        test_file = tmp_path / "exists.txt"
        await write_file_async(str(test_file), "content")

        assert await exists_async(str(test_file)) is True

    @pytest.mark.asyncio
    async def test_exists_async_false(self, tmp_path):
        """Test exists_async returns False for non-existing file"""
        from src.core.async_io import exists_async

        test_file = tmp_path / "nonexistent.txt"

        assert await exists_async(str(test_file)) is False


class TestAsyncFileUploadDownload:
    """Tests for async file upload/download operations"""

    @pytest.mark.asyncio
    async def test_copy_file_async(self, tmp_path):
        """Test copying file asynchronously"""
        from src.core.async_io import write_file_async, copy_file_async, read_file_async

        src_file = tmp_path / "source.txt"
        dst_file = tmp_path / "destination.txt"
        content = "Content to copy"

        await write_file_async(str(src_file), content)
        await copy_file_async(str(src_file), str(dst_file))

        copied_content = await read_file_async(str(dst_file))
        assert copied_content == content

    @pytest.mark.asyncio
    async def test_save_upload_async(self, tmp_path):
        """Test saving upload asynchronously"""
        from src.core.async_io import save_upload_async, read_file_async

        # Mock upload file
        class MockUploadFile:
            async def read(self, size=-1):
                if not hasattr(self, "_read"):
                    self._read = True
                    return b"Uploaded content"
                return b""

        upload = MockUploadFile()
        destination = tmp_path / "uploaded.bin"

        total_bytes = await save_upload_async(upload, str(destination))

        assert total_bytes > 0
        assert destination.exists()


class TestUtilityFunctions:
    """Tests for utility functions"""

    @pytest.mark.asyncio
    async def test_get_file_size_async(self, tmp_path):
        """Test getting file size asynchronously"""
        from src.core.async_io import write_file_async, get_file_size_async

        test_file = tmp_path / "size_test.txt"
        content = "A" * 1000  # 1000 bytes

        await write_file_async(str(test_file), content)

        size = await get_file_size_async(str(test_file))
        assert size == 1000

    @pytest.mark.asyncio
    async def test_ensure_dir_async_creates(self, tmp_path):
        """Test ensure_dir_async creates directory"""
        from src.core.async_io import ensure_dir_async, exists_async

        new_dir = tmp_path / "ensured"

        assert not await exists_async(str(new_dir))

        await ensure_dir_async(str(new_dir))

        assert await exists_async(str(new_dir))

    @pytest.mark.asyncio
    async def test_ensure_dir_async_exists(self, tmp_path):
        """Test ensure_dir_async with existing directory"""
        from src.core.async_io import ensure_dir_async, exists_async

        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()

        # Should not raise error
        await ensure_dir_async(str(existing_dir))

        assert await exists_async(str(existing_dir))


class TestFallbackBehavior:
    """Tests for fallback behavior when aiofiles not available"""

    @pytest.mark.asyncio
    @patch("src.core.async_io.AIOFILES_AVAILABLE", False)
    async def test_read_file_async_fallback(self, tmp_path):
        """Test read_file_async falls back to sync when aiofiles unavailable"""
        from src.core.async_io import read_file_async

        test_file = tmp_path / "fallback.txt"
        test_file.write_text("Fallback content")

        content = await read_file_async(str(test_file))
        assert content == "Fallback content"

    @pytest.mark.asyncio
    @patch("src.core.async_io.AIOFILES_AVAILABLE", False)
    async def test_write_file_async_fallback(self, tmp_path):
        """Test write_file_async falls back to sync"""
        from src.core.async_io import write_file_async

        test_file = tmp_path / "fallback_write.txt"
        content = "Sync fallback write"

        bytes_written = await write_file_async(str(test_file), content)

        assert bytes_written == len(content)
        assert test_file.read_text() == content


class TestEdgeCases:
    """Tests for edge cases and error handling"""

    @pytest.mark.asyncio
    async def test_read_file_async_nonexistent(self):
        """Test reading non-existent file raises error"""
        from src.core.async_io import read_file_async

        with pytest.raises(FileNotFoundError):
            await read_file_async("/nonexistent/path/file.txt")

    @pytest.mark.asyncio
    async def test_write_file_async_empty_content(self, tmp_path):
        """Test writing empty content"""
        from src.core.async_io import write_file_async, read_file_async

        test_file = tmp_path / "empty.txt"

        bytes_written = await write_file_async(str(test_file), "")
        assert bytes_written == 0

        content = await read_file_async(str(test_file))
        assert content == ""

    @pytest.mark.asyncio
    async def test_stream_file_async_empty_file(self, tmp_path):
        """Test streaming empty file"""
        from src.core.async_io import write_file_async, stream_file_async

        test_file = tmp_path / "empty.bin"
        await write_file_async(str(test_file), b"", mode="wb")

        chunks = []
        async for chunk in stream_file_async(str(test_file)):
            chunks.append(chunk)

        assert len(chunks) == 0
