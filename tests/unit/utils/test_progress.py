"""
Comprehensive tests for progress bar utilities

Tests professional progress bar wrappers including ProgressBar,
MultiProgress, FileProgressBar, StepProgress and utility functions.

Session 26 - 65+ tests
"""

import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

# Mock tqdm before importing progress module
mock_tqdm = Mock()
mock_tqdm_class = MagicMock()
mock_tqdm_class.return_value = mock_tqdm
sys.modules["tqdm"] = Mock(tqdm=mock_tqdm_class)

from src.utils.progress import (
    FileProgressBar,
    MultiProgress,
    ProgressBar,
    StepProgress,
    create_progress,
    get_progress_function,
    progress_iterator,
    progress_map,
    silent_progress,
)


@pytest.fixture
def mock_tqdm_instance():
    """Create a mock tqdm instance"""
    mock = Mock()
    mock.update = Mock()
    mock.close = Mock()
    mock.set_description = Mock()
    mock.set_postfix_str = Mock()
    return mock


class TestProgressBar:
    """Test ProgressBar class"""

    def test_progress_bar_class_exists(self):
        """Test ProgressBar class exists"""
        assert ProgressBar is not None

    def test_progress_bar_initialization_defaults(self):
        """Test ProgressBar initialization with defaults"""
        pbar = ProgressBar()
        assert pbar.desc == "Processing"
        assert pbar.unit == "item"
        assert pbar.disable is False
        assert pbar.leave is True
        assert pbar.position == 0
        assert pbar.colour == "green"

    def test_progress_bar_initialization_custom(self):
        """Test ProgressBar initialization with custom parameters"""
        pbar = ProgressBar(total=100, desc="Custom", unit="file", disable=True, leave=False, position=1, colour="blue")
        assert pbar.total == 100
        assert pbar.desc == "Custom"
        assert pbar.unit == "file"
        assert pbar.disable is True
        assert pbar.leave is False
        assert pbar.position == 1
        assert pbar.colour == "blue"

    def test_progress_bar_default_colour_green(self):
        """Test ProgressBar defaults to green colour"""
        pbar = ProgressBar()
        assert pbar.colour == "green"

    def test_progress_bar_initial_pbar_none(self):
        """Test ProgressBar pbar is None initially"""
        pbar = ProgressBar()
        assert pbar.pbar is None

    @patch("src.utils.progress.tqdm")
    def test_progress_bar_context_manager_enter(self, mock_tqdm_cls, mock_tqdm_instance):
        """Test ProgressBar context manager __enter__"""
        mock_tqdm_cls.return_value = mock_tqdm_instance

        pbar = ProgressBar(total=100, desc="Test")
        with pbar as p:
            assert p == mock_tqdm_instance
            assert pbar.pbar == mock_tqdm_instance

    @patch("src.utils.progress.tqdm")
    def test_progress_bar_context_manager_exit(self, mock_tqdm_cls, mock_tqdm_instance):
        """Test ProgressBar context manager __exit__"""
        mock_tqdm_cls.return_value = mock_tqdm_instance

        pbar = ProgressBar()
        with pbar:
            pass

        mock_tqdm_instance.close.assert_called_once()

    @patch("src.utils.progress.tqdm")
    def test_progress_bar_calls_tqdm_with_correct_params(self, mock_tqdm_cls, mock_tqdm_instance):
        """Test ProgressBar calls tqdm with correct parameters"""
        mock_tqdm_cls.return_value = mock_tqdm_instance

        pbar = ProgressBar(total=50, desc="Test", unit="test", disable=False, leave=True, position=0, colour="red")
        with pbar:
            pass

        mock_tqdm_cls.assert_called_once()
        call_kwargs = mock_tqdm_cls.call_args[1]
        assert call_kwargs["total"] == 50
        assert call_kwargs["desc"] == "Test"
        assert call_kwargs["unit"] == "test"
        assert call_kwargs["disable"] is False
        assert call_kwargs["leave"] is True
        assert call_kwargs["position"] == 0
        assert call_kwargs["colour"] == "red"

    @patch("src.utils.progress.tqdm")
    def test_progress_bar_returns_false_from_exit(self, mock_tqdm_cls, mock_tqdm_instance):
        """Test ProgressBar __exit__ returns False"""
        mock_tqdm_cls.return_value = mock_tqdm_instance

        pbar = ProgressBar()
        result = pbar.__exit__(None, None, None)
        assert result is False


