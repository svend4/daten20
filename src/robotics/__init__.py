"""
Advanced Robotics Integration Module - v4.3

Enterprise robotics capabilities with autonomous navigation, manipulation,
and human-robot collaboration.

Modules:
- robotics_services: Complete robotics implementation

Components:
- Robot Control System: Multi-robot coordination and control
- Motion Planning & Navigation: Path planning, SLAM, obstacle avoidance
- Computer Vision: Object detection, depth estimation, document recognition
- Manipulation & Grasping: Grasp planning, pick-and-place, force control
- Human-Robot Interaction: Voice, gestures, collaborative workspace
- Fleet Management: Task allocation, battery management, traffic control
- Robot Digital Twin: Virtual simulation, predictive maintenance

Version: 4.3.0
"""

__version__ = "4.3.0"

from .robotics_services import (  # Robot Control System; Motion Planning & Navigation; Computer Vision; Manipulation & Grasping; Human-Robot Interaction; Fleet Management; Robot Digital Twin
    BatteryManager,
    BinPicking,
    CollaborativeSpace,
    ControlMode,
    DepthEstimator,
    DigitalTwinEngine,
    DocumentRecognizer,
    FleetManager,
    ForceController,
    GestureRecognizer,
    GestureType,
    GraspPlanner,
    GraspType,
    IntentPredictor,
    ManipulationController,
    MotionController,
    NavigationStack,
    ObjectDetector,
    ObstacleAvoidance,
    PathPlanner,
    PathPlanningAlgorithm,
    PerformanceMonitor,
    PerformanceOptimizer,
    PhysicsSimulator,
    PickAndPlace,
    PoseEstimator,
    PredictiveAnalytics,
    RobotController,
    RobotStatus,
    RobotType,
    SafetySystem,
    SimulationEngine,
    SLAMAlgorithm,
    SLAMEngine,
    SocialBehavior,
    SpeechInterface,
    TaskAllocationAlgorithm,
    TaskAllocator,
    TrafficController,
    VisionModel,
    VisualServoing,
    get_digital_twin,
    get_fleet_manager,
    get_hri_system,
    get_manipulation_system,
    get_navigation_stack,
    get_robot_controller,
    get_vision_system,
)

__all__ = [
    # Robot Control System
    "RobotType",
    "ControlMode",
    "RobotStatus",
    "RobotController",
    "MotionController",
    "SafetySystem",
    "get_robot_controller",
    # Motion Planning & Navigation
    "PathPlanningAlgorithm",
    "SLAMAlgorithm",
    "PathPlanner",
    "SLAMEngine",
    "ObstacleAvoidance",
    "NavigationStack",
    "get_navigation_stack",
    # Computer Vision
    "VisionModel",
    "ObjectDetector",
    "DepthEstimator",
    "DocumentRecognizer",
    "VisualServoing",
    "PoseEstimator",
    "get_vision_system",
    # Manipulation & Grasping
    "GraspType",
    "GraspPlanner",
    "ManipulationController",
    "ForceController",
    "PickAndPlace",
    "BinPicking",
    "get_manipulation_system",
    # Human-Robot Interaction
    "SpeechInterface",
    "GestureRecognizer",
    "GestureType",
    "CollaborativeSpace",
    "IntentPredictor",
    "SocialBehavior",
    "get_hri_system",
    # Fleet Management
    "TaskAllocationAlgorithm",
    "FleetManager",
    "TaskAllocator",
    "BatteryManager",
    "TrafficController",
    "PerformanceMonitor",
    "get_fleet_manager",
    # Robot Digital Twin
    "SimulationEngine",
    "DigitalTwinEngine",
    "PhysicsSimulator",
    "PredictiveAnalytics",
    "PerformanceOptimizer",
    "get_digital_twin",
]
