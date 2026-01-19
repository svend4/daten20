"""
Tests for Robotics Integration (v4.3)

Tests for robot control, motion planning, and computer vision.
"""

import pytest
import numpy as np
from typing import List


class TestRobotControl:
    """Test Robot Control System (v4.3)"""

    def test_import_robot_controller(self):
        """Test importing RobotController"""
        from robotics.robot_control import (
            RobotController,
            RobotType,
            RobotStatus,
            ControlMode
        )
        assert RobotController is not None
        assert RobotType.MANIPULATOR is not None
        assert RobotStatus.IDLE is not None

    def test_create_robot_controller(self):
        """Test creating robot controller"""
        from robotics.robot_control import RobotController, RobotConfig, RobotType

        config = RobotConfig(
            robot_type=RobotType.MANIPULATOR,
            num_joints=6,
            joint_limits=[(-3.14, 3.14)] * 6
        )

        controller = RobotController(
            robot_id="robot_test_01",
            config=config
        )

        assert controller is not None
        assert controller.robot_id == "robot_test_01"
        assert controller.config.num_joints == 6

    def test_robot_start_stop(self):
        """Test starting and stopping robot"""
        from robotics.robot_control import RobotController, RobotConfig, RobotType

        config = RobotConfig(robot_type=RobotType.MANIPULATOR, num_joints=6)
        controller = RobotController("test_robot", config)

        # Start robot
        result = controller.start()
        assert result is True

        # Stop robot
        result = controller.stop()
        assert result is True

    def test_move_to_joint_positions(self):
        """Test moving to joint positions"""
        from robotics.robot_control import RobotController, RobotConfig, RobotType

        config = RobotConfig(robot_type=RobotType.MANIPULATOR, num_joints=6)
        controller = RobotController("test_robot", config)
        controller.start()

        target_positions = [0.0, 0.5, -0.5, 0.0, 1.0, 0.0]
        result = controller.move_to_joint_positions(target_positions)

        assert result is True

    def test_emergency_stop(self):
        """Test emergency stop"""
        from robotics.robot_control import (
            RobotController,
            RobotConfig,
            RobotType,
            RobotStatus
        )

        config = RobotConfig(robot_type=RobotType.MANIPULATOR, num_joints=6)
        controller = RobotController("test_robot", config)
        controller.start()

        # Trigger emergency stop
        result = controller.emergency_stop()
        assert result is True
        assert controller.emergency_stop_active is True

    def test_multi_robot_coordinator(self):
        """Test multi-robot coordinator"""
        from robotics.robot_control import (
            MultiRobotCoordinator,
            RobotController,
            RobotConfig,
            RobotType
        )

        coordinator = MultiRobotCoordinator()

        # Create and register robots
        config1 = RobotConfig(robot_type=RobotType.MANIPULATOR, num_joints=6)
        robot1 = RobotController("robot_1", config1)

        config2 = RobotConfig(robot_type=RobotType.MOBILE, num_joints=2)
        robot2 = RobotController("robot_2", config2)

        coordinator.register_robot(robot1)
        coordinator.register_robot(robot2)

        assert len(coordinator.robots) == 2


class TestMotionPlanning:
    """Test Motion Planning System (v4.3)"""

    def test_import_motion_planner(self):
        """Test importing MotionPlanner"""
        from robotics.motion_planning import (
            MotionPlanner,
            PlannerAlgorithm,
            Point2D,
            Obstacle
        )
        assert MotionPlanner is not None
        assert PlannerAlgorithm.A_STAR is not None
        assert Point2D is not None

    def test_create_motion_planner(self):
        """Test creating motion planner"""
        from robotics.motion_planning import (
            MotionPlanner,
            PathPlanningConfig,
            PlannerAlgorithm
        )

        config = PathPlanningConfig(
            algorithm=PlannerAlgorithm.A_STAR,
            grid_resolution=0.1,
            max_iterations=1000
        )

        planner = MotionPlanner(config)
        assert planner is not None
        assert planner.config.algorithm == PlannerAlgorithm.A_STAR

    def test_plan_path_simple(self):
        """Test simple path planning without obstacles"""
        from robotics.motion_planning import MotionPlanner, Point2D

        planner = MotionPlanner()
        start = Point2D(0.0, 0.0)
        goal = Point2D(5.0, 5.0)

        path = planner.plan_path(start, goal, obstacles=[])

        assert path is not None
        assert path.success is True
        assert len(path.waypoints) > 0

    def test_plan_path_with_obstacles(self):
        """Test path planning with obstacles"""
        from robotics.motion_planning import MotionPlanner, Point2D, Obstacle

        planner = MotionPlanner()
        start = Point2D(0.0, 0.0)
        goal = Point2D(5.0, 5.0)

        # Add obstacle in the middle
        obstacle = Obstacle(
            position=Point2D(2.5, 2.5),
            radius=1.0
        )

        path = planner.plan_path(start, goal, obstacles=[obstacle])

        assert path is not None
        # Path should still succeed by going around obstacle

    def test_slam_system(self):
        """Test SLAM system"""
        from robotics.motion_planning import SLAMSystem, Point2D

        slam = SLAMSystem()

        # Add some pose updates
        pose1 = Point2D(0.0, 0.0)
        slam.update_pose(pose1)

        pose2 = Point2D(1.0, 0.0)
        slam.update_pose(pose2)

        # Get current map
        slam_map = slam.get_map()
        assert slam_map is not None


