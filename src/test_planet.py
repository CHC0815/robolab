#!/usr/bin/env python3

import unittest
import sys

from planet import Direction, Planet

# class ExampleTestPlanet(unittest.TestCase):
#     def setUp(self):
#         """
#         Instantiates the planet data structure and fills it with paths

#         +--+
#         |  |
#         +-0,3------+
#            |       |
#           0,2-----2,2 (target)
#            |      /
#         +-0,1    /
#         |  |    /
#         +-0,0-1,0
#            |
#         (start)

#         """
#         # Initialize your data structure here
#         self.planet = Planet()

#         # paths of the Example Planet

#         # passable paths
#         self.planet.add_path(((0, 0), Direction.NORTH),
#                              ((0, 1), Direction.SOUTH), 1)
#         self.planet.add_path(((0, 0), Direction.WEST),
#                              ((0, 1), Direction.WEST), 3)
#         self.planet.add_path(((0, 0), Direction.EAST),
#                              ((1, 0), Direction.WEST), 1)
#         self.planet.add_path(((1, 0), Direction.NORTH),
#                              ((2, 2), Direction.SOUTH), 3)
#         self.planet.add_path(((0, 1), Direction.NORTH),
#                              ((0, 2), Direction.SOUTH), 1)
#         self.planet.add_path(((0, 2), Direction.EAST),
#                              ((2, 2), Direction.WEST), 2)
#         self.planet.add_path(((0, 3), Direction.NORTH),
#                              ((0, 3), Direction.WEST), 3)
#         self.planet.add_path(((0, 2), Direction.NORTH),
#                              ((0, 3), Direction.SOUTH), 1)
#         self.planet.add_path(((0, 3), Direction.EAST),
#                              ((2, 2), Direction.NORTH), 3)

#     # @unittest.skip('Example test, should not count in final test results')
#     def test_empty_planet(self):
#         # print(self.planet.get_paths())
#         self.assertIsNotNone(self.planet.get_paths())
#         self.assertNotEqual(self.planet.get_paths(), {})

#     def test_target_not_reachable_with_loop(self):
#         """
#         This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
#         searching for a target not reachable nearby

#         Result: Target is not reachable
#         """

#         # blocked paths
#         self.planet.add_path(((0, 2), Direction.NORTH),
#                              ((0, 3), Direction.SOUTH), -1)
#         self.planet.add_path(((0, 3), Direction.EAST),
#                              ((2, 2), Direction.NORTH), -1)

#         # print(self.planet.get_paths())
#         self.assertIsNone(self.planet.shortest_path((0, 0), (0, 3)))


# class testPlanetSimpleForIntegrity(unittest.TestCase):
#     def setUp(self):
#         self.planet = Planet()

#         self.planet.add_path(((0, 0), Direction.NORTH),
#                              ((0, 1), Direction.SOUTH), 1)
#         self.planet.add_path(((0, 1), Direction.EAST),
#                              ((1, 1), Direction.WEST), 1)

#     def test_integrity(self):
#         """
#         This test should check that the dictionary returned by "planet.get_paths()" matches the expected structure
#         """
#         expected = {
#             (0, 0): {
#                 Direction.NORTH: ((0, 1), Direction.SOUTH, 1)
#             },
#             (0, 1): {
#                 Direction.EAST: ((1, 1), Direction.WEST, 1),
#                 Direction.SOUTH: ((0, 0), Direction.NORTH, 1)
#             },
#             (1, 1): {
#                 Direction.WEST: ((0, 1), Direction.EAST, 1)
#             }
#         }

#         self.assertEqual(self.planet.get_paths(), expected)


# class TestRoboLabPlanet(unittest.TestCase):
#     def setUp(self):
#         """
#         Instantiates the planet data structure and fills it with paths

#         MODEL YOUR TEST PLANET HERE (if you'd like):

#         """
#         # Initialize your data structure here
#         self.RoboLabPlanet = Planet()

