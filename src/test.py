graph = {
    "A":["B", "C"],   # 与A相连的节点是B,C 
    "B":["A", "C", "D"], # 与B相连的节点是A,C,D
    "C":["A", "B", "D", "E"],
    "D":["B", "C", "E", "F"],
    "E":["C", "D"],
    "F":["D"]
 }

def BFS(graph, s):
    queue = []  # 初始化一个空队列
    queue.append(s) # 将所有节点入队列
    seen = set()
    seen.add(s)
    parent = {s : None}

    while(len(queue) > 0):
        vertex = queue.pop(0)
        nodes = graph[vertex]
        for w in nodes:
            if w not in seen:
                queue.append(w)
                seen.add(w)
                parent[w] = vertex
        
            if w in ["A","B"]:
                print(w)
                return vertex,parent
            
    # return parent

vertex, parent = BFS(graph, "E")
for key in parent:
    print(key, parent[key])


def DFS(graph, s):
    stack = []
    stack.append(s)
    queue=[s]
    seen = set()
    
    # parent = {s : None}
    # lastVertex = None
    while(len(stack) > 0):
        vertex = stack.pop()    
        if vertex not in seen:           
            seen.add(vertex)
            nodes = set(graph[vertex])
            diff = nodes-seen
            stack.extend(diff)
            queue.extend(diff)
            
            for i in diff:
                if i in ["E"]:
                    print(i)
                    print(queue)
                    print(seen)

                    return i
            


# i=DFS(graph, "A")
# print(i)


# vertex, parent = BFS(graph, "E")
# for key in parent:
#     print(key, parent[key])