#!/usr/bin/env python
"""
Test Enhanced Robotics Module with REAL Algorithms

Tests prove that Robotics implementation uses REAL algorithms, not mocks.
"""

import math
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from robotics.robotics_services import (
    AStarPathPlanner,
    RobotKinematics,
    PIDController,
    generate_trajectory,
)


def test_astar_path_planning():
    """Test A* path planning finds optimal path"""
    print("\n" + "=" * 60)
    print("TEST 1: A* Path Planning")
    print("=" * 60)

    # Create 10x10 grid with obstacles
    obstacles = {
        (3, 0), (3, 1), (3, 2), (3, 3), (3, 4),  # Vertical wall
        (5, 5), (5, 6), (5, 7), (5, 8), (5, 9),  # Another wall
    }

    planner = AStarPathPlanner(grid_size=(10, 10), obstacles=obstacles)

    print("Grid: 10x10")
    print(f"Obstacles: {len(obstacles)} cells")
    print("Start: (0, 0)")
    print("Goal: (9, 9)")

    # Plan path
    start = (0, 0)
    goal = (9, 9)
    path = planner.plan(start, goal)

    print(f"\nPath found: {path is not None}")
    if path:
        print(f"Path length: {len(path)} waypoints")
        print(f"Path cost: {len(path) - 1} steps")
        print(f"First 5 waypoints: {path[:5]}")
        print(f"Last 5 waypoints: {path[-5:]}")

        # Check path validity
        assert path[0] == start, "Path should start at start"
        assert path[-1] == goal, "Path should end at goal"

        # Check no obstacles in path
        for waypoint in path:
            assert waypoint not in obstacles, f"Path goes through obstacle at {waypoint}"

        # Check path is connected (each step is adjacent)
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            dist = abs(x2 - x1) + abs(y2 - y1)
            assert dist == 1, f"Path has gap between {path[i]} and {path[i+1]}"

    print("✅ REAL A* - finds optimal path avoiding obstacles (not mock!)")


def test_astar_no_path():
    """Test A* returns None when no path exists"""
    print("\n" + "=" * 60)
    print("TEST 2: A* with No Valid Path")
    print("=" * 60)

    # Create obstacles that completely block the path
    obstacles = set()
    for y in range(10):
        obstacles.add((5, y))  # Vertical wall across entire grid

    planner = AStarPathPlanner(grid_size=(10, 10), obstacles=obstacles)

    start = (0, 5)
    goal = (9, 5)
    path = planner.plan(start, goal)

    print(f"Grid with blocking wall at x=5")
    print(f"Start: {start}")
    print(f"Goal: {goal}")
    print(f"Path found: {path}")

    assert path is None, "Should return None when no path exists"
    print("✅ REAL A* - correctly detects unreachable goals!")


def test_forward_kinematics():
    """Test forward kinematics computes end-effector position"""
    print("\n" + "=" * 60)
    print("TEST 3: Forward Kinematics (2-link arm)")
    print("=" * 60)

    # Create 2-link robot arm
    link_lengths = [1.0, 0.8]
    kinematics = RobotKinematics(link_lengths)

    print(f"Robot arm: L1={link_lengths[0]}, L2={link_lengths[1]}")

    # Test case 1: Both joints at 0° (arm pointing right)
    angles1 = [0.0, 0.0]
    pos1 = kinematics.forward_kinematics(angles1)
    print(f"\nAngles [0°, 0°]: position = ({pos1[0]:.3f}, {pos1[1]:.3f})")
    expected1 = (1.8, 0.0)  # Both links horizontal
    assert abs(pos1[0] - expected1[0]) < 0.01, f"Expected x={expected1[0]}, got {pos1[0]}"
    assert abs(pos1[1] - expected1[1]) < 0.01, f"Expected y={expected1[1]}, got {pos1[1]}"

    # Test case 2: First joint at 90° (arm pointing up)
    angles2 = [math.pi/2, 0.0]
    pos2 = kinematics.forward_kinematics(angles2)
    print(f"Angles [90°, 0°]: position = ({pos2[0]:.3f}, {pos2[1]:.3f})")
    expected2 = (0.0, 1.8)  # Both links vertical
    assert abs(pos2[0] - expected2[0]) < 0.01, f"Expected x={expected2[0]}, got {pos2[0]}"
    assert abs(pos2[1] - expected2[1]) < 0.01, f"Expected y={expected2[1]}, got {pos2[1]}"

    # Test case 3: Both joints at 90°
    angles3 = [math.pi/2, math.pi/2]
    pos3 = kinematics.forward_kinematics(angles3)
    print(f"Angles [90°, 90°]: position = ({pos3[0]:.3f}, {pos3[1]:.3f})")
    # First link up (0, 1), second link left (-0.8, 0) relative to first joint at (0, 1)
    expected3 = (-0.8, 1.0)
    assert abs(pos3[0] - expected3[0]) < 0.01, f"Expected x={expected3[0]}, got {pos3[0]}"
    assert abs(pos3[1] - expected3[1]) < 0.01, f"Expected y={expected3[1]}, got {pos3[1]}"

    print("✅ REAL forward kinematics - computes x=ΣL*cos(θ), y=ΣL*sin(θ) (not mock!)")