#         # self.planet.add_path(...)
#         self.RoboLabPlanet.add_path(
#             ((0, 0), Direction.NORTH), ((0, 1), Direction.SOUTH), 1)
#         self.RoboLabPlanet.add_path(
#             ((0, 0), Direction.EAST), ((1, 0), Direction.WEST), 1)
#         self.RoboLabPlanet.add_path(
#             ((0, 1), Direction.EAST), ((1, 2), Direction.SOUTH), 2)
#         self.RoboLabPlanet.add_path(
#             ((1, 0), Direction.EAST), ((2, 1), Direction.SOUTH), 2)
#         self.RoboLabPlanet.add_path(
#             ((1, 2), Direction.WEST), ((0, 2), Direction.EAST), 1)
#         self.RoboLabPlanet.add_path(
#             ((1, 2), Direction.NORTH), ((2, 4), Direction.WEST), 3)
#         self.RoboLabPlanet.add_path(
#             ((0, 2), Direction.WEST), ((0, 2), Direction.SOUTH), 2)
#         self.RoboLabPlanet.add_path(
#             ((2, 1), Direction.NORTH), ((2, 3), Direction.SOUTH), 2)
#         self.RoboLabPlanet.add_path(
#             ((2, 3), Direction.NORTH), ((2, 4), Direction.SOUTH), 1)
#         self.RoboLabPlanet.add_path(
#             ((0, 4), Direction.WEST), ((0, 4), Direction.EAST), 3)
#         self.RoboLabPlanet.add_path(
#             ((2, 4), Direction.NORTH), ((0, 4), Direction.NORTH), 4)

#     def test_empty_planet(self):
#         self.assertIsNotNone(self.RoboLabPlanet.get_paths())
#         self.assertNotEqual(len(self.RoboLabPlanet.get_paths()), 0)

#     def test_target(self):
#         """
#         This test should check that the shortest-path algorithm implemented works.

#         Requirement: Minimum distance is three nodes (two paths in list returned)
#         """
#         expected = [((0, 0), Direction.EAST), ((1, 0), Direction.EAST)]
#         self.assertEqual(self.RoboLabPlanet.shortest_path(
#             (0, 0), (2, 1)), expected)

#     def test_target_not_reachable(self):
#         """
#         This test should check that a target outside the map or at an unexplored node is not reachable
#         """
#         self.assertIsNone(self.RoboLabPlanet.shortest_path((0, 0), (99, 99)))

#     def test_same_length(self):
#         """
#         This test should check that the shortest-path algorithm implemented returns a shortest path even if there
#         are multiple shortest paths with the same length.

#         Requirement: Minimum of two paths with same cost exists, only one is returned by the logic implemented
#         """
#         shortest_path = self.RoboLabPlanet.shortest_path((0, 0), (2, 4))
#         expected1 = [((0, 0), Direction.EAST), ((1, 0), Direction.EAST),
#                      ((2, 1), Direction.NORTH), ((2, 3), Direction.NORTH)]
#         expected2 = [((0, 0), Direction.NORTH),
#                      ((0, 1), Direction.EAST), ((1, 2), Direction.NORTH)]

#         self.assertTrue(shortest_path ==
#                         expected1 or shortest_path == expected2)

#     def test_target_with_loop(self):
#         """
#         This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
#         searching for a target nearby

#         Result: Target is reachable
#         """
#         self.RoboLabPlanet.add_path(
#             ((2, 1), Direction.EAST), ((2, 3), Direction.EAST), 4)
#         # print(self.RoboLabPlanet.get_paths())
#         self.assertTrue(self.RoboLabPlanet.shortest_path((0, 0), (2, 4)))

#     def test_target_not_reachable_with_loop(self):
#         """
#         This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
#         searching for a target not reachable nearby

