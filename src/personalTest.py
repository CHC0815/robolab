# 'A = [(15,37),(15,39),1]
# B = [(15,39),(17,37),1]
# C = [(15,37),(15,39),4]

# D_new = [[(15,37),(15,39),1],[(15,39),(17,37),1],[(17,37),(15,44),4],[(15,37),(15,39),3],[(15,37),(15,39),7]]



# E=[]

# for i, value0 in enumerate(D_new):
#     current = value0
#     for j, value1 in enumerate(D_new):
#         if j>i:
#             if (current[0] == value1[0]) and (current[1] == value1[1]): 
#                 if current[2]<value1[2]:
#                     E.append(value1)
#                 else:
#                     E.append(current)

# print(E)

# F = []

# for i, remove0 in enumerate(E):
#     if remove0 not in F:
#         F.append(remove0)

# print (F)

# # for i, remove0 in enumerate(E):
# #     if i == 0: 
# #         F.append(remove0)
# #     for j, remove1 in enumerate(E):
# #         if j>i:
# #             if remove0 == remove1:
# #                 print('A')
# #             else: 
# #                 F.append(remove0)

# for i, value in enumerate(F):
#     for value3 in D_new:
#         if value == value3:
#             D_new.remove(value)

# print(D_new)
            


# # new = set.union(A[0],B[0],C[0])
# # print(new)'

# def startwith(start: int, target: int,  mgraph: list):
#     passed = [start]
#     nopass = [x for x in range(len(mgraph)) if x != start]
#     # print(nopass)
#     dis = mgraph[start]
#     path0 = []
#     path1 = []

#     while len(nopass):
#         idx = nopass[0]
#         for i in nopass:
#             if dis[i] < dis[idx]: idx = i

#         nopass.remove(idx)
#         passed.append(idx)
        
#         for i in nopass:
#             if dis[idx] + mgraph[idx][i] < dis[i]: 
#                 dis[i] = dis[idx] + mgraph[idx][i]
#                 path0.append(idx)
#                 # print(dis[i])
#                 print(path0)
#                 path1.append(i)
#                 print(path1)

#         if target == idx:
#             print('find target!')
#             print(passed)
#             print(dis)
#     return dis


# if __name__ == "__main__":
#     inf = 10086
#     mgraph = [[0, 1, 12, inf, inf, inf],
#               [1, 0, 9, 3, inf, inf],
#               [12, 9, 0, inf, 5, inf],
#               [inf, 3, inf, 0, 13, 15],
#               [inf, inf, 5 ,13, 0, 4],
#               [inf, inf, inf, 15 ,4, 0]]

#     dis = startwith(1,4, mgraph)
#     # print (dis)

# nodes = ('A', 'B', 'C', 'D', 'E', 'F', 'G')
# distances = {
#     'B': {'A': 5, 'D': 1, 'G': 2},
#     'A': {'B': 5, 'D': 3, 'E': 12, 'F' :5},
#     'D': {'B': 1, 'G': 1, 'E': 1, 'A': 3},
#     'G': {'B': 2, 'D': 1, 'C': 2},
#     'C': {'G': 2, 'E': 1, 'F': 16},
#     'E': {'A': 12, 'D': 1, 'C': 1, 'F': 2},
#     'F': {'A': 5, 'E': 2, 'C': 16}}

# unvisited = {node: None for node in nodes} #把None作为无穷大使用
# visited = {}#用来记录已经松弛过的数组
# current = 'B' #要找B点到其他点的距离
# currentDistance = 0
# unvisited[current] = currentDistance#B到B的距离记为0

# while True:
#     for neighbour, distance in distances[current].items():
#         if neighbour not in unvisited: continue#被访问过了，跳出本次循环
#         newDistance = currentDistance + distance#新的距离
#         if unvisited[neighbour] is None or unvisited[neighbour] > newDistance:#如果两个点之间的距离之前是无穷大或者新距离小于原来的距离
#             unvisited[neighbour] = newDistance#更新距离
#     visited[current] = currentDistance#这个点已经松弛过，记录
#     del unvisited[current]#从未访问过的字典中将这个点删除
#     if not unvisited: break#如果所有点都松弛过，跳出此次循环
#     candidates = [node for node in unvisited.items() if node[1]]#找出目前还有拿些点未松弛过
#     current, currentDistance = sorted(candidates, key = lambda x: x[1])[0]#找出目前可以用来松弛的点

#     print (current)

#########################################################################################################

# successful, but do not want to use!

from heapq import heappop,heappush
from typing import List, Tuple, Dict, Union,DefaultDict



def dijkstra(graph_dict, from_node, to_node):

    cost = -1
    ret_path=[]
    q, seen = [(0,from_node,())], []
    while q:
        (cost,v1,path) = heappop(q)
        if v1 not in seen:
            seen.append(v1)
            path = (v1, path)
            if v1 == to_node: # Find the to_node!!!
                break;
            for v2,weight in graph_dict.get(v1):
                if v2 not in seen:
                    heappush(q, (cost+weight, v2, path))

    # Check the way to quit 'while' loop!!!
    if v1 != to_node:
        print("There is no node: " + str(to_node))
        cost = -1
        ret_path=[]

    else:

        # IF there is a path from from_node to to_node, THEN format the path!!!
        if len(path)>0:
            left = path[0]
            ret_path.append(left)
            right = path[1]
            while len(right)>0:
                left = right[0]
                ret_path.append(left)
                right = right[1]
            ret_path.reverse()

    print('cost: ' + str(cost))
    print('shortest path shown in dijkstra: ' + str(ret_path))
    return cost,ret_path

def nodeFormToListForm(nodeForm,graph_edges):
    shortestPathList=[]
    for i in range(len(nodeForm)):
        if i+1<len(nodeForm):
            for elem1 in graph_edges:               
                if nodeForm[i] == elem1[0] and nodeForm[i+1] == elem1[1]:
                    shortestPathList.append(elem1)
    
    return shortestPathList


if __name__ == "__main__":
    inf = 10086
    nodes = ['A','B','C','D','E','F']
    mgraph = [[0, 1, 12, inf, inf, inf],
            [1, 0, 9, 3, inf, inf],
            [12, 9, 0, inf, inf, inf],
            [inf, 3, inf, 0, inf, inf],
            [inf, inf, inf ,inf, 0, 4],
            [inf, inf, inf, inf ,4, 0]]

    graph_edges = []
    for i in nodes:
        for j in nodes:
            if i!=j and mgraph[nodes.index(i)][nodes.index(j)]!=inf:
                graph_edges.append((i,j,mgraph[nodes.index(i)][nodes.index(j)]))
    print(graph_edges)

    # graph_edges->graph_dict
    graph_dict0 = DefaultDict(list)
    for tail,head,cost in graph_edges:
        graph_dict0[tail].append((head,cost))

    # graph_dict0 = {
    # 's1':[('s2',1),('s3',1),('s4',1)],
    # 's2':[('s1',1), ('s4',1)],
    # 's3':[('s1',1), ('s4',1)],
    # 's4':[('s1',1),('s2',1),('s3',1)],
    # }
    a1,a2=dijkstra(graph_dict0,'C','E')

    print(nodeFormToListForm(a2,graph_edges))

    if len(a2):
        print('aaaaaaaaaaaaaaaaaaa')
    else:
        print('bbbbbbbbbbbbbbbbbb')
    
    