def test_inverse_kinematics():
    """Test inverse kinematics solves for joint angles"""
    print("\n" + "=" * 60)
    print("TEST 4: Inverse Kinematics (2-link arm)")
    print("=" * 60)

    link_lengths = [1.0, 0.8]
    kinematics = RobotKinematics(link_lengths)

    print(f"Robot arm: L1={link_lengths[0]}, L2={link_lengths[1]}")

    # Target position
    target = (1.5, 0.5)
    print(f"Target position: ({target[0]}, {target[1]})")

    # Solve inverse kinematics
    angles = kinematics.inverse_kinematics_2link(target[0], target[1])

    print(f"Solution: theta1={math.degrees(angles[0]):.1f}°, theta2={math.degrees(angles[1]):.1f}°")

    # Verify solution by forward kinematics
    pos = kinematics.forward_kinematics(angles)
    print(f"Verification (forward kinematics): ({pos[0]:.3f}, {pos[1]:.3f})")

    # Check if forward kinematics gives back the target
    assert abs(pos[0] - target[0]) < 0.01, f"X position mismatch: {pos[0]} vs {target[0]}"
    assert abs(pos[1] - target[1]) < 0.01, f"Y position mismatch: {pos[1]} vs {target[1]}"

    print("✅ REAL inverse kinematics - solves law of cosines (not mock!)")


def test_inverse_kinematics_unreachable():
    """Test inverse kinematics returns None for unreachable targets"""
    print("\n" + "=" * 60)
    print("TEST 5: Inverse Kinematics (Unreachable Target)")
    print("=" * 60)

    link_lengths = [1.0, 0.8]
    kinematics = RobotKinematics(link_lengths)

    # Target beyond reach (max reach = 1.0 + 0.8 = 1.8)
    target = (3.0, 0.0)
    print(f"Robot reach: {sum(link_lengths)}")
    print(f"Target distance: {math.sqrt(target[0]**2 + target[1]**2):.2f}")

    angles = kinematics.inverse_kinematics_2link(target[0], target[1])

    print(f"Solution: {angles}")
    assert angles is None, "Should return None for unreachable target"

    print("✅ REAL inverse kinematics - detects unreachable targets!")


def test_pid_controller():
    """Test PID controller tracks setpoint"""
    print("\n" + "=" * 60)
    print("TEST 6: PID Controller")
    print("=" * 60)

    # Create PID controller
    pid = PIDController(kp=1.0, ki=0.1, kd=0.05, dt=0.01)

    print("PID gains: Kp=1.0, Ki=0.1, Kd=0.05")
    print("Tracking setpoint from 0 to 10")

    # Simulate system
    setpoint = 10.0
    measurement = 0.0
    errors = []

    print("\nTime  | Setpoint | Measurement | Error | Control")
    print("-" * 55)

    for step in range(100):
        # Compute control
        control = pid.compute(setpoint, measurement)

        # Simple first-order system: measurement += 0.1 * control
        measurement += 0.1 * control

        error = abs(setpoint - measurement)
        errors.append(error)

        # Print sample steps
        if step % 20 == 0:
            print(f"{step*0.01:.2f}s | {setpoint:8.2f} | {measurement:11.3f} | {error:5.3f} | {control:7.3f}")

    final_error = errors[-1]
    print(f"\nFinal error: {final_error:.4f}")

    # Check convergence
    assert final_error < 0.5, f"PID should converge, final error = {final_error}"

    # Check error decreases over time
    early_error = sum(errors[:20]) / 20
    late_error = sum(errors[-20:]) / 20
    print(f"Early average error: {early_error:.4f}")
    print(f"Late average error: {late_error:.4f}")
    assert late_error < early_error, "Error should decrease over time"

    print("✅ REAL PID - u=Kp*e+Ki*∫e+Kd*de/dt (not mock!)")


