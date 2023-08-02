from collections import deque

def maxThroughput(connections, maxIn, maxOut, origin, targets):
    """
    Find the maximum possible data that can be throughput from the origin to 
    the targets, i.e. the maximum flow using Ford Fulkerson with BFS
    
    Approach Description:
    I have chosen to directly created a residual network instead of a flow 
    network first since we are only concern about the maximum flow. 

    In the residual network, there is a forward edge and a backward edge. The
    forward edge represents the remaining capacity and the backward edge 
    represents the flow that can be cancelled. When initializing the residual
    network, the forward edge is initially set to the original capacity of the
    edge and the backward edge is initially set to 0. This is because there is
    no flow yet. 
    
    For every vertex (data centre), there is a maximum incoming data and a 
    maximum outgoing data that the vertex can accept. This is similar to the 
    Week 9 Tutorial Problem 8. For each vertex V, I have created two new 
    vertices Vin and Vout. The Vin to V will have an edge which is initially 
    set to the maximum incoming data that V can accept. The V to Vout will have 
    an edge which is initially set to the maximum outgoing data that V can 
    accept. All the incoming edges to V will now connect to Vin instead of V. 
    This is because there is a limit of incoming data that a data centre can 
    process. All the outgoing edges from V will now connect from Vout to the 
    corresponding destination vertices. This is because there is a limit of 
    outgoing data that a data centre can process. 

    I have created a super target where all the targets will connect to the
    super target, referring to the Week 9 Tutorial Problem 5 solution. This is 
    because Ford Fulkerson works only for single source and single target. Each
    target has an edge to the super target which is initially set to the
    maximum incoming data that the target can accept. It is not the maximum 
    outgoing data that the target can accept because we want the maximum flow
    from the origin to the targets. The amount of outgoing data that a data
    centre can process only matters when the data centre is trasferring the 
    data to other data centres. 

    This is also why we run Ford Fulkerson from the source/origin to the super 
    target, and not from the Vin of the source to the super target. It is 
    because the amount of incoming data that a data centre can process only 
    matters when the data centre is accepting data from other data centres. 

    :Input: 
        connections: a list of tuples (a,b,t) where a is the data centre ID 
                     where the channel departs, b is the data centre ID where 
                     the channel arrives and t is the maximum throughput of 
                     the channel, i.e. the capacity
        maxIn: a list of integers where maxIn[i] is the maximum incoming data 
               that the data centre i can accept
        maxOut: a list of integers where maxOut[i] is the maximum outgoing data
                that the data centre i can accept
        origin: an integer that represents the data centre ID where the data 
                transfer begins
        targets: a list of integers which each corresponds to a data centre ID
                 where the data transfer ends

    :Output/Return: an integer that represents the maximum possible data that 
                    can be throughput from the source to the sink, i.e. the 
                    maximum flow of the residual network

    :Time complexity: O(|D|*|C|^2) + O(|D|^2) = O(|D|*|C|^2) where D is the 
                      number of data centres and C is the number of 
                      communication channels
    :Aux space complexity: O(|D|+|C|) + O(|D|) = O(|D|+|C|)
    """
    # total number of data centres
    total_centre = len(maxIn)

    preprocessed_connections = []

    # add a new node, Vin for each data centre V
    for i in range(len(maxIn)):
        u = i + total_centre
        v = i
        w = maxIn[i]

        # add forward edge from Vin to V
        preprocessed_connections.append((u,v,w))

        # add backward edge from V to Vin
        preprocessed_connections.append((v,u,0))

    # add a new node, Vout for each data centre V
    # O(|D|^2)
    for i in range(len(maxOut)):
        u = i
        v = i + (total_centre*2)
        w = maxOut[i]

        # add forward edge from V to Vout
        preprocessed_connections.append((u,v,w))

        # add backward edge from Vout to V
        preprocessed_connections.append((v,u,0))
    
    for i in range(len(connections)):
        u = connections[i][0] + (total_centre * 2)
        v = connections[i][1] + total_centre
        w = connections[i][2]

        # add forward edge from the departure data centre to the arrival data
        # centre
        preprocessed_connections.append((u,v,w))

        # add backward edge from the arrival data centre to the departure data
        # centre
        preprocessed_connections.append((v,u,0))
    
    # add a new node, super target
    # all targets will connect to this node
    for i in range(len(targets)):
        u = targets[i]
        v = total_centre * 3
        w = maxIn[targets[i]]

        # add forward edge from target to super target
        preprocessed_connections.append((u,v,w))

        # add backward edge from super target to target
        preprocessed_connections.append((v,u,0))

    # create the residual network
    # O(|D|+|C|) aux space
    graph = Graph(preprocessed_connections, total_centre*3+1)

    # find the maximum possible data that can be throughput from the source to 
    # the super target, i.e. the maximum flow
    # O(|D|*|C|^2) time and O(|D|) aux space
    return graph.fordFulkerson(origin, total_centre*3)