#         Result: Target is not reachable
#         """
#         # blocked paths
#         self.RoboLabPlanet.add_path(((0, 1), Direction.EAST),
#                                     ((1, 2), Direction.SOUTH), -1)
#         self.RoboLabPlanet.add_path(((2, 3), Direction.NORTH),
#                                     ((2, 4), Direction.SOUTH), -1)

#         # print(self.RoboLabPlanet.get_paths())
#         self.assertIsNone(self.RoboLabPlanet.shortest_path((0, 0), (2, 4)))
               
class TestExploringPlanet(unittest.TestCase):
    def setUp(self):
        self.planet = Planet()
        self.planet.add_path(((1, 1), Direction.NORTH),
                            ((1, 2), Direction.SOUTH), 1)
        self.planet.add_path(((1, 1), Direction.EAST),
                            ((2, 1), Direction.WEST), 1)
        self.planet.add_path(((2, 1), Direction.EAST),
                            ((3, 2), Direction.SOUTH), 2)
        self.planet.add_path(((3, 2), Direction.NORTH),
                            ((3, 4), Direction.SOUTH), 5)
        self.planet.add_path(((3, 4), Direction.NORTH),
                            ((3, 5), Direction.SOUTH), 1)
        self.planet.add_path(((1, 2), Direction.EAST),
                            ((2, 3), Direction.SOUTH), 2)
        self.planet.add_path(((2, 3), Direction.WEST),
                            ((1, 3), Direction.EAST), 1)
        self.planet.add_path(((2, 3), Direction.SOUTH),
                            ((3, 5), Direction.WEST), 22)
        self.planet.add_path(((3, 5), Direction.NORTH),
                            ((1, 5), Direction.NORTH), 1)
        


        self.planet.add_unknown_path({(1, 5): [(Direction.EAST, -2), (Direction.WEST, -2)]})
        self.planet.add_unknown_path({(3, 5): [(Direction.EAST, -1)]})
        self.planet.add_unknown_path({(1, 3): [(Direction.SOUTH, -2), (Direction.WEST, -2)]})

    # def test_able_to_go_direction(self):
    #     self.assertTrue(self.planet.able_to_go_direction((1, 5)))
    #     self.assertFalse(self.planet.able_to_go_direction((2, 3)))
    #     self.assertFalse(self.planet.able_to_go_direction((3, 5)))

    # def test_get_direction(self): 
    #     self.assertEqual(self.planet.get_direction((1, 5)), Direction.EAST)

    def test_explore_next_node(self):
        self.assertEqual(
            self.planet.explore_next_node((1, 1)), [((1, 1), Direction.NORTH),
                                                 ((1, 2), Direction.EAST),
                                                 ((2, 3), Direction.WEST)
                                                 ])
        self.assertEqual(
            self.planet.explore_next_node((3, 5)), [((3, 5), Direction.NORTH)])

        self.assertEqual(
            self.planet.explore_next_node((3, 4)), [((3, 4), Direction.NORTH), ((3, 5), Direction.NORTH)])



#   class ExploringNodes(unittest.TestCase):
#     def setUp(self):
#         self.nugget = Planet()
#         self.nugget.add_path(((0, 0), Direction.NORTH),
#                              ((0, 1), Direction.SOUTH), 1)
#         # 0,1 all known
#         self.nugget.add_path(((0, 1), Direction.NORTH),
#                              ((1, 0), Direction.SOUTH), 1)
#         self.nugget.add_path(((0, 1), Direction.EAST),
#                              ((1, 1), Direction.SOUTH), 1)
#         self.nugget.add_path(((0, 1), Direction.WEST),
#                              ((1, 1), Direction.SOUTH), 1)

#     def test_next_node(self):
#         self.assertFalse(self.nugget.able_to_go_direction((0, 0)))
#         self.assertNotEqual(
#             self.nugget.get_next_node((0, 0)), [((0, 0), Direction.NORTH)])


if __name__ == "__main__":
    unittest.main()



