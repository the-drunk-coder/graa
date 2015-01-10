# Import graphviz
import sys, os, copy
sys.path.append('..')
sys.path.append('/usr/lib/graphviz/python/')
sys.path.append('/usr/lib64/graphviz/python/')
import graphviz

from graphviz import Digraph

class GraphError(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)

"""
A node, consting of an
"""
class Node():
    def __init__(self, node_id, node_content, meta=""):
        self.id = node_id
        self.content = node_content
        # space for arbitrary meta information
        self.meta = meta

"""
An edge, consisting of the destination node, the transition probability and the transition duration.

If transition probability is None, it will be calculated when the edge is added.

"""
class Edge():
    def __init__(self, destination_node_id, transition_duration, transition_probability=None):
        self.dest = destination_node_id
        self.prob = transition_probability
        self.dur = transition_duration
        
class Graph():
    def __init__(self):
        self.nodes = {}
        self.edges = {}
        self.start_node_id = None
        self.current_node_id = None
    def add_node(self, node):
        # by convention, first added node is start node
        if self.start_node_id == None:
            self.start_node_id = node.id
            self.current_node_id = node.id
        self.nodes[node.id] = node
        self.edges[node.id] = []
    # Add an edge, a a tuple of destination node and transition
    def add_edge(self, source_node_id, new_edge):
        if source_node_id not in self.nodes or new_edge.dest not in self.nodes:
            raise GraphError("nodes for this edge not present")
        else:
            #check if there's already an edge in that respective direction, and remove it
            for edge in self.edges[source_node_id]:
                if edge.dest == new_edge.dest:
                    self.edges[source_node_id].remove(edge)
            if new_edge.prob == None:
                new_prob = int(100/(len(self.edges[source_node_id]) + 1))
                for edge in self.edges[source_node_id]:
                    edge.prob = new_prob
                new_edge.prob = new_prob
            self.edges[source_node_id].append(new_edge)                
    def render(self, filename, render="content"):
        dot = Digraph(comment="",edge_attr={'len': '6', 'weight':'0.00001'})
        dot.engine = 'dot'
        # add nodes to dot graph
        for node_key in self.nodes.keys():
            node_content = "nil"
            # either use id or content to mark graph nodes
            if render == "id":
                    node_content = str(self.nodes[node_key].id)
            elif render == "content":
                if len(self.nodes[node_key].content) > 0:
                    node_content = ', '.join(str(x) for x in self.nodes[node_key].content)
            else:
                node_content = str(self.nodes[node_key].id) + ":"
                if len(self.nodes[node_key].content) > 0:
                    node_content += ', '.join(str(x) for x in self.nodes[node_key].content) + ":"
                else:
                    node_content += "nil:"
                if len(self.nodes[node_key].meta) > 0:
                    node_content += self.nodes[node_key].meta
                else:
                    node_content += "nil"
            dot.node(str(self.nodes[node_key].id), node_content)
        #add edges to dot graph
        for edge_key in self.edges.keys():
            for edge in self.edges[edge_key]:
                dot.edge(str(edge_key), str(edge.dest))
        if not os.path.exists("graph"):
            os.makedirs("graph")
        dot.render("graph/" + filename + ".gv")

class GraphTool():
    # destructively reverse direction of edges 
    def reverse_digraph(self, graph):
        for i in range(0, len(graph.nodes)):
            node = graph.nodes[i]
            for edge in graph.edges[node.id]:
                # don't touch self-referential edges ...
                if edge.dest != node.id:
                    rev_edge = Edge(node.id, edge.dur, edge.prob) 
                    graph.add_edge(edge.dest, rev_edge)
                    graph.edges[node.id].remove(edge)
                    
    
class TraversalTool():
    # returns node traversal, breadth first
    def bf_trav(self, graph):
        node_stack = []
        nodes_unvisited = [x for x in range(0,len(graph.nodes) + 1)]
        traversal_list = []
        #remove start node and push to stack
        nodes_unvisited.remove(0)
        node_stack.append(0)
        traversal_list.append(0)
        while len(node_stack) != 0:
            current_node = node_stack.pop()
            for edge in graph.edges[current_node]:
                if edge.dest in nodes_unvisited:
                    nodes_unvisited.remove(edge.dest)
                    node_stack.append(edge.dest)
                    traversal_list.append(edge.dest)
        return traversal_list
    # return (dfs) topological sorting of the nodes
    def topo_trav(self, graph):
        dfs_tree = DfsTree(graph)
        sorted_tuples = sorted(list(zip(dfs_tree.all_node_ids, dfs_tree.finish_time)), key=lambda time:time[1])
        sorted_node_ids = [tpl[0] for tpl in sorted_tuples]
        return list(reversed(sorted_node_ids))
                           
class DfsTree():
    def __init__(self, graph):
        self.graph = graph
        self.node_stack = []
        self.node_color = []
        self.discovery_time =[]
        self.finish_time = []
        self.predecessor = []
        self.time = 0
        self.all_node_ids = []
        for i in range(0, len(graph.nodes)):
            self.node_color.append('white')
            self.discovery_time.append(0)
            self.finish_time.append(0)
            self.predecessor.append(None)
            self.all_node_ids.append(graph.nodes[i].id)
        self.dfs()
    def dfs(self):
        for i in range(0, len(self.graph.nodes)):
            if self.node_color[self.graph.nodes[i].id] == 'white':
                self.dfs_visit(self.graph.nodes[i])
    def dfs_visit(self, node):
        # actual algorithm ..
        self.node_color[node.id] = 'gray'
        self.time += 1
        self.discovery_time[node.id] = self.time
        # the child nodes are directly stored as integers, so we can use them directly here 
        for edge in self.graph.edges[node.id]:
            if self.node_color[edge.dest] == 'white':
                self.predecessor[edge.dest] = node.id
                self.dfs_visit(self.graph.nodes[edge.dest])
        self.node_color[node.id] = 'black'
        self.time += 1
        self.finish_time[node.id] = self.time
    def print_results(self):
        # generate result lists
        finish = sorted(list(zip(self.all_node_ids, self.finish_time)), key=lambda time:time[1])
        disc = list(zip(self.all_node_ids, self.discovery_time))
        col = list(zip(self.all_node_ids, self.node_color))
        pre = list(zip(self.all_node_ids, self.predecessor))
        # print them
        print("SORTED FINISH TIMES:" + str(finish))
        print("DISCOVERY TIMES:" + str(disc))
        print("COLORS:" + str(col))
        print("PREDECESSORS:" + str(pre))
 