class TestProgressIterator:
    """Test progress_iterator function"""

    def test_progress_iterator_function_exists(self):
        """Test progress_iterator function exists"""
        assert progress_iterator is not None
        assert callable(progress_iterator)

    @patch("src.utils.progress.tqdm")
    def test_progress_iterator_returns_tqdm(self, mock_tqdm_cls):
        """Test progress_iterator returns tqdm instance"""
        mock_instance = Mock()
        mock_tqdm_cls.return_value = mock_instance

        iterable = [1, 2, 3]
        result = progress_iterator(iterable)

        assert result == mock_instance

    @patch("src.utils.progress.tqdm")
    def test_progress_iterator_with_defaults(self, mock_tqdm_cls):
        """Test progress_iterator with default parameters"""
        iterable = [1, 2, 3]
        progress_iterator(iterable)

        mock_tqdm_cls.assert_called_once()
        args, kwargs = mock_tqdm_cls.call_args
        assert args[0] == iterable
        assert kwargs["desc"] == "Processing"
        assert kwargs["unit"] == "item"
        assert kwargs["colour"] == "green"

    @patch("src.utils.progress.tqdm")
    def test_progress_iterator_with_custom_params(self, mock_tqdm_cls):
        """Test progress_iterator with custom parameters"""
        iterable = [1, 2, 3]
        progress_iterator(iterable, desc="Custom", unit="file", total=10, disable=True, colour="blue")

        args, kwargs = mock_tqdm_cls.call_args
        assert kwargs["desc"] == "Custom"
        assert kwargs["unit"] == "file"
        assert kwargs["total"] == 10
        assert kwargs["disable"] is True
        assert kwargs["colour"] == "blue"


class TestProgressMap:
    """Test progress_map function"""

    def test_progress_map_function_exists(self):
        """Test progress_map function exists"""
        assert progress_map is not None
        assert callable(progress_map)

    @patch("src.utils.progress.progress_iterator")
    def test_progress_map_applies_function(self, mock_iter):
        """Test progress_map applies function to all items"""
        items = [1, 2, 3]
        mock_iter.return_value = items

        def double(x):
            return x * 2

        result = progress_map(double, items)

        assert result == [2, 4, 6]

    @patch("src.utils.progress.progress_iterator")
    def test_progress_map_passes_params_to_iterator(self, mock_iter):
        """Test progress_map passes parameters to progress_iterator"""
        items = [1, 2, 3]
        mock_iter.return_value = items

        def identity(x):
            return x

        progress_map(identity, items, desc="Test", unit="num", total=5, disable=True, colour="red")

        mock_iter.assert_called_once_with(items, "Test", "num", 5, True, "red")

    @patch("src.utils.progress.progress_iterator")
    def test_progress_map_returns_list(self, mock_iter):
        """Test progress_map returns list"""
        items = [1, 2, 3]
        mock_iter.return_value = items

        result = progress_map(lambda x: x, items)

        assert isinstance(result, list)
        assert len(result) == 3


class TestMultiProgress:
    """Test MultiProgress class"""

    def test_multi_progress_class_exists(self):
        """Test MultiProgress class exists"""
        assert MultiProgress is not None

    def test_multi_progress_initialization(self):
        """Test MultiProgress initialization"""
        mp = MultiProgress()
        assert mp.bars == []

    def test_add_bar_creates_progress_bar(self):
        """Test add_bar creates ProgressBar instance"""
        mp = MultiProgress()
        bar = mp.add_bar(total=100)

        assert isinstance(bar, ProgressBar)
        assert bar in mp.bars

    def test_add_bar_with_custom_params(self):
        """Test add_bar with custom parameters"""
        mp = MultiProgress()
        bar = mp.add_bar(total=50, desc="Custom", unit="file", position=1, colour="blue")

        assert bar.total == 50
        assert bar.desc == "Custom"
        assert bar.unit == "file"
        assert bar.position == 1
        assert bar.colour == "blue"

    def test_add_bar_sets_leave_false(self):
        """Test add_bar sets leave=False"""
        mp = MultiProgress()
        bar = mp.add_bar()

        assert bar.leave is False

    def test_add_multiple_bars(self):
        """Test adding multiple bars"""
        mp = MultiProgress()
        bar1 = mp.add_bar(desc="Bar1")
        bar2 = mp.add_bar(desc="Bar2")
        bar3 = mp.add_bar(desc="Bar3")

        assert len(mp.bars) == 3
        assert bar1 in mp.bars
        assert bar2 in mp.bars
        assert bar3 in mp.bars

    def test_close_all_closes_all_bars(self):
        """Test close_all closes all progress bars"""
        mp = MultiProgress()

        # Add bars with mock pbar
        for i in range(3):
            bar = mp.add_bar()
            bar.pbar = Mock()

        mp.close_all()

        for bar in mp.bars:
            bar.pbar.close.assert_called_once()

    def test_close_all_handles_none_pbar(self):
        """Test close_all handles bars with None pbar"""
        mp = MultiProgress()
        bar1 = mp.add_bar()
        bar2 = mp.add_bar()
        bar1.pbar = Mock()
        bar2.pbar = None

        # Should not raise error
        mp.close_all()

        bar1.pbar.close.assert_called_once()


class TestFileProgressBar:
    """Test FileProgressBar class"""

    def test_file_progress_bar_class_exists(self):
        """Test FileProgressBar class exists"""
        assert FileProgressBar is not None

    def test_file_progress_bar_initialization(self):
        """Test FileProgressBar initialization"""
        fpb = FileProgressBar(total_files=10, total_size=1024, desc="Files", disable=False)

        assert fpb.total_files == 10
        assert fpb.total_size == 1024
        assert fpb.desc == "Files"
        assert fpb.disable is False
        assert fpb.pbar is None
        assert fpb.bytes_processed == 0

    def test_file_progress_bar_default_size_zero(self):
        """Test FileProgressBar defaults total_size to 0"""
        fpb = FileProgressBar(total_files=5)
        assert fpb.total_size == 0

    @patch("src.utils.progress.tqdm")
    def test_file_progress_bar_context_manager(self, mock_tqdm_cls, mock_tqdm_instance):
        """Test FileProgressBar context manager"""
        mock_tqdm_cls.return_value = mock_tqdm_instance

        fpb = FileProgressBar(total_files=5)
        with fpb as bar:
            assert bar == fpb
            assert fpb.pbar == mock_tqdm_instance

        mock_tqdm_instance.close.assert_called_once()

    @patch("src.utils.progress.tqdm")
    def test_file_progress_bar_update(self, mock_tqdm_cls, mock_tqdm_instance):
        """Test FileProgressBar update method"""
        mock_tqdm_cls.return_value = mock_tqdm_instance

        fpb = FileProgressBar(total_files=5, total_size=1000)
        with fpb:
            fpb.update(n=1, bytes_processed=100)

        assert fpb.bytes_processed == 100
        mock_tqdm_instance.update.assert_called_once_with(1)

    @patch("src.utils.progress.tqdm")
    def test_file_progress_bar_update_multiple_times(self, mock_tqdm_cls, mock_tqdm_instance):
        """Test FileProgressBar update accumulates bytes"""
        mock_tqdm_cls.return_value = mock_tqdm_instance

        fpb = FileProgressBar(total_files=3, total_size=1000)
        with fpb:
            fpb.update(n=1, bytes_processed=100)
            fpb.update(n=1, bytes_processed=200)
            fpb.update(n=1, bytes_processed=300)

        assert fpb.bytes_processed == 600

    @patch("src.utils.progress.tqdm")
    def test_file_progress_bar_set_description(self, mock_tqdm_cls, mock_tqdm_instance):
        """Test FileProgressBar set_description method"""
        mock_tqdm_cls.return_value = mock_tqdm_instance

        fpb = FileProgressBar(total_files=5)
        with fpb:
            fpb.set_description("New description")

        mock_tqdm_instance.set_description.assert_called_once_with("New description")

    def test_file_progress_bar_format_bytes(self):
        """Test FileProgressBar _format_bytes static method"""
        assert FileProgressBar._format_bytes(0) == "0.0B"
        assert FileProgressBar._format_bytes(500) == "500.0B"
        assert FileProgressBar._format_bytes(1024) == "1.0KB"
        assert FileProgressBar._format_bytes(1536) == "1.5KB"
        assert FileProgressBar._format_bytes(1024 * 1024) == "1.0MB"
        assert FileProgressBar._format_bytes(1024 * 1024 * 1024) == "1.0GB"
        assert FileProgressBar._format_bytes(1024 * 1024 * 1024 * 1024) == "1.0TB"

    def test_file_progress_bar_format_bytes_large_values(self):
        """Test FileProgressBar _format_bytes with very large values"""
        result = FileProgressBar._format_bytes(1024 ** 5)
        assert result.endswith("PB")