"""
A class represents a residual network

I have referred to the implementation of Graph class shown in the recording
Lecture04 P1 Graph BFS DFS Lecture05 P1 Dijkstra
"""
class Graph:
    def __init__(self, connections, total_vertices):
        """
        Create a Graph object, i.e. a residual network 

        According to the assignment specification, we should not assume that 
        the graph is always dense. Hence, I have chosen to use adjacency list
        instead of adjacency matrix because adjacency list is more efficient 
        when the graph is sparse whereas adjacency matrix is more efficient
        when the graph is dense.

        :Input:
            self: a reference to the Graph object
            connections: a list of tuples (a,b,t) where a is the data centre
                         ID where the channel departs, b is the data centre ID
                         where the channel arrives and t is the maximum 
                         throughput of the channel
            total_vertices: an integer that represents the total number of data
                            centres
        
        :Output/Return: -

        :Time complexity: O(|D|+|C|) 
        :Aux space complexity: O(|D|+|C|) because a list of size |D| is created
                               to store |D| number of data centres and each 
                               centre has at most |C| channels
        """
        # create an adjacency list
        # O(|D|) aux space
        self.vertices = [None] * total_vertices
        
        # add vertices to the graph
        # O(|D|) time
        for i in range(total_vertices):
            self.vertices[i] = Vertex(i)

        # add edges to the graph
        # O(|C|) time
        for connection in connections:
            u = connection[0]
            v = connection[1]
            w = connection[2]
            
            edge = Edge(u,v,w)
            self.vertices[u].add_edge(edge)

    def hasAugmentingPath(self, source, sink):
        """
        Check if there is an augmenting path from the source to the sink using
        BFS

        I have referred to the implementation of BFS shown in the recording
        Lecture04 P1 Graph BFS DFS Lecture05 P1 Dijkstra, Week 4: Introduction
        to Graphs slide 65, and the documentation of deque in 
        https://docs.python.org/3/library/collections.html#collections.deque.

        :Input:
            self: a reference to the Graph object
            source: the vertex ID where the flow begins
            sink: the vertex ID where the flow ends

        :Output/Return: True if there is an augmenting path from the source to
                        the sink, otherwise False

        :Time complexity: O(|D|+|C|)
        :Aux space complexity: O(|D|)
        """
        # initialize the queue
        queue = deque()

        # add the source to the queue
        queue.append(self.vertices[source])

        while len(queue) > 0:
            
            # serves the first vertex in the queue
            # O(1) time
            u = queue.popleft()         # BFS is FIFO

            u.visited = True

            # if reach the sink,
            # this means that there is a path from source to sink
            if u.id == sink:
                return True

            # for every adjacency vertex of u
            for edge in u.edges:
                v = edge.v
                v = self.vertices[v]

                if v.discovered == False and edge.w > 0:
                    v.discovered = True
                    v.previous = u      # for backtracking
                    queue.append(v)

        return False
    
    def getAugmentingPath(self, source, sink):
        """
        Get the augmenting path from the source to sink, and the minimum 
        residual capacity of the path

        :Input:
            self: a reference to the Graph object
            source: the vertex ID where the flow begins
            sink: the vertex ID where the flow ends

        :Output/Return: True if there is an augmenting path from the source to
                        the sink, otherwise False

        :Time complexity: O(|D|+|C|)
        :Aux space complexity: O(|D|)
        """
        path = []
        current = sink
        smallest_value = -1

        # backtrack to obtain the path from sink to source
        # BFS is already performed in the hasAugmentingPath method
        while current != source:
            path.append(current)
            previous = current
            current = self.vertices[current].previous.id

            # find the residual capacity 
            for edge in self.vertices[current].edges:
                if edge.v == previous:

                    # check if it is the minimum
                    if smallest_value == -1:
                            smallest_value = edge.w
                    else:
                        if edge.w < smallest_value:
                            smallest_value = edge.w

        path.append(source)

        # reverse the path
        for i in range(len(path)//2):
            path[i], path[len(path)-i-1] = path[len(path)-i-1], path[i]

        return path, smallest_value

    def fordFulkerson(self, source, sink):
        """
        Find the maximum flow in the residual network from the source to the 
        sink

        I have referred to the implementation of Ford Fulkerson shown in the 
        lecture slide Lecture08_NetworkFlow

        Approach Description:
        I have used BFS to find the augmenting path instead of using DFS. This
        is because using BFS reduced the time complexity from O(|C|*f) to
        O(|D|*|C|^2). 

        :Input:
            self: an reference to the Graph object
            source: the vertex ID where the flow begins
            sink: the vertex ID where the flow ends

        :Output/Return: an integer that represents the maximum possible data 
                        that can be throughput from the source to the sink,
                        i.e. the maximum flow of the residual network

        :Time complexity: O(|D|*|C|^2)
        :Aux space complexity: O(|D|)
        """
        flow = 0

        # repeat until there is no augmenting path from source to sink
        while self.hasAugmentingPath(source, sink):

            # find augmenting path and minimum residual capacity of the path 
            path, smallest_value = self.getAugmentingPath(source, sink)

            # update the flow
            flow += smallest_value

            # update residual network
            for i in range(1, len(path)-1):
                v = self.vertices[path[i]]
                u = v.previous

                # update the residual capacity, i.e. the forward edge
                for edge in u.edges:
                    if edge.v == v.id:
                        edge.w -= smallest_value
                        break

                # update the flow that can be cancelled, i.e. the backword edge
                for edge in v.edges:
                    if edge.v == u.id:
                        edge.w += smallest_value
                        break

            # reset visited, discovered and previous
            for vertex in self.vertices:
                vertex.discovered = False
                vertex.visited = False
                vertex.previous = None

        # return the maximum flow
        return flow

    def __str__(self):
        """
        Display the residual network

        :Input:
            self: a reference to the Vertex object
        
        :Output/Return: a string containing all the data centres and 
                        communication channels in the network

        :Time complexity: O(|D|*|C|) because there are |D| data centres
        :Aux space complexity: O(1)
        """
        return_string = ""
        for vertex in self.vertices:
            return_string = return_string + str(vertex) + "\n"
        return return_string

"""
A class represents a vertex, i.e an data centre in a residual network

I have referred to the implementation of Vertex class shown in the recording
Lecture04 P1 Graph BFS DFS Lecture05 P1 Dijkstra
"""
class Vertex:
    def __init__(self, id):
        """
        Create a new Vertex object

        :Input:
            self: a reference to the Vertex object
            id: an unique identifier for the Vertex object

        :Output/Return: -

        :Time complexity: O(1)
        :Aux space complexity: O(1)
        """
        self.id = id
        self.edges = []
        self.discovered = False
        self.visited = False
        self.previous = None

    def add_edge(self, new_edge):
        """
        Add a edge from a Vertex to its adjacent vertex
        
        :Input:
            self: a reference to the Vertex object

        :Output/return: -

        :Time complexity: O(1)
        :Aux space complexity: O(1)
        """
        self.edges.append(new_edge)

    def __str__(self):
        """
        Display the vertex

        :Input:
            self: a reference to the Vertex object

        :Output/return: a string containing the id of the Vertex and its 
                        adjacent vertices

        :Time complexity: O(|C|) because a Vertex can have at most |C| edges
        :Aux space complexity: O(1)
        """
        output_string = "Centre " + str(self.id) + "\n"
        if len(self.edges) > 0:
            for edge in self.edges:
                output_string += str(edge) + "\n"
        return output_string

"""
A class represents an edge, i.e. an communication channels between two data 
centres in a residual network

I have referred to the implementation of Edge class shown in the recording
Lecture04 P1 Graph BFS DFS Lecture05 P1 Dijkstra
"""
class Edge:
    def __init__(self, u, v, w):
        """
        Create a new Edge object

        :Input:
            self: a reference to the Edge object
            u: data centre ID where the channel departs
            v: data centre ID where the channel arrives
            w: maximum throughput of the channel

        :Output/Return: -

        :Time complexity: O(1)
        :Aux space complexity: O(1)
        """
        self.u = u
        self.v = v
        self.w = w

    def __str__(self):
        """
        Display the edge

        :Input:
            self: a reference to the Edge object

        :Output/return: a string containing the data centre IDs where the 
        channel departs and arrives, including its maximum throughput

        :Time complexity: O(1)
        :Aux space complexity: O(1)
        """
        return "Centre " + str(self.u) + " to " + str(self.v) + " with " \
                + str(self.w) + " capacity"