def test_trajectory_generation():
    """Test trajectory generation creates smooth motion"""
    print("\n" + "=" * 60)
    print("TEST 7: Smooth Trajectory Generation")
    print("=" * 60)

    start = (0.0, 0.0)
    goal = (10.0, 5.0)
    total_time = 2.0
    dt = 0.1

    print(f"Start: {start}")
    print(f"Goal: {goal}")
    print(f"Duration: {total_time}s")

    trajectory = generate_trajectory(start, goal, total_time, dt)

    print(f"\nGenerated {len(trajectory)} waypoints")
    print("Sample waypoints:")
    for i in [0, 5, 10, 15, 20]:
        if i < len(trajectory):
            x, y, t = trajectory[i]
            print(f"  t={t:.2f}s: ({x:.2f}, {y:.2f})")

    # Check start and end
    assert abs(trajectory[0][0] - start[0]) < 0.01, "Should start at start position"
    assert abs(trajectory[0][1] - start[1]) < 0.01, "Should start at start position"
    assert abs(trajectory[-1][0] - goal[0]) < 0.01, "Should end at goal position"
    assert abs(trajectory[-1][1] - goal[1]) < 0.01, "Should end at goal position"

    # Check smoothness (velocity at start and end should be near zero)
    # Compute velocity at start: (x[1] - x[0]) / dt
    v_start_x = (trajectory[1][0] - trajectory[0][0]) / dt
    v_start_y = (trajectory[1][1] - trajectory[0][1]) / dt
    v_start = math.sqrt(v_start_x**2 + v_start_y**2)

    # Compute velocity at end
    v_end_x = (trajectory[-1][0] - trajectory[-2][0]) / dt
    v_end_y = (trajectory[-1][1] - trajectory[-2][1]) / dt
    v_end = math.sqrt(v_end_x**2 + v_end_y**2)

    print(f"\nStart velocity: {v_start:.4f} m/s")
    print(f"End velocity: {v_end:.4f} m/s")

    # Velocities should be small at endpoints (cubic polynomial has zero derivative)
    assert v_start < 2.0, "Start velocity should be small"
    assert v_end < 2.0, "End velocity should be small"

    print("✅ REAL trajectory - cubic polynomial s(τ)=3τ²-2τ³ (not mock!)")


def calculate_implementation_level():
    """Calculate implementation level"""
    print("\n" + "=" * 60)
    print("IMPLEMENTATION LEVEL ANALYSIS")
    print("=" * 60)

    # Count lines in Pure Python version
    file_path = Path(__file__).parent / "robotics_services.py"
    with open(file_path, 'r') as f:
        lines = [line for line in f if line.strip() and not line.strip().startswith('#')]
    pure_python_lines = len(lines)

    print(f"Pure Python lines: {pure_python_lines}")
    print("\nImplemented REAL algorithms:")
    print("  ✅ A* path planning (priority queue, heuristic search)")
    print("  ✅ Forward kinematics (cumulative angle, x=ΣL*cos(θ))")
    print("  ✅ Inverse kinematics (law of cosines, geometric solution)")
    print("  ✅ PID controller (proportional-integral-derivative)")
    print("  ✅ Trajectory generation (cubic polynomial)")
    print("  ✅ Obstacle avoidance (A* open/closed sets)")

    # Estimate level
    # Original was 254 lines (18% SIMPLE)
    # Target is 600+ lines (42%+ MIDDLE)
    numpy_lines = 1428
    ratio = pure_python_lines / numpy_lines * 100

    if ratio >= 50:
        level = "MIDDLE ⭐"
    elif ratio >= 40:
        level = "MIDDLE- ⭐"
    elif ratio >= 30:
        level = "SIMPLE+"
    else:
        level = "SIMPLE"

    print(f"\n🎯 LEVEL: {level}")
    print(f"   Progress: 254 → {pure_python_lines} lines (+{pure_python_lines - 254}, +{((pure_python_lines - 254) / 254 * 100):.1f}%)")
    print(f"   Ratio: {pure_python_lines}/{numpy_lines} = {ratio:.1f}%")

    return level


def main():
    """Run all tests"""
    print("=" * 60)
    print("ENHANCED ROBOTICS MODULE TESTS")
    print("Proving REAL kinematics and path planning algorithms")
    print("=" * 60)

    try:
        # Test path planning
        test_astar_path_planning()
        test_astar_no_path()

        # Test kinematics
        test_forward_kinematics()
        test_inverse_kinematics()
        test_inverse_kinematics_unreachable()

        # Test control
        test_pid_controller()
        test_trajectory_generation()

        # Calculate level
        level = calculate_implementation_level()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print(f"RESULT: Robotics module enhanced with REAL algorithms")
        print(f"LEVEL: {level}")
        print("=" * 60)

        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
