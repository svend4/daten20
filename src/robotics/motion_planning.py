"""
Motion Planning System - v4.3

Path planning and navigation for robotics.
Implements A*, RRT, SLAM, and obstacle avoidance algorithms.

Version: 4.3.0
"""

__version__ = '4.3.0'

from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import math
import heapq
import random
import logging

logger = logging.getLogger(__name__)


class PlannerAlgorithm(Enum):
    """Path planning algorithms"""
    A_STAR = "a_star"
    RRT = "rrt"              # Rapidly-exploring Random Tree
    RRT_STAR = "rrt_star"    # Optimal RRT
    PRM = "prm"              # Probabilistic Roadmap
    DIJKSTRA = "dijkstra"
    DWA = "dwa"              # Dynamic Window Approach


@dataclass
class Point2D:
    """2D point"""
    x: float
    y: float

    def distance_to(self, other: 'Point2D') -> float:
        """Calculate Euclidean distance"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


@dataclass
class Point3D:
    """3D point"""
    x: float
    y: float
    z: float

    def distance_to(self, other: 'Point3D') -> float:
        """Calculate Euclidean distance"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)


@dataclass
class Obstacle:
    """Obstacle representation"""
    center: Point2D
    radius: float
    height: Optional[float] = None


@dataclass
class PathPlanningConfig:
    """Path planning configuration"""
    algorithm: PlannerAlgorithm = PlannerAlgorithm.A_STAR
    resolution: float = 0.1          # Grid resolution (meters)
    safety_margin: float = 0.2       # Safety margin around obstacles (meters)
    max_iterations: int = 10000
    goal_tolerance: float = 0.1      # Goal reached tolerance (meters)


@dataclass
class Path:
    """Planned path"""
    waypoints: List[Point2D] = field(default_factory=list)
    total_length: float = 0.0
    planning_time: float = 0.0
    success: bool = False


