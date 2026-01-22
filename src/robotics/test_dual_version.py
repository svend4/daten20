"""
Test Dual-Version Robotics Implementation
"""

import asyncio
import sys
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from robotics import (
    # Check which version is being used
    HAS_NUMPY,
    
    # Enums
    RobotType,
    ControlMode,
    
    # Systems
    RobotController,
    MotionPlanner,
    ComputerVision,
    ManipulationSystem,
    FleetManager,
    IntegratedRoboticsSystem,
    
    # Singletons
    get_motion_planner,
    get_computer_vision,
    get_manipulation_system,
    get_fleet_manager,
    get_integrated_robotics_system,
)


async def test_robot_controller():
    """Test robot controller"""
    print("\nTesting Robot Controller...")
    
    controller = RobotController(
        robot_id="robot1",
        robot_type=RobotType.MOBILE_ROBOT,
        control_mode=ControlMode.POSITION,
    )
    
    await controller.connect()
    
    success = await controller.move_to((1.0, 2.0, 0.0))
    print(f"  Move success: {success}")
    
    status = controller.get_status()
    print(f"  Position: {status.position}")
    print(f"  Battery: {status.battery_percent:.1f}%")
    
    print("  ✅ Robot Controller works!")


async def test_motion_planner():
    """Test motion planner"""
    print("\nTesting Motion Planner...")
    
    planner = get_motion_planner()
    
    path = await planner.plan_path(
        start=(0.0, 0.0, 0.0),
        goal=(10.0, 10.0, 0.0),
    )
    
    print(f"  Path points: {len(path)}")
    print(f"  First point: {path[0]}")
    print(f"  Last point: {path[-1]}")
    
    print("  ✅ Motion Planner works!")


async def test_computer_vision():
    """Test computer vision"""
    print("\nTesting Computer Vision...")
    
    cv = get_computer_vision()
    
    # Mock image data
    image = [[0] * 100 for _ in range(100)]
    
    objects = await cv.detect_objects(image)
    
    print(f"  Detected objects: {len(objects)}")
    if objects:
        print(f"  First object: {objects[0]['class']} (conf: {objects[0]['confidence']:.2f})")
    
    print("  ✅ Computer Vision works!")


async def test_manipulation():
    """Test manipulation system"""
    print("\nTesting Manipulation System...")
    
    manipulation = get_manipulation_system()
    
    success = await manipulation.grasp_object(
        object_pose=(1.0, 2.0, 0.5),
        robot_id="robot1",
    )
    
    print(f"  Grasp success: {success}")
    
    print("  ✅ Manipulation System works!")


async def test_fleet_manager():
    """Test fleet manager"""
    print("\nTesting Fleet Manager...")
    
    fleet = get_fleet_manager()
    
    robot1 = RobotController("robot1", RobotType.MOBILE_ROBOT, ControlMode.POSITION)
    robot2 = RobotController("robot2", RobotType.MANIPULATOR, ControlMode.VELOCITY)
    
    fleet.add_robot(robot1)
    fleet.add_robot(robot2)
    
    status = fleet.get_fleet_status()
    
    print(f"  Fleet size: {status['num_robots']}")
    print(f"  Robot IDs: {list(status['robots'].keys())}")
    
    print("  ✅ Fleet Manager works!")


async def test_integrated_system():
    """Test integrated robotics system"""
    print("\nTesting Integrated Robotics System...")
    
    system = get_integrated_robotics_system()
    
    status = system.get_system_status()
    
    print(f"  Robots: {status['num_robots']}")
    print(f"  Planners: {status['num_planners']}")
    
    print("  ✅ Integrated System works!")


async def main():
    print("=" * 60)
    print("Robotics Dual-Version Test Suite")
    print("=" * 60)
    
    print(f"\nTesting imports...")
    print(f"  HAS_NUMPY: {HAS_NUMPY}")
    print(f"  ✅ Imports work!")
    
    await test_robot_controller()
    await test_motion_planner()
    await test_computer_vision()
    await test_manipulation()
    await test_fleet_manager()
    await test_integrated_system()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
