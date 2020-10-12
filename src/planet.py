#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
from enum import IntEnum, unique
from typing import List, Tuple, Dict, Union
import logging

logger = logging.getLogger('Planet')


@unique
class Direction(IntEnum):
    """ Directions in shortcut """
    NORTH = 0
    EAST = 90
    SOUTH = 180
    WEST = 270


Weight = int
"""
Weight of a given path (received from the server)

Value:  -1 if blocked path
        >0 for all other paths
        never 0
"""


class Planet:
    """
    Contains the representation of the map and provides certain functions to manipulate or extend
    it according to the specifications
    """

    def __init__(self):
        """ Initializes the data structure """
        self.paths = {}

    def add_path(self, start: Tuple[Tuple[int, int], Direction], target: Tuple[Tuple[int, int], Direction],
                 weight: int):
        """
         Adds a bidirectional path defined between the start_directiond end coordinates to the map and assigns the weight to it

        Example:
            add_path(((0, 3), Direction.NORTH), ((0, 3), Direction.WEST), 1)
        :param start_direction-Tuple
        :param target:  2-Tuple
        :param weight: Integer
        :return: void
        """

        # YOUR CODE FOLLOWS (remove pass, please!)
        start_coordinate = start[0]
        start_direction = start[1]
        target_coordinate = target[0]
        target_direction = target[1]

        if weight > 0:
            if start_coordinate in self.paths:
                # node in dict
                if start_direction not in self.paths[start_coordinate]:
                    self.paths[start_coordinate].update(
                        {start_direction: (target_coordinate, target_direction, weight)})
                    logger.info("new path added")

            elif start_coordinate not in self.paths:
                # add node to dict
                self.paths.update(
                    {start_coordinate: {
                        start_direction: (target_coordinate,
                                          target_direction, weight)
                    }})
                logger.info("new path added")

            if target_coordinate in self.paths:
                # node in dict
                if target_direction not in self.paths[target_coordinate]:
                    self.paths[target_coordinate].update(
                        {target_direction: (start_coordinate, start_direction, weight)})

            elif target_coordinate not in self.paths:
                # add node to dict
                self.paths.update(
                    {target_coordinate: {
                        target_direction: (
                            start_coordinate, start_direction, weight)
                    }})

        elif weight == -1:
            # if path is blocked, after scanning node again
            if start_coordinate in self.paths:
                # node in dict
                self.paths[start_coordinate].update(
                    {start_direction: (target_coordinate, target_direction, weight)})

            elif start_coordinate not in self.paths:
                # add node to dict
                self.paths.update(
                    {start_coordinate: {
                        start_direction: (target_coordinate,
                                          target_direction, weight)
                    }})
        else:
            logger.error("Path could not be added!")

    def get_paths(self):
        """
        Returns all paths

        -> Dict[Tuple[int, int], Dict[Direction, Tuple[Tuple[int, int], Direction, Weight]]]

        Example:
            {
                (0, 3): {
                    Direction.NORTH: ((0, 3), Direction.WEST, 1),
                    Direction.EAST: ((1, 3), Direction.WEST, 2),
                    Direction.WEST: ((0, 3), Direction.NORTH, 1)
                },
                (1, 3): {
                    Direction.WEST: ((0, 3), Direction.EAST, 2),
                    ...
                },
                ...
            }
        :return: Dict
        """

        # YOUR CODE FOLLOWS (remove pass, please!)
        return self.paths

    def shortest_path(self, start: Tuple[int, int], target: Tuple[int, int]):
        """
        Returns a shortest path between two nodes

        -> Union[None, List[Tuple[Tuple[int, int], Direction]]]:

        Examples:
            shortest_path((0,0), (2,2)) returns: [((0, 0), Direction.EAST), ((1, 0), Direction.NORTH)]
            shortest_path((0,0), (1,2)) returns: None
        :param start: 2-Tuple
        :param target: 2-Tuple
        :return: 2-Tuple[List, Direction]
        """

        # YOUR CODE FOLLOWS (remove pass, please!)
        shortestPath = []
        





