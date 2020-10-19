#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
from enum import IntEnum, unique
from typing import List, Tuple, Dict, Union, DefaultDict
import logging
from heapq import heappop,heappush
from Communication import Communication
import time

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

    def __init__(self, robo): # robo = None
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
        self.robo = robo
        self.viewedNodes = set()
        self.unseenNodes = []
        self.graph = None

        self.target = None # node
        self.target_refresh = False # flag
        self.shortestPath = None # list
        self.exploringPath = None # list
        self.dir = None # direction
        self.dir_refresh = False # flag

    ####################################################################################################
    ####################################################################################################
    ####################################################################################################

    # adds unknown paths
    def add_unknown_path(self, node):
        """node like:
        {
            currentNode: [(Direction.NORTH, -2), (Direction.EAST, -1)]
        } Definition: -1 = blocked, -2 = path available
        example:
            add_unknown_path({(1, 5): [(Direction.EAST, -2), (Direction.WEST, -2)]})
        """
        key = list(node.keys())[0]
        unknown_paths = list(node.values())[0]      
        # remove -1 elements
        unknown_paths = [x for x in unknown_paths if -1 not in x]       
        new_unknown_paths = []       
        if unknown_paths :
            for element in unknown_paths:
                new_unknown_paths.append(element[0])
            self.unknownPaths.update({key: new_unknown_paths})
        # self.viewedNodes.add(key)
        print(self.unknownPaths)

    # direction with unknown path for node
    def get_direction(self, node):
        value = self.unknownPaths[node]
        # print(value)
        directionList = [Direction.EAST, Direction.SOUTH, Direction.WEST, Direction.NORTH]
        for di in directionList:
            if di in value:
                return di
         
    # returns path to next node from node
    def explore_next_node(self, node):
        # maybe there are no paths to discover
        if not self.unknownPaths: # and not self.unseenNodes
            logger.info("Every node discovered. Exploring finished.")
            return None
        # creat graphToSearch
        graphList = {}
        for key, value in self.paths.items():
            for targets in value.values():
                if key not in graphList and targets[2] > 0:
                    # add node to dict
                    graphList.update({key: [targets[0]]})
                elif key in graphList and targets[2] > 0:
                    # node in dict
                    graphList[key].append(targets[0])

        print('graphList:')
        print(graphList)
        interesting_start_nodes = list(self.unknownPaths.keys())
        print('interesting_start_nodes(unknown):')
        print(interesting_start_nodes)
        # interesting_start_nodes.extend(self.unseenNodes)
        # print('interesting_start_nodes(unknown)+unseenNodes:')
        # print(interesting_start_nodes)
        # graph = graphToSearch(graphList, node, interesting_start_nodes) # node is current start node
        # logger.info("graphToSearch done.")
        target = self.find_possible_node(graphList, node, interesting_start_nodes)
        if target:
            print("Found new target node:")
            print(target)
            return self.shortest_path(node, target)
        else:
            logger.warning("Wrong.")
            return None

    def find_possible_node(self, graph:dict, node:tuple, nodesWithUnknownPaths:list):
        """
        graph should look like:
        {
            node: [connectted node 1, connectted node 2, ...]
            ...
            ...
        }

        graph example:
            {(1, 1): [(1, 2), (2, 1)], (1, 2): [(1, 1), (2, 3)], ...}

        """
        # BFS
        queue = [node]
        print('queue:')
        print(queue)
        parent = {node : None}
        usedNodes = []
        
        while (len(queue) > 0):
            vertex = queue.pop(0)
            connections = graph[vertex]
            
            for u in connections:
                if u not in usedNodes:  
                    queue.append(u)
                    usedNodes.append(u)
                    parent[u] = vertex
            
                if u in nodesWithUnknownPaths: 
                    # print('parent(dict): ')
                    # print(parent)   
                    return u

    # check whether there are unknown directions for current node, return boolean
    def check_unknown_directions(self, node):
        self.clean_unknown_paths()
        if node in self.unknownPaths:
            logger.info("Discover unknown direction on current Node")
            return True
        else:
            logger.info("Run exploring next node.")
            return False

    def clean_unknown_paths(self):
    #    # format unknown paths, remove unknown paths which indeed known 
    #    if self.paths:
    #        for known_key, known_value in self.paths.items():
    #            known_directions = known_value.keys()
    #            # # append viewedNodes
    #            # if len(known_directions) == 4:
    #            #     self.viewedNodes.add(known_key)
    #            if known_key in self.unknownPaths:
    #                unknown_directions = self.unknownPaths[known_key]
    #                new_unknown_paths = [
    #                    item for item in unknown_directions
    #                    if item not in known_directions
    #                ]
    #                if new_unknown_paths:
    #                    self.unknownPaths[known_key] = new_unknown_paths
    #                else:
    #                    self.unknownPaths.pop(known_key)
    #                    
            # # regenerate list of unseenNodes, not already viewed
            # self.unseenNodes = [
            #     node for node in self.paths.keys()
            #     if node not in self.viewedNodes
            # ] 

    ####################################################################################################
    ####################################################################################################
    ####################################################################################################    
    #            send direction(where to go) to robo            #

    def set_direction(self, startDir):
        startDir = Direction(startDir)
        self.dir = startDir
        self.dir_refresh = True

    def set_target(self, targetX, targetY):
        target = (int(targetX), int(targetY))
        self.target = target
        self.target_refresh = True

    def directionToPathSelect(self, currentX, currentY):
        # this direction is sent to mother ship
        # check if there is a running shortestPath
        if self.target == (currentX, currentY):
            self.target = None
            logger.debug('Target reached!')
            self.robo.comm.send_target_completed('Done')
            time.sleep(3)
            return None

        if not self.shortestPath:
            # exploring, check if there is a running explored path
            if not self.exploringPath:
                # check if possible direction exists on current node
                if self.check_unknown_directions((currentX, currentY)):
                    # search possible direction on current node
                    goDirection = self.get_direction((currentX, currentY))
                else:
                    # go to a node with unknown path
                    self.exploringPath = self.explore_next_node((currentX, currentY))
                    print(self.exploringPath)
                    if self.exploringPath is None:
                        print('Exploring is done, and no nore nodes with unknown paths!')
                        self.robo.isRunning = True
                        goDirection = None
                    else:
                        goDirection = self.exploringPath[0][1]
            else:
                goDirection = self.exploringPath[0][1]
        else:
            goDirection = self.shortestPath[0][1]
        
        return goDirection


    def go_direction(self, currentX, currentY):
        goDir = self.directionToPathSelect(currentX, currentY)

        node = [currentX, currentY, goDir]
        self.robo.comm.sendPathSelect(node)
        time.sleep(3)
        
        if self.dir and self.dir_refresh:
            goDirection = self.dir
            self.dir_refresh = False
        else:
            # self.target maybe need as input
            # self.target_refresh should be controlled by the message somehow
            if self.target is not None and self.shortestPath is None and not self.target_refresh:
                print('current target: '+ str(self.target))
                path_possible = self.shortest_path(
                    (currentX, currentY), self.target)
                if path_possible :
                    self.shortestPath = path_possible
                    self.exploringPath = None
            # check existence of target and reachability
            elif self.target is not None and self.target_refresh:
                path_possible = self.shortest_path(
                    (currentX, currentY), self.target)
                if path_possible:
                    self.shortestPath = path_possible
                    self.exploringPath = None
                else:
                    self.shortestPath = None
                self.target_refresh = False
            # reached target
            if self.target == (currentX, currentY):
                self.target = None
                # print('Target reached!')
                return None
            # check if there is a running shortestPath
            if not self.shortestPath:
                # exploring, check if there is a running explored path
                if not self.exploringPath:
                    # check if possible direction exists on current node
                    if self.check_unknown_directions((currentX, currentY)):
                        # search possible direction on current node    
                        goDirection = self.get_direction((currentX, currentY))
                    else:
                        # go to a node with unknown path
                        self.exploringPath = self.explore_next_node((currentX, currentY))
                        if self.exploringPath is None:
                            
                            time.sleep(3)
                            logger.debug('Moin')
                            if not self.target == None:
                                logger.debug('servus')
                                path_possible = self.shortest_path((currentX, currentY), self.target)
                                if path_possible:
                                    logger.debug('moin 2')
                                    self.shortest_path = path_possible
                                    self.exploringPath = None
                                    goDirection = self.shortestPath.pop(0)[1]
                                    print('Direction on the current node:'+ str(goDirection))
                                    return goDirection

                            print('Exploring is done, and no nore nodes with unknown paths!')
                            goDirection = None
                        else:
                            goDirection = self.exploringPath.pop(0)[1]
                else:
                    goDirection = self.exploringPath.pop(0)[1]
            else:
                goDirection = self.shortestPath.pop(0)[1]


        node = [currentX, currentY, goDirection]
        self.robo.comm.sendPathSelect(node)
        time.sleep(3)
        
        print('Direction on the current node:'+ str(goDirection))
        return goDirection
       

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
        start_position = start[0]
        start_direction = start[1]
        end_position = target[0]
        end_direction = target[1]

        if (weight > 0) or (weight == -1):
            if start_position in self.paths:
                # start node already in dict
                # if start_direction not in self.paths[start_position]:
                #add new path
                self.paths[start_position].update(
                    {start_direction: (end_position, end_direction, weight)})
                logger.info("new path added")

            elif start_position not in self.paths:
                # start node unknown, then add it to dict 
                self.paths.update(
                    {start_position: {
                        start_direction: (end_position,
                                          end_direction, weight)
                    }})
                logger.info("new path added")

            if end_position in self.paths:
                # end node already in dict
                # if end_direction not in self.paths[end_position]:
                self.paths[end_position].update(
                    {end_direction: (start_position, start_direction, weight)})

            elif end_position not in self.paths:
                # end node unknown, add it to dict
                self.paths.update(
                    {end_position: {
                        end_direction: (
                            start_position, start_direction, weight)
                    }})

        # elif weight == -1:
        #     # if path is blocked, after scanning node again
        #     if start_position in self.paths:
        #         # node in dict
        #         self.paths[start_position].update(
        #             {start_direction: (end_position, end_direction, weight)})

        #     elif start_position not in self.paths:
        #         # add node to dict
        #         self.paths.update(
        #             {start_position: {
        #                 start_direction: (end_position,
        #                                   end_direction, weight)
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
                print('shortest Path in List:')
                print(shortestPathList)
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
        if startEnabled and targetEnabled and not (START == TARGET):
            logger.info("Start and target are the VALID elements of planet.")
            return True
        else:
            logger.warning("Start and target are NOT the valid elements of planet, start and target are equal.")
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

        return cost, pathReturn
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
    




