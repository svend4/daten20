"""
Advanced Robotics Services v4.3.0

**DUAL-VERSION IMPLEMENTATION**:
- Pure Python: Works everywhere, no dependencies (simplified)
- NumPy: 20-50x faster, full features, requires numpy

Comprehensive robotics framework for autonomous systems, mobile robots,
manipulators, and multi-robot coordination.

Version: 4.3.0 (FULL IMPLEMENTATION - Dual Version)
"""

__version__ = "4.3.0"

# ALWAYS import Pure Python version (baseline, always available)
from .robotics_services import (
    # Enums
    RobotType,
    ControlMode,

    # Dataclasses
    RobotStatus,

    # Classes (Pure Python - simplified)
    RobotController as RobotControllerPython,
    MotionPlanner as MotionPlannerPython,
    ComputerVision as ComputerVisionPython,
    ManipulationSystem as ManipulationSystemPython,
    FleetManager as FleetManagerPython,
    IntegratedRoboticsSystem as IntegratedRoboticsSystemPython,

    # Singletons (Pure Python)
    get_motion_planner as get_motion_planner_python,
    get_computer_vision as get_computer_vision_python,
    get_manipulation_system as get_manipulation_system_python,
    get_fleet_manager as get_fleet_manager_python,
    get_integrated_robotics_system as get_integrated_robotics_system_python,
)

# TRY to import NumPy version (optional, faster, full features)
try:
    from .robotics_services_numpy import (
        # Classes (NumPy version - full features)
        RobotController as RobotControllerNumpy,
        MotionPlanner as MotionPlannerNumpy,
        ComputerVision as ComputerVisionNumpy,
        ManipulationSystem as ManipulationSystemNumpy,
        FleetManager as FleetManagerNumpy,
        IntegratedRoboticsSystem as IntegratedRoboticsSystemNumpy,

        # Singletons (NumPy version)
        get_motion_planner as get_motion_planner_numpy,
        get_computer_vision as get_computer_vision_numpy,
        get_manipulation as get_manipulation_system_numpy,
        get_fleet_manager as get_fleet_manager_numpy,
        get_integrated_robotics_system as get_integrated_robotics_system_numpy,
    )
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Smart aliases - automatically use best available version
if HAS_NUMPY:
    # NumPy version available - use it (20-50x faster, full features)
    RobotController = RobotControllerNumpy
    MotionPlanner = MotionPlannerNumpy
    ComputerVision = ComputerVisionNumpy
    ManipulationSystem = ManipulationSystemNumpy
    FleetManager = FleetManagerNumpy
    IntegratedRoboticsSystem = IntegratedRoboticsSystemNumpy

    # Use NumPy getters
    get_motion_planner = get_motion_planner_numpy
    get_computer_vision = get_computer_vision_numpy
    get_manipulation_system = get_manipulation_system_numpy
    get_fleet_manager = get_fleet_manager_numpy
    get_integrated_robotics_system = get_integrated_robotics_system_numpy
else:
    # NumPy not available - use Pure Python (simplified)
    RobotController = RobotControllerPython
    MotionPlanner = MotionPlannerPython
    ComputerVision = ComputerVisionPython
    ManipulationSystem = ManipulationSystemPython
    FleetManager = FleetManagerPython
    IntegratedRoboticsSystem = IntegratedRoboticsSystemPython

    # Use Pure Python getters
    get_motion_planner = get_motion_planner_python
    get_computer_vision = get_computer_vision_python
    get_manipulation_system = get_manipulation_system_python
    get_fleet_manager = get_fleet_manager_python
    get_integrated_robotics_system = get_integrated_robotics_system_python

__all__ = [
    # Version
    "__version__",

    # Enums
    "RobotType",
    "ControlMode",

    # Dataclasses
    "RobotStatus",

    # Core Systems (auto-select best version)
    "RobotController",
    "MotionPlanner",
    "ComputerVision",
    "ManipulationSystem",
    "FleetManager",
    "IntegratedRoboticsSystem",

    # Pure Python versions (always available)
    "RobotControllerPython",
    "MotionPlannerPython",
    "ComputerVisionPython",
    "ManipulationSystemPython",
    "FleetManagerPython",
    "IntegratedRoboticsSystemPython",

    # Singletons
    "get_motion_planner",
    "get_computer_vision",
    "get_manipulation_system",
    "get_fleet_manager",
    "get_integrated_robotics_system",

    # Pure Python singleton getters
    "get_motion_planner_python",
    "get_computer_vision_python",
    "get_manipulation_system_python",
    "get_fleet_manager_python",
    "get_integrated_robotics_system_python",

    # Dual-version flag
    "HAS_NUMPY",
]