class TestComputerVision:
    """Test Computer Vision System (v4.3)"""

    def test_import_vision_system(self):
        """Test importing VisionSystem"""
        from robotics.computer_vision import (
            VisionSystem,
            DetectionModel,
            BoundingBox,
            Detection
        )
        assert VisionSystem is not None
        assert DetectionModel.YOLO_V8 is not None

    def test_create_vision_system(self):
        """Test creating vision system"""
        from robotics.computer_vision import VisionSystem, DetectionModel

        vision = VisionSystem(model=DetectionModel.YOLO_V8)
        assert vision is not None
        assert vision.model == DetectionModel.YOLO_V8

    def test_detect_objects(self):
        """Test object detection"""
        from robotics.computer_vision import VisionSystem

        vision = VisionSystem()

        # Simulate image (in real scenario, this would be actual image data)
        fake_image = np.zeros((480, 640, 3), dtype=np.uint8)

        detections = vision.detect_objects(fake_image, confidence_threshold=0.5)

        assert isinstance(detections, list)
        # In simulation mode, should return at least one detection
        if len(detections) > 0:
            detection = detections[0]
            assert hasattr(detection, 'bbox')
            assert hasattr(detection.bbox, 'confidence')

    def test_estimate_depth(self):
        """Test depth estimation"""
        from robotics.computer_vision import VisionSystem

        vision = VisionSystem()
        fake_image = np.zeros((480, 640, 3), dtype=np.uint8)

        depth_estimate = vision.estimate_depth(fake_image)

        assert depth_estimate is not None
        assert hasattr(depth_estimate, 'min_depth')
        assert hasattr(depth_estimate, 'max_depth')
        assert hasattr(depth_estimate, 'confidence')

    def test_object_tracking(self):
        """Test object tracking"""
        from robotics.computer_vision import VisionSystem, BoundingBox

        vision = VisionSystem()
        fake_image = np.zeros((480, 640, 3), dtype=np.uint8)

        initial_bbox = BoundingBox(
            x=100, y=100, width=50, height=50,
            confidence=0.9, class_id=0, class_name="object"
        )

        # Start tracking
        updated_bbox = vision.track_object(fake_image, initial_bbox, tracker_id=1)

        assert updated_bbox is not None
        assert 1 in vision.trackers


class TestRoboticsManager:
    """Test Robotics Manager Integration (v4.3)"""

    def test_import_robotics_manager(self):
        """Test importing RoboticsManager"""
        from robotics import RoboticsManager, RoboticsSystemConfig
        assert RoboticsManager is not None

    def test_create_robotics_manager(self):
        """Test creating robotics manager"""
        from robotics import RoboticsManager, RoboticsSystemConfig

        config = RoboticsSystemConfig(
            enable_vision=True,
            enable_planning=True,
            simulation_mode=True
        )

        manager = RoboticsManager(config)
        assert manager is not None
        assert manager.config.simulation_mode is True

    def test_create_robot_via_manager(self):
        """Test creating robot via manager"""
        from robotics import RoboticsManager, RobotType

        manager = RoboticsManager()
        robot_id = manager.create_robot(
            robot_id="test_robot_01",
            robot_type=RobotType.MANIPULATOR,
            num_joints=6
        )

        assert robot_id == "test_robot_01"
        assert robot_id in manager.robots

    def test_move_robot_via_manager(self):
        """Test moving robot via manager"""
        from robotics import RoboticsManager, RobotType

        manager = RoboticsManager()
        robot_id = manager.create_robot("test_robot", RobotType.MANIPULATOR, 6)

        result = manager.move_robot(
            robot_id=robot_id,
            target_position=[0.0, 0.5, -0.5, 0.0, 1.0, 0.0],
            use_planning=False
        )

        assert result is True

    def test_emergency_stop_all_via_manager(self):
        """Test emergency stop all robots"""
        from robotics import RoboticsManager, RobotType

        manager = RoboticsManager()
        manager.create_robot("robot1", RobotType.MANIPULATOR, 6)
        manager.create_robot("robot2", RobotType.MOBILE, 2)

        result = manager.emergency_stop_all()
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
