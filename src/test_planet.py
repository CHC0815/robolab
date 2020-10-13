#!/usr/bin/env python3
 
import unittest
import sys

from planet import Direction, Planet


class ExampleTestPlanet(unittest.TestCase):
    def setUp(self):
        """
        Instantiates the planet data structure and fills it with paths

        +--+
        |  |
        +-0,3------+
           |       |
          0,2-----2,2 (target)
           |      /
        +-0,1    /
        |  |    /
        +-0,0-1,0
           |
        (start)

        """
        # Initialize your data structure here
        self.planet = Planet()

        # paths of the Example Planet
        self.planet.add_path(((0, 0), Direction.NORTH), ((0, 1), Direction.SOUTH), 1)
        self.planet.add_path(((0, 0), Direction.WEST), ((0, 1), Direction.WEST), 3)
        self.planet.add_path(((0, 0), Direction.EAST), ((1, 0), Direction.WEST), 1)
        self.planet.add_path(((1, 0), Direction.NORTH), ((2, 2), Direction.SOUTH), 3)
        self.planet.add_path(((0, 1), Direction.NORTH), ((0, 2), Direction.SOUTH), 1)
        self.planet.add_path(((0, 2), Direction.EAST), ((2, 2), Direction.WEST), 2)
        self.planet.add_path(((0, 2), Direction.NORTH), ((0, 3), Direction.SOUTH), 1)
        self.planet.add_path(((0, 3), Direction.NORTH), ((0, 3), Direction.WEST), 3)
        self.planet.add_path(((0, 3), Direction.EAST), ((2, 2), Direction.NORTH), 3)

    # def show_test_planet(self):
        print(self.planet.get_paths())
        # print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')

    @unittest.skip('Example test, should not count in final test results')
    def test_target_not_reachable_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target not reachable nearby

        Result: Target is not reachable
        """
        self.assertIsNone(self.planet.shortest_path((0, 0), (1, 2)))


class TestRoboLabPlanet(unittest.TestCase):
    def setUp(self):
        """
        Instantiates the planet data structure and fills it with paths

        MODEL YOUR TEST PLANET HERE (if you'd like):

        """
        # Initialize your data structure here
        self.planet = Planet()

        # self.planet.add_path(...)
        self.planet.add_path(((0, 0), Direction.NORTH), ((0, 1), Direction.SOUTH), 1)
        self.planet.add_path(((0, 0), Direction.EAST), ((1, 0), Direction.WEST), 1)
        self.planet.add_path(((0, 1), Direction.EAST), ((1, 2), Direction.SOUTH), 2)
        self.planet.add_path(((1, 0), Direction.EAST), ((2, 1), Direction.SOUTH), 2)
        self.planet.add_path(((1, 2), Direction.WEST), ((0, 2), Direction.EAST), 1)
        self.planet.add_path(((1, 2), Direction.NORTH), ((2, 4), Direction.WEST), 3)
        self.planet.add_path(((0, 2), Direction.WEST), ((0, 2), Direction.SOUTH), 1)
        self.planet.add_path(((2, 1), Direction.NORTH), ((2, 3), Direction.SOUTH), 2)
        self.planet.add_path(((2, 3), Direction.NORTH), ((2, 4), Direction.SOUTH), 1)
        self.planet.add_path(((0, 4), Direction.WEST), ((0, 4), Direction.EAST), 2)
        self.planet.add_path(((2, 4), Direction.NORTH), ((0, 4), Direction.NORTH), 4)

    def test_integrity(self):
        """
        This test should check that the dictionary returned by "planet.get_paths()" matches the expected structure
        """
        self.fail('implement me!')

    def test_empty_planet(self):
        """
        This test should check that an empty planet really is empty
        """
        self.fail('implement me!')

    def test_target(self):
        """
        This test should check that the shortest-path algorithm implemented works.

        Requirement: Minimum distance is three nodes (two paths in list returned)
        """
        self.fail('implement me!')

    def test_target_not_reachable(self):
        """
        This test should check that a target outside the map or at an unexplored node is not reachable
        """
        self.fail('implement me!')

    def test_same_length(self):
        """
        This test should check that the shortest-path algorithm implemented returns a shortest path even if there
        are multiple shortest paths with the same length.

        Requirement: Minimum of two paths with same cost exists, only one is returned by the logic implemented
        """
        self.fail('implement me!')

    def test_target_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target nearby

        Result: Target is reachable
        """
        self.fail('implement me!')

    def test_target_not_reachable_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target not reachable nearby

        Result: Target is not reachable
        """
        self.fail('implement me!')


if __name__ == "__main__":
    # unittest.main()
    ExampleTestPlanet().setUp()

    
    # p = Planet();
