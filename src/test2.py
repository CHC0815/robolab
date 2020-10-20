


def explore_next_node(self, node):
        # maybe there are no paths to discover
        if not self.unknownPaths: # and not self.unseenNodes
            print("Every node discovered. Exploring finished.")
            return None
        # creat graphToSearch
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
        # interesting_start_nodes.extend(self.unseenNodes)
        # print('interesting_start_nodes(unknown)+unseenNodes:')
        # print(interesting_start_nodes)
        graph = graphToSearch(graphList, node, interesting_start_nodes) # node is current start node
        logger.info("graphToSearch done.")
        target = graph.find_next_node()
        if target is not None:
            print("Found new target node:")
            print(target)
            return self.shortest_path(node, target)
        else:
            logger.warning("Something wrong.")
            return None


def find_next_node(self):
        queue = [[self.node]]
        print('queue:')
        print(queue)
        parent = {self.node : None}
        usedNodes = []
        
        while (len(queue) > 0):
            vertex = queue.pop(0)
            connections = self.graph[vertex]
            
            for u in connections:
                if u not in usedNodes:  
                    queue.append(u)
                    usedNodes.append(u)
                    parent[u] = vertex
            
                if u in ["A","B"]:
                    print(u)
                    return vertex,parent


            """
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
                if known in self.nodesWithUnknownPaths:
                    return known
            """

# graph = {'A': set(['B', 'C']),
#          'B': set(['A', 'D', 'E']),
#          'C': set(['A', 'F']),
#          'D': set(['B']),
#          'E': set(['B', 'F']),
#          'F': set(['C', 'E'])}

# def dfs(graph, start):
#     visited, stack = set(), [start]
#     while stack:
#         vertex = stack.pop()
#         if vertex not in visited:
#             visited.add(vertex)
#             stack.extend(graph[vertex] - visited)
#     return visited

# print(dfs(graph, 'A')) # {'E', 'D', 'F', 'A', 'C', 'B'}ass