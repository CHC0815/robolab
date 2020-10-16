#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
from enum import IntEnum, unique
from typing import List, Tuple, Dict, Union, DefaultDict
import logging
from heapq import heappop,heappush
import random


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
        self.ripeGraphList = [] 
        self.visited = {}

        self.unknownPaths = {}
        """
        self.unknownPaths looks like
        {
            (0, 0): [Direction.NORTH, Direction.SOUTH, ...]
        }
        """
        self.scannedNodes = set()
        self.unseenNodes = []
        self.graph = None

    ####################################################################################################
    ####################################################################################################
    ####################################################################################################

    # adds unknown paths
    def add_unknown_paths(self, node):
        """node should look like:
        {
            currentNode: [(Direction.NORTH, -2), (Direction.EAST, -3)]
        } Definition: -1 = blocked, -2 = pathAvailable, -3 = noPath
        """
        key = list(node.keys())[0]
        print(key)
        unknown_paths = list(node.values())[0]
        print(unknown_paths)
        # filter list, remove -1 and - 3 elements
        unknown_paths = [x for x in unknown_paths if -1 not in x]
        unknown_paths = [x for x in unknown_paths if -3 not in x]
        new_unknown_paths = []
        for element in unknown_paths:
            new_unknown_paths.append(element[0])
        self.scannedNodes.add(key)
        self.unknownPaths.update({key: new_unknown_paths})
        print(self.unknownPaths)

    # direction with unknown path for node
    def get_direction(self, node):
        value = self.unknownPaths[node]
        return random.choice(value)

    # returns path to next node from node
    def get_next_node(self, node):
        # maybe there are no paths to discover
        if not self.unknownPaths and not self.unseenNodes:
            logger.info("Everything discovered. Finishing exploration.")
            return None
        logger.info("Performing graph creation...")
        graphList = {}
        for key, value in self.paths.items():
            for targets in value.values():
                if key in graphList and targets[2] > 0:
                    # node in dict
                    graphList[key].append(targets[0])

                elif key not in graphList and targets[2] > 0:
                    # add node to dict
                    graphList.update({key: [targets[0]]})

        print('graphList:')
        print(graphList)
        interesting_start_nodes = list(self.unknownPaths.keys())
        print('interesting_start_nodes(unknown):')
        print(interesting_start_nodes)
        interesting_start_nodes.extend(self.unseenNodes)
        print('interesting_start_nodes(unknown)+unseenNodes:')
        print(interesting_start_nodes)
        graph = SearchableGraph(graphList, node, interesting_start_nodes) # node is current start node
        logger.info("...done")
        target = graph.find_next_node()
        if target is not None:
            logger.info("Found new target node:")
            logger.info(target)
            return self.shortest_path(node, target)
        else:
            logger.warning("Function did not exit properly.")
            return None

    # check whether node is already scanned, return boolean
    def node_scanned(self, node):
        self.clean_unknown_paths()
        if node in self.scannedNodes:
            logger.info("Node already scanned.")
            return True
        else:
            logger.info("Node unknown. Please scan!")
            return False

    # check whether there are unknown directions for node, return boolean
    def able_to_go_direction(self, node):
        self.clean_unknown_paths()
        if node in self.unknownPaths:
            logger.info("Dicover Direction on current Node")
            return True
        else:
            logger.info("Go to other node")
            return False

    def clean_unknown_paths(self):
        if self.paths:

            for known_key, known_value in self.paths.items():
                known_directions = known_value.keys()
                # append scannedNodes
                if len(known_directions) == 4:
                    self.scannedNodes.add(known_key)
                if known_key in self.unknownPaths:
                    unknown_directions = self.unknownPaths[known_key]
                    new_unknown_paths = [
                        item for item in unknown_directions
                        if item not in known_directions
                    ]
                    if not new_unknown_paths:
                        self.unknownPaths.pop(known_key, None)
                    else:
                        self.unknownPaths[known_key] = new_unknown_paths
            # regen list of unseenNodes
            # criteria: not already scanned
            # and less than 4 edges
            self.unseenNodes = [
                node for node in self.paths.keys()
                if node not in self.scannedNodes
            ] 
   

    ####################################################################################################
    ####################################################################################################
    ####################################################################################################


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

        if (weight > 0) or (weight == -1):
            if start_coordinate in self.paths:
                # start node already in dict
                # if start_direction not in self.paths[start_coordinate]:
                #add new path
                self.paths[start_coordinate].update(
                    {start_direction: (target_coordinate, target_direction, weight)})
                logger.info("new path added")

            elif start_coordinate not in self.paths:
                # start node unknown, then add it to dict 
                self.paths.update(
                    {start_coordinate: {
                        start_direction: (target_coordinate,
                                          target_direction, weight)
                    }})
                logger.info("new path added")

            if target_coordinate in self.paths:
                # target node already in dict
                # if target_direction not in self.paths[target_coordinate]:
                self.paths[target_coordinate].update(
                    {target_direction: (start_coordinate, start_direction, weight)})

            elif target_coordinate not in self.paths:
                # target node unknown, add it to dict
                self.paths.update(
                    {target_coordinate: {
                        target_direction: (
                            start_coordinate, start_direction, weight)
                    }})

        # elif weight == -1:
        #     # if path is blocked, after scanning node again
        #     if start_coordinate in self.paths:
        #         # node in dict
        #         self.paths[start_coordinate].update(
        #             {start_direction: (target_coordinate, target_direction, weight)})

        #     elif start_coordinate not in self.paths:
        #         # add node to dict
        #         self.paths.update(
        #             {start_coordinate: {
        #                 start_direction: (target_coordinate,
        #                                   target_direction, weight)
        #             }})
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
        logger.info("Shortest path requested")
        # create graph
        logger.info("Creating known graph...")
        graphList = []
        for key, value in self.paths.items():
            for pathElement in value.values():
                # remove blocked(invalid) paths by requirement(weight>0), ensure graph valid
                if pathElement[2] > 0: 
                    edge = [key, pathElement[0], pathElement[2]]
                    graphList.append(edge)
        """
        edge looks like:

        startNode   targetNode   weight
        --------------------------------
        (0,0)       (1,0)        1
        """
        # remove loops, and processing graph list useful
        self.ripeGraphList = self.removeLoops(graphList)
        logger.info("ripe graph:")
        # self.printGraphList(self.ripeGraphList)
        logger.info("...(ripe graph) created done.")

        # check if start and target in graph
        # true, begin shortest_path algorithm
        # false, path invalid
        if self.pathAccessible(start, target):
            # graph_edges->graph_dict
            ripeGraphDict = DefaultDict(list)
            for head, tail, weight in self.ripeGraphList:
                ripeGraphDict[head].append((tail,weight))
            # dijkstra computes shortest path
            shortestDisValue, shortestPathInNodeForm = self.dijkstra(ripeGraphDict,start,target)
 
            if len(shortestPathInNodeForm):
                print('shortest distence value:')
                print(shortestDisValue)
                logger.info('shortest Path in Node:')
                logger.info(shortestPathInNodeForm)
                # format path node form to list form
                shortestPathList = self.nodeFormToListForm(shortestPathInNodeForm)
                logger.info('shortest Path in List:')
                logger.info(shortestPathList)
                # format path list to required form: 
                # such as [((0, 0), <Direction.NORTH: 0>), ((0, 1), <Direction.NORTH: 0>), ...]
                shortestPath= self.listFormToRequiredForm(shortestPathList)
                print("Shortest Path:")
                print(shortestPath)
                return shortestPath
            else:
                logger.warning("target node: " + str(target)+" in NOT full connected graph, checked already in dijkstra")
                return None
        
        else:
            logger.warning("Path invalid.")
        return None

    ####################################################################################################
    def printGraphList(self, GRAPHLIST:[]):
        for element in GRAPHLIST:
            print(element)
    ####################################################################################################
    def removeLoops(self, rawGraphList:[]):
        # remove loop in one point
        ripeGraphList0 = []
        for element in rawGraphList:
            if element[0] == element[1]:
                logger.info("Detected loop in one point:")
                logger.info(element)
            else:
                ripeGraphList0.append(element)
        # remove loops between two points:
        # 1. remove the paths between two points with equal weight
        ripeGraphList1 = []
        [ripeGraphList1.append(item) for item in ripeGraphList0 if not item in ripeGraphList1]
        # 2. if the paths' weight(path num>=2) unequal, keep the smaller one, erase the paths with bigger weight
        toRemoveList0 = []
        for i, elem0 in enumerate(ripeGraphList1):
            current_edge = elem0
            for j, elem1 in enumerate(ripeGraphList1):
                if j>i:
                    if (current_edge[0] == elem1[0]) and (current_edge[1] == elem1[1]): 
                        if current_edge[2]<elem1[2]:
                            toRemoveList0.append(elem1)
                        else:
                            toRemoveList0.append(current_edge)
        toRemoveList1 = []
        [toRemoveList1.append(item) for item in toRemoveList0 if not item in toRemoveList1]
        for i in toRemoveList1:
            for j in ripeGraphList1:
                if j == i:
                    ripeGraphList1.remove(j)
        # print('... Final ripe graph list without any loop ... ... generated!')
        # print(ripeGraphList1)
        return ripeGraphList1
    ####################################################################################################
    def pathAccessible(self, START: Tuple[int, int], TARGET: Tuple[int, int]):
        startEnabled = False
        targetEnabled = False
        for edge in self.ripeGraphList:
            if edge[0] == START:
                startEnabled = True
            if edge[0] == TARGET:
                targetEnabled = True
        if startEnabled and targetEnabled:
            logger.info("Start and target are the VALID elements of planet.")
            return True
        else:
            logger.warning("Start and target are NOT the valid elements of planet.")
            return False
       
    ####################################################################################################
    def dijkstra(self, graph_dict:DefaultDict, start_node:Tuple[int, int], target_node:Tuple[int, int]):
    
        cost = -1
        pathReturn=[]
        q, visited = [(0,start_node,())], []
        while q:
            (cost,p1,path) = heappop(q)
            if p1 not in visited:
                visited.append(p1)
                path = (p1, path)
                if p1 == target_node: # find the target_node
                    break
                for p2,weight in graph_dict.get(p1):
                    if p2 not in visited:
                        heappush(q, (cost+weight, p2, path))

        # Check if reach the target exactly
        if p1 != target_node:
            print("The garph can not reach to target_node: " + str(target_node)+", Not full connected graph")
            cost = -1
            pathReturn=[]
        else:
            # if there is a path from start_node to target_node, then format the path
            if len(path)>0:
                left = path[0]
                pathReturn.append(left)
                right = path[1]
                while len(right)>0:
                    left = right[0]
                    pathReturn.append(left)
                    right = right[1]
                pathReturn.reverse()
        
        logger.info('cost: ' + str(cost))
        logger.info('shortest path shown in dijkstra: ' + str(pathReturn))

        return cost,pathReturn
    ####################################################################################################
    def nodeFormToListForm(self, nodeForm):
        shortestPathList=[]
        for i in range(len(nodeForm)):
            if i+1<len(nodeForm):
                for elem1 in self.ripeGraphList:               
                    if nodeForm[i] == elem1[0] and nodeForm[i+1] == elem1[1]:
                        shortestPathList.append(elem1)
                    
        return shortestPathList
    ####################################################################################################
    def listFormToRequiredForm(self, PathList:[]):
        shortestPath = []
        for edge in PathList:
            infoDict = self.paths[edge[0]]
            weight = {}
            for key, values in infoDict.items():
                if edge[1] in values:
                    weight.update({values[2]: key})
            weightToCompare=[]
            for d in weight.items():
                weightToCompare.append(d[0])
            shortestPath.append((edge[0], weight[min(weightToCompare)]))
        
        return shortestPath
    
    ####################################################################################################
    ####################################################################################################
    ####################################################################################################
    