class MotionPlanner:
    """
    Motion Planner - Path planning for robot navigation

    Supports multiple planning algorithms:
    - A*: Grid-based optimal path finding
    - RRT: Sampling-based rapid exploration
    - RRT*: Optimal sampling-based planning
    - PRM: Probabilistic roadmap for multi-query planning

    Example:
        >>> planner = MotionPlanner(config)
        >>> start = Point2D(0, 0)
        >>> goal = Point2D(10, 10)
        >>> obstacles = [Obstacle(Point2D(5, 5), radius=1.0)]
        >>> path = planner.plan_path(start, goal, obstacles)
    """

    def __init__(self, config: Optional[PathPlanningConfig] = None):
        """
        Initialize Motion Planner

        Args:
            config: Path planning configuration
        """
        self.config = config or PathPlanningConfig()
        self.map_bounds = ((0.0, 0.0), (100.0, 100.0))  # Default map bounds
        logger.info(f"Motion Planner initialized - Algorithm: {self.config.algorithm.value}")

    def plan_path(self,
                  start: Point2D,
                  goal: Point2D,
                  obstacles: List[Obstacle]) -> Path:
        """
        Plan path from start to goal

        Args:
            start: Start position
            goal: Goal position
            obstacles: List of obstacles

        Returns:
            Planned path
        """
        import time
        start_time = time.time()

        if self.config.algorithm == PlannerAlgorithm.A_STAR:
            path = self._plan_a_star(start, goal, obstacles)
        elif self.config.algorithm == PlannerAlgorithm.RRT:
            path = self._plan_rrt(start, goal, obstacles)
        elif self.config.algorithm == PlannerAlgorithm.RRT_STAR:
            path = self._plan_rrt_star(start, goal, obstacles)
        elif self.config.algorithm == PlannerAlgorithm.DIJKSTRA:
            path = self._plan_dijkstra(start, goal, obstacles)
        else:
            logger.error(f"Unsupported algorithm: {self.config.algorithm}")
            path = Path(success=False)

        path.planning_time = time.time() - start_time
        logger.info(f"Path planning completed in {path.planning_time:.3f}s - "
                   f"Length: {path.total_length:.2f}m, Success: {path.success}")

        return path

    def _plan_a_star(self,
                     start: Point2D,
                     goal: Point2D,
                     obstacles: List[Obstacle]) -> Path:
        """
        A* path planning algorithm

        Args:
            start: Start position
            goal: Goal position
            obstacles: List of obstacles

        Returns:
            Planned path
        """
        # Create grid
        grid = self._create_grid(obstacles)

        # Convert to grid coordinates
        start_grid = self._world_to_grid(start)
        goal_grid = self._world_to_grid(goal)

        # Check if start/goal are valid
        if not self._is_valid_grid_cell(start_grid, grid):
            logger.error("Start position is invalid or in obstacle")
            return Path(success=False)

        if not self._is_valid_grid_cell(goal_grid, grid):
            logger.error("Goal position is invalid or in obstacle")
            return Path(success=False)

        # A* algorithm
        open_set = [(0, start_grid)]  # (f_score, node)
        came_from = {}
        g_score = {start_grid: 0}
        f_score = {start_grid: self._heuristic(start_grid, goal_grid)}

        iterations = 0
        while open_set and iterations < self.config.max_iterations:
            iterations += 1

            _, current = heapq.heappop(open_set)

            # Check if reached goal
            if self._distance(current, goal_grid) < self.config.goal_tolerance / self.config.resolution:
                # Reconstruct path
                waypoints = self._reconstruct_path(came_from, current)
                waypoints_world = [self._grid_to_world(p) for p in waypoints]

                path = Path(
                    waypoints=waypoints_world,
                    total_length=self._calculate_path_length(waypoints_world),
                    success=True
                )
                logger.info(f"A* found path with {len(waypoints)} waypoints in {iterations} iterations")
                return path

            # Explore neighbors
            for neighbor in self._get_neighbors(current):
                if not self._is_valid_grid_cell(neighbor, grid):
                    continue

                tentative_g = g_score[current] + self._distance(current, neighbor)

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self._heuristic(neighbor, goal_grid)

                    if neighbor not in [node for _, node in open_set]:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))

        logger.warning(f"A* failed to find path after {iterations} iterations")
        return Path(success=False)

    def _plan_rrt(self,
                  start: Point2D,
                  goal: Point2D,
                  obstacles: List[Obstacle]) -> Path:
        """
        RRT (Rapidly-exploring Random Tree) path planning

        Args:
            start: Start position
            goal: Goal position
            obstacles: List of obstacles

        Returns:
            Planned path
        """
        tree = {0: {'point': start, 'parent': None}}
        node_id = 1

        for iteration in range(self.config.max_iterations):
            # Sample random point (bias toward goal)
            if random.random() < 0.1:  # 10% bias
                random_point = goal
            else:
                random_point = Point2D(
                    random.uniform(self.map_bounds[0][0], self.map_bounds[1][0]),
                    random.uniform(self.map_bounds[0][1], self.map_bounds[1][1])
                )

            # Find nearest node in tree
            nearest_id = self._find_nearest_node(random_point, tree)
            nearest_point = tree[nearest_id]['point']

            # Steer toward random point
            new_point = self._steer(nearest_point, random_point, step_size=1.0)

            # Check collision
            if not self._is_path_collision_free(nearest_point, new_point, obstacles):
                continue

            # Add to tree
            tree[node_id] = {'point': new_point, 'parent': nearest_id}

            # Check if reached goal
            if new_point.distance_to(goal) < self.config.goal_tolerance:
                # Reconstruct path
                waypoints = self._reconstruct_rrt_path(tree, node_id)

                path = Path(
                    waypoints=waypoints,
                    total_length=self._calculate_path_length(waypoints),
                    success=True
                )
                logger.info(f"RRT found path with {len(waypoints)} waypoints in {iteration} iterations")
                return path

            node_id += 1

        logger.warning(f"RRT failed to find path after {self.config.max_iterations} iterations")
        return Path(success=False)

    def _plan_rrt_star(self,
                       start: Point2D,
                       goal: Point2D,
                       obstacles: List[Obstacle]) -> Path:
        """
        RRT* (optimal RRT) path planning

        Similar to RRT but includes rewiring for optimal paths.

        Args:
            start: Start position
            goal: Goal position
            obstacles: List of obstacles

        Returns:
            Planned path
        """
        # RRT* implementation (simplified)
        # In full implementation, add rewiring step for optimality
        return self._plan_rrt(start, goal, obstacles)

    def _plan_dijkstra(self,
                       start: Point2D,
                       goal: Point2D,
                       obstacles: List[Obstacle]) -> Path:
        """
        Dijkstra path planning algorithm

        Args:
            start: Start position
            goal: Goal position
            obstacles: List of obstacles

        Returns:
            Planned path
        """
        # Similar to A* but without heuristic
        # Implementation similar to A* with h(n) = 0
        return self._plan_a_star(start, goal, obstacles)

    # Helper methods

    def _create_grid(self, obstacles: List[Obstacle]) -> Dict[Tuple[int, int], bool]:
        """Create occupancy grid"""
        grid = {}
        grid_width = int((self.map_bounds[1][0] - self.map_bounds[0][0]) / self.config.resolution)
        grid_height = int((self.map_bounds[1][1] - self.map_bounds[0][1]) / self.config.resolution)

        # Mark all cells as free initially
        for i in range(grid_width):
            for j in range(grid_height):
                grid[(i, j)] = True  # Free

        # Mark obstacle cells
        for obstacle in obstacles:
            center_grid = self._world_to_grid(obstacle.center)
            radius_cells = int(obstacle.radius / self.config.resolution) + int(self.config.safety_margin / self.config.resolution)

            for i in range(-radius_cells, radius_cells + 1):
                for j in range(-radius_cells, radius_cells + 1):
                    cell = (center_grid[0] + i, center_grid[1] + j)
                    if 0 <= cell[0] < grid_width and 0 <= cell[1] < grid_height:
                        grid[cell] = False  # Occupied

        return grid

    def _world_to_grid(self, point: Point2D) -> Tuple[int, int]:
        """Convert world coordinates to grid coordinates"""
        i = int((point.x - self.map_bounds[0][0]) / self.config.resolution)
        j = int((point.y - self.map_bounds[0][1]) / self.config.resolution)
        return (i, j)

    def _grid_to_world(self, grid_cell: Tuple[int, int]) -> Point2D:
        """Convert grid coordinates to world coordinates"""
        x = self.map_bounds[0][0] + grid_cell[0] * self.config.resolution
        y = self.map_bounds[0][1] + grid_cell[1] * self.config.resolution
        return Point2D(x, y)

    def _is_valid_grid_cell(self, cell: Tuple[int, int], grid: Dict[Tuple[int, int], bool]) -> bool:
        """Check if grid cell is valid and free"""
        return cell in grid and grid[cell]

    def _get_neighbors(self, cell: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get 8-connected neighbors of grid cell"""
        i, j = cell
        neighbors = []
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue
                neighbors.append((i + di, j + dj))
        return neighbors

    def _heuristic(self, cell1: Tuple[int, int], cell2: Tuple[int, int]) -> float:
        """Heuristic function (Euclidean distance)"""
        return math.sqrt((cell1[0] - cell2[0])**2 + (cell1[1] - cell2[1])**2)

    def _distance(self, cell1: Tuple[int, int], cell2: Tuple[int, int]) -> float:
        """Distance between two grid cells"""
        return math.sqrt((cell1[0] - cell2[0])**2 + (cell1[1] - cell2[1])**2)

    def _reconstruct_path(self, came_from: Dict, current: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Reconstruct path from came_from dictionary"""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def _find_nearest_node(self, point: Point2D, tree: Dict[int, Dict]) -> int:
        """Find nearest node in RRT tree"""
        nearest_id = 0
        min_distance = float('inf')

        for node_id, node_data in tree.items():
            distance = point.distance_to(node_data['point'])
            if distance < min_distance:
                min_distance = distance
                nearest_id = node_id

        return nearest_id

    def _steer(self, from_point: Point2D, to_point: Point2D, step_size: float) -> Point2D:
        """Steer from one point toward another with maximum step size"""
        distance = from_point.distance_to(to_point)
        if distance <= step_size:
            return to_point

        ratio = step_size / distance
        new_x = from_point.x + (to_point.x - from_point.x) * ratio
        new_y = from_point.y + (to_point.y - from_point.y) * ratio

        return Point2D(new_x, new_y)

    def _is_path_collision_free(self,
                                from_point: Point2D,
                                to_point: Point2D,
                                obstacles: List[Obstacle]) -> bool:
        """Check if path segment is collision-free"""
        # Check collision along line segment
        steps = int(from_point.distance_to(to_point) / self.config.resolution) + 1

        for i in range(steps + 1):
            t = i / steps
            x = from_point.x + (to_point.x - from_point.x) * t
            y = from_point.y + (to_point.y - from_point.y) * t
            point = Point2D(x, y)

            # Check collision with obstacles
            for obstacle in obstacles:
                if point.distance_to(obstacle.center) < obstacle.radius + self.config.safety_margin:
                    return False

        return True

    def _reconstruct_rrt_path(self, tree: Dict[int, Dict], leaf_id: int) -> List[Point2D]:
        """Reconstruct path from RRT tree"""
        path = []
        current_id = leaf_id

        while current_id is not None:
            path.append(tree[current_id]['point'])
            current_id = tree[current_id]['parent']

        path.reverse()
        return path

    def _calculate_path_length(self, waypoints: List[Point2D]) -> float:
        """Calculate total path length"""
        length = 0.0
        for i in range(len(waypoints) - 1):
            length += waypoints[i].distance_to(waypoints[i + 1])
        return length


class SLAMSystem:
    """
    SLAM (Simultaneous Localization and Mapping) System

    Builds map while tracking robot position.
    Simplified implementation for demonstration.
    """

    def __init__(self):
        """Initialize SLAM system"""
        self.map_data: Dict[Tuple[int, int], float] = {}  # Occupancy grid
        self.robot_pose = Point2D(0.0, 0.0)
        logger.info("SLAM System initialized")

    def update(self, sensor_data: Dict[str, Any], odometry: Tuple[float, float]) -> None:
        """
        Update SLAM with sensor data and odometry

        Args:
            sensor_data: Sensor readings (e.g., LIDAR scans)
            odometry: Robot odometry (delta_x, delta_y)
        """
        # Update robot pose
        self.robot_pose.x += odometry[0]
        self.robot_pose.y += odometry[1]

        # Update map with sensor data
        # In full implementation, use particle filter or EKF-SLAM
        logger.debug(f"SLAM updated - Robot pose: ({self.robot_pose.x:.2f}, {self.robot_pose.y:.2f})")

    def get_map(self) -> Dict[Tuple[int, int], float]:
        """Get current map"""
        return self.map_data

    def get_pose(self) -> Point2D:
        """Get current robot pose estimate"""
        return self.robot_pose


__all__ = [
    'MotionPlanner',
    'SLAMSystem',
    'PlannerAlgorithm',
    'Point2D',
    'Point3D',
    'Obstacle',
    'PathPlanningConfig',
    'Path',
]