class TestStepProgress:
    """Test StepProgress class"""

    def test_step_progress_class_exists(self):
        """Test StepProgress class exists"""
        assert StepProgress is not None

    def test_step_progress_initialization(self):
        """Test StepProgress initialization"""
        steps = ["Step 1", "Step 2", "Step 3"]
        sp = StepProgress(steps, desc="Process", disable=False)

        assert sp.steps == steps
        assert sp.desc == "Process"
        assert sp.disable is False
        assert sp.pbar is None
        assert sp.current_step == 0

    def test_step_progress_default_desc(self):
        """Test StepProgress defaults desc to 'Processing'"""
        sp = StepProgress(["Step 1"])
        assert sp.desc == "Processing"

    @patch("src.utils.progress.tqdm")
    def test_step_progress_context_manager(self, mock_tqdm_cls, mock_tqdm_instance):
        """Test StepProgress context manager"""
        mock_tqdm_cls.return_value = mock_tqdm_instance

        steps = ["Step 1", "Step 2"]
        sp = StepProgress(steps)

        with sp as s:
            assert s == sp
            assert sp.pbar == mock_tqdm_instance

        mock_tqdm_instance.close.assert_called_once()

    @patch("src.utils.progress.tqdm")
    def test_step_progress_next_step(self, mock_tqdm_cls, mock_tqdm_instance):
        """Test StepProgress next_step method"""
        mock_tqdm_cls.return_value = mock_tqdm_instance

        steps = ["Step 1", "Step 2", "Step 3"]
        sp = StepProgress(steps)

        with sp:
            sp.next_step()

        assert sp.current_step == 1
        mock_tqdm_instance.set_description.assert_called()
        mock_tqdm_instance.update.assert_called_with(1)

    @patch("src.utils.progress.tqdm")
    def test_step_progress_multiple_next_steps(self, mock_tqdm_cls, mock_tqdm_instance):
        """Test StepProgress multiple next_step calls"""
        mock_tqdm_cls.return_value = mock_tqdm_instance

        steps = ["Step 1", "Step 2", "Step 3"]
        sp = StepProgress(steps)

        with sp:
            sp.next_step()
            sp.next_step()
            sp.next_step()

        assert sp.current_step == 3
        assert mock_tqdm_instance.update.call_count == 3

    @patch("src.utils.progress.tqdm")
    def test_step_progress_set_step_status(self, mock_tqdm_cls, mock_tqdm_instance):
        """Test StepProgress set_step_status method"""
        mock_tqdm_cls.return_value = mock_tqdm_instance

        steps = ["Step 1", "Step 2"]
        sp = StepProgress(steps)

        with sp:
            sp.next_step()
            sp.set_step_status("Complete")

        calls = mock_tqdm_instance.set_description.call_args_list
        # Last call should include status
        assert "Complete" in calls[-1][0][0]

    @patch("src.utils.progress.tqdm")
    def test_step_progress_calls_tqdm_with_cyan(self, mock_tqdm_cls, mock_tqdm_instance):
        """Test StepProgress calls tqdm with cyan colour"""
        mock_tqdm_cls.return_value = mock_tqdm_instance

        steps = ["Step 1"]
        sp = StepProgress(steps)

        with sp:
            pass

        call_kwargs = mock_tqdm_cls.call_args[1]
        assert call_kwargs["colour"] == "cyan"