class SearchableGraph:
    def __init__(self, graph, node, unknown):
        self.graph = graph
        """
        graph should look like:
        {
            node: [nodes, connected, to]
        }
        """
        self.node = node
        self.unknown = unknown
        self.logger = logging.getLogger('SearchableGraph')
        logging.basicConfig(level=logging.DEBUG)

    def find_next_node(self):
        queue = [[self.node]]
        print('queue:')
        print(queue)
        usedNodes = []
        foundNode = True
        level = 1
        nextNodeElement = 0
        while foundNode:
            # check available paths in level
            if not queue[nextNodeElement]:
                nextNodeElement += 1
                level += 1
            # set next node
            try:
                nextNode = queue[nextNodeElement].pop()
                print('nextNode:')
                print(nextNode)
                usedNodes.append(nextNode)
                print('usedNodes')
                print(usedNodes)
            except IndexError:
                self.logger.error(
                    "There are undiscovered directions, but they are not reachable!"
                )
                return None
            # get nodes from this node
            value = self.graph[nextNode]
            print('value:')
            print(value)
            # filter nodes - you shouldnt go back
            value = [
                unknown_node for unknown_node in value
                if unknown_node not in usedNodes
            ]
            print('value after filter:')
            print(value)
            
            try:
                known_data = queue[level]
                print(known_data)
                for element in value:
                    known_data.append(element)
                queue[level] = known_data
                
                # dann erweitern
            except IndexError:
                queue.append(value)
            print(queue)
            # if one of these nodes is missing return it
            # else keep on searching
            for known in queue[level]:
                # known node has unknown directions
                if known in self.unknown:
                    return known