class TestCreateProgress:
    """Test create_progress convenience function"""

    def test_create_progress_function_exists(self):
        """Test create_progress function exists"""
        assert create_progress is not None
        assert callable(create_progress)

    @patch("src.utils.progress.tqdm")
    def test_create_progress_returns_tqdm(self, mock_tqdm_cls):
        """Test create_progress returns tqdm instance"""
        mock_instance = Mock()
        mock_tqdm_cls.return_value = mock_instance

        result = create_progress(100)

        assert result == mock_instance

    @patch("src.utils.progress.tqdm")
    def test_create_progress_with_defaults(self, mock_tqdm_cls):
        """Test create_progress with defaults"""
        create_progress(100)

        call_kwargs = mock_tqdm_cls.call_args[1]
        assert call_kwargs["total"] == 100
        assert call_kwargs["desc"] == "Processing"

    @patch("src.utils.progress.tqdm")
    def test_create_progress_with_custom_desc(self, mock_tqdm_cls):
        """Test create_progress with custom description"""
        create_progress(50, desc="Custom")

        call_kwargs = mock_tqdm_cls.call_args[1]
        assert call_kwargs["desc"] == "Custom"

    @patch("src.utils.progress.tqdm")
    def test_create_progress_accepts_kwargs(self, mock_tqdm_cls):
        """Test create_progress passes kwargs to tqdm"""
        create_progress(100, unit="file", colour="blue")

        call_kwargs = mock_tqdm_cls.call_args[1]
        assert call_kwargs["unit"] == "file"
        assert call_kwargs["colour"] == "blue"


class TestSilentProgress:
    """Test silent_progress function"""

    def test_silent_progress_function_exists(self):
        """Test silent_progress function exists"""
        assert silent_progress is not None
        assert callable(silent_progress)

    def test_silent_progress_returns_iterable(self):
        """Test silent_progress returns original iterable"""
        iterable = [1, 2, 3]
        result = silent_progress(iterable)

        assert result == iterable

    def test_silent_progress_ignores_kwargs(self):
        """Test silent_progress ignores all kwargs"""
        iterable = [1, 2, 3]
        result = silent_progress(iterable, desc="Ignored", unit="ignored", total=999)

        assert result == iterable


class TestGetProgressFunction:
    """Test get_progress_function utility"""

    def test_get_progress_function_exists(self):
        """Test get_progress_function exists"""
        assert get_progress_function is not None
        assert callable(get_progress_function)

    def test_get_progress_function_returns_progress_iterator_when_verbose(self):
        """Test get_progress_function returns progress_iterator when verbose=True"""
        result = get_progress_function(verbose=True)
        assert result == progress_iterator

    def test_get_progress_function_returns_silent_progress_when_not_verbose(self):
        """Test get_progress_function returns silent_progress when verbose=False"""
        result = get_progress_function(verbose=False)
        assert result == silent_progress

    def test_get_progress_function_defaults_to_verbose_true(self):
        """Test get_progress_function defaults to verbose=True"""
        result = get_progress_function()
        assert result == progress_iterator
