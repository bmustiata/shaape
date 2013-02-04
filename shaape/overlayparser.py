import networkx as nx
import warnings
import operator
import math
from opengraph import OpenGraph
from polygon import Polygon
from parser import *
from node import *
from edge import Edge
from overlay import Overlay
from graphalgorithms import planar_cycles

class OverlayParser(Parser):

    CROSSING_LENGTH = 0.5
    CROSSING_HEIGHT = 0.25

    def __init__(self):
        super(OverlayParser, self).__init__()
        self.__sub_overlays = []
        self.__sub_overlays.append(Overlay([['-']], [Edge(Node(0, 0.5), Node(1, 0.5))]))
        self.__sub_overlays.append(Overlay([['|']], [Edge(Node(0.5, 0), Node(0.5, 1))]))
        self.__sub_overlays.append(Overlay([['/']], [Edge(Node(0, 1), Node(1, 0))]))
        self.__sub_overlays.append(Overlay([['\\']], [Edge(Node(1, 1), Node(0, 0))]))
        self.__sub_overlays.append(Overlay([['-','|','-']], [Edge(Node(1, 0.5), Node(2, 0.5), top_of = Edge(Node(1.5, 0), Node(1.5, 1)))]))
        self.__sub_overlays.append(Overlay([['|'],['-'],['|']], [Edge(Node(0.5, 1), Node(0.5, 2), top_of = Edge(Node(0, 1.5), Node(1, 1.5)))]))
        self.__sub_overlays.append(Overlay([['+','-']], [Edge(Node(0.5, 0.5, fusable = False), Node(1, 0.5))]))
        self.__sub_overlays.append(Overlay([['-','+']], [Edge(Node(1, 0.5), Node(1.5, 0.5, fusable = False))]))
        self.__sub_overlays.append(Overlay([['+'],['|']], [Edge(Node(0.5, 0.5, fusable = False), Node(0.5, 1))]))
        self.__sub_overlays.append(Overlay([['|'],['+']], [Edge(Node(0.5, 1), Node(0.5, 1.5, fusable = False))]))
        self.__sub_overlays.append(Overlay([[None, '/'],['+', None]], [Edge(Node(1, 1), Node(0.5, 1.5, fusable = False))]))
        self.__sub_overlays.append(Overlay([[None, '*'],['+', None]], [Edge(Node(1.5, 0.5, 'curve'), Node(0.5, 1.5, fusable = False))]))
        self.__sub_overlays.append(Overlay([['*', None],[None, '+']], [Edge(Node(0.5, 0.5, 'curve'), Node(1.5, 1.5, fusable = False))]))
        self.__sub_overlays.append(Overlay([['+', None],[None, '+']], [Edge(Node(0.5, 0.5, fusable = False), Node(1.5, 1.5, fusable = False))]))
        self.__sub_overlays.append(Overlay([[None, '+'],['*', None]], [Edge(Node(1.5, 0.5), Node(0.5, 1.5, 'curve', fusable = False))]))
        self.__sub_overlays.append(Overlay([[None, '+'],['+', None]], [Edge(Node(1.5, 0.5, fusable = False), Node(0.5, 1.5, fusable = False))]))
        self.__sub_overlays.append(Overlay([['+', None],[None, '*']], [Edge(Node(0.5, 0.5), Node(1.5, 1.5, 'curve', fusable = False))]))
        self.__sub_overlays.append(Overlay([['\\', None],[None, '+']], [Edge(Node(1, 1), Node(1.5, 1.5, fusable = False))]))
        self.__sub_overlays.append(Overlay([['+', None],[None, '\\']], [Edge(Node(0.5, 0.5, fusable = False), Node(1, 1))]))
        self.__sub_overlays.append(Overlay([[None, '+'],['/', None]], [Edge(Node(1.5, 0.5, fusable = False), Node(1, 1))]))
        self.__sub_overlays.append(Overlay([['|'],['*']], [Edge(Node(0.5, 1), Node(0.5, 1.5, 'curve'))]))
        self.__sub_overlays.append(Overlay([['*'],['|']], [Edge(Node(0.5, 0.5, 'curve'), Node(0.5, 1))]))
        self.__sub_overlays.append(Overlay([['*','-']], [Edge(Node(0.5, 0.5, 'curve'), Node(1, 0.5))]))
        self.__sub_overlays.append(Overlay([['-','*']], [Edge(Node(1, 0.5), Node(1.5, 0.5, 'curve'))]))
        self.__sub_overlays.append(Overlay([['+','+']], [Edge(Node(0.5, 0.5, fusable = False), Node(1.5, 0.5, fusable = False))]))
        self.__sub_overlays.append(Overlay([['+'],['+']], [Edge(Node(0.5, 0.5, fusable = False), Node(0.5, 1.5, fusable = False))]))

        self.__sub_overlays.append(Overlay([['|'], ['v']], [Edge(Node(0.5, 1), Node(0.5, 1.55))]))
        self.__sub_overlays.append(Overlay([['^'], ['|']], [Edge(Node(0.5, 0.45), Node(0.5, 1))]))

        self.__sub_overlays.append(Overlay([['|'], ['^']], [Edge(Node(0.5, 1), Node(0.5, 1.45))]))
        self.__sub_overlays.append(Overlay([['v'], ['|']], [Edge(Node(0.5, 0.55), Node(0.5, 1))]))
        self.__sub_overlays.append(Overlay([['-', '<']], [Edge(Node(1, 0.5), Node(2, 0.5))]))
        self.__sub_overlays.append(Overlay([['>', '-']], [Edge(Node(0, 0.5), Node(1, 0.5))]))

        self.__sub_overlays.append(Overlay([['+'], ['^']], [Edge(Node(0.5, 0.5), Node(0.5, 1.45))]))
        self.__sub_overlays.append(Overlay([['v'], ['+']], [Edge(Node(0.5, 0.55), Node(0.5, 1.5))]))
        self.__sub_overlays.append(Overlay([['+', '<']], [Edge(Node(0.5, 0.5), Node(2, 0.5))]))
        self.__sub_overlays.append(Overlay([['>', '+']], [Edge(Node(0, 0.5), Node(1.5, 0.5))]))

        self.__sub_overlays.append(Overlay([['*','*']], [Edge(Node(0.5, 0.5, 'curve'), Node(1.5, 0.5, 'curve'))]))
        self.__sub_overlays.append(Overlay([['*'],['*']], [Edge(Node(0.5, 0.5, 'curve'), Node(0.5, 1.5,'curve'))]))
        self.__sub_overlays.append(Overlay([[None, '*'],['*', None]], [Edge(Node(1.5, 0.5, 'curve'), Node(0.5, 1.5,'curve'))]))
        self.__sub_overlays.append(Overlay([['*', None],[None, '*']], [Edge(Node(0.5, 0.5, 'curve'), Node(1.5, 1.5,'curve'))]))

        crossing_top = (1.0 - OverlayParser.CROSSING_LENGTH) / 2.0
        crossing_bottom = 1.0 - (1.0 - OverlayParser.CROSSING_LENGTH) / 2.0
        crossing_top_curve = crossing_top + OverlayParser.CROSSING_LENGTH / 5.0
        crossing_bottom_curve = crossing_bottom - OverlayParser.CROSSING_LENGTH / 5.0
        crossing_left = 0.5 - OverlayParser.CROSSING_HEIGHT
        crossing_right = 0.5 + OverlayParser.CROSSING_HEIGHT

        self.__sub_overlays.append(Overlay([['[']], [Edge(Node(0.5, 0), Node(0.5, crossing_top)), Edge(Node(0.5, crossing_top), Node(crossing_left, crossing_top)), Edge(Node(crossing_left, crossing_top), Node(crossing_left, crossing_bottom)), Edge(Node(0.5, crossing_bottom), Node(crossing_left, crossing_bottom)), Edge(Node(0.5, 1), Node(0.5, crossing_bottom))]))
        self.__sub_overlays.append(Overlay([[']']], [Edge(Node(0.5, 0), Node(0.5, crossing_top)), Edge(Node(0.5, crossing_top), Node(crossing_right, crossing_top)), Edge(Node(crossing_right, crossing_top), Node(crossing_right, crossing_bottom)), Edge(Node(0.5, crossing_bottom), Node(crossing_right, crossing_bottom)), Edge(Node(0.5, 1), Node(0.5, crossing_bottom))]))
        self.__sub_overlays.append(Overlay([[')']], [Edge(Node(0.5, 0, 'curve'), Node(0.5, crossing_top, 'curve')), Edge(Node(0.5, crossing_top, 'curve'), Node(crossing_right, crossing_top_curve, 'curve')), Edge(Node(crossing_right, crossing_top_curve, 'curve'), Node(crossing_right, crossing_bottom_curve, 'curve')), Edge(Node(0.5, crossing_bottom, 'curve'), Node(crossing_right, crossing_bottom_curve, 'curve')), Edge(Node(0.5, 1, 'curve'), Node(0.5, crossing_bottom, 'curve'))]))
        self.__sub_overlays.append(Overlay([['(']], [Edge(Node(0.5, 0, 'curve'), Node(0.5, crossing_top, 'curve')), Edge(Node(0.5, crossing_top, 'curve'), Node(crossing_left, crossing_top_curve, 'curve')), Edge(Node(crossing_left, crossing_top_curve, 'curve'), Node(crossing_left, crossing_bottom_curve, 'curve')), Edge(Node(0.5, crossing_bottom, 'curve'), Node(crossing_left, crossing_bottom_curve, 'curve')), Edge(Node(0.5, 1, 'curve'), Node(0.5, crossing_bottom, 'curve'))]))

        crossing_left = (1.0 - OverlayParser.CROSSING_LENGTH) / 4.0
        crossing_right = 1.0 - (1.0 - OverlayParser.CROSSING_LENGTH) / 4.0
        crossing_left_curve = crossing_left + OverlayParser.CROSSING_LENGTH / 5.0
        crossing_right_curve = crossing_right - OverlayParser.CROSSING_LENGTH / 5.0
        crossing_top = 0.5 - OverlayParser.CROSSING_HEIGHT / 2
        self.__sub_overlays.append(Overlay([['~']], [Edge(Node(0, 0.5, 'curve'), Node(crossing_left, 0.5, 'curve')), Edge(Node(crossing_left, 0.5, 'curve'), Node(crossing_left_curve, crossing_top, 'curve')), Edge(Node(crossing_left_curve, crossing_top, 'curve'), Node(crossing_right_curve, crossing_top, 'curve')), Edge(Node(crossing_right_curve, crossing_top, 'curve'), Node(crossing_right, 0.5, 'curve')), Edge(Node(crossing_right, 0.5, 'curve'), Node(1, 0.5, 'curve'))]))

        for crossing_indicator in ['[', ']', '(', ')']:
            self.__sub_overlays.append(Overlay([['-', crossing_indicator]], [Edge(Node(1, 0.5, fusable = False), Node(1.5, 0.5, fusable = False))]))
            self.__sub_overlays.append(Overlay([[crossing_indicator, '-']], [Edge(Node(0.5, 0.5, fusable = False), Node(1, 0.5, fusable = False))]))

        self.__sub_overlays.append(Overlay([['~'], ['|']], [Edge(Node(0.5, 1, fusable = False), Node(0.5, 0.5, fusable = False))]))
        self.__sub_overlays.append(Overlay([['|'], ['~']], [Edge(Node(0.5, 1, fusable = False), Node(0.5, 1.5, fusable = False))]))
        return

    def cycle_len(self, cycle):
        length = 0
        for i in range(0, len(cycle) - 1):
            length = length + (cycle[i + 1] - cycle[i]).length()
        return length

    def run(self, raw_data, drawable_objects):
        graphs = []
        new_objects = []
        for overlay in self.__sub_overlays:
            g = overlay.substitutes(raw_data)
            graphs.append(g)

        graph = graphs.pop(0)
        for h in graphs:
            graph = nx.compose(graph, h)

        components = nx.connected_component_subgraphs(graph)
        closed_polygons = []
        polygons = []
        for component in components:
            minimum_cycles = planar_cycles(component)

            # the polygons are the same as the minimum cycles
            closed_polygons += minimum_cycles
            path_graph = nx.Graph()
            path_graph.add_nodes_from(component.nodes())

            for polygon in minimum_cycles:
                polygons.append(Polygon(polygon))
                path_graph.add_cycle(polygon)

            remaining_graph = nx.difference(component, path_graph)
            for n in remaining_graph.nodes():
                if remaining_graph.degree(n) == 0:
                    remaining_graph.remove_node(n)
            if len(remaining_graph.edges()) > 0:
                remaining_components = nx.connected_component_subgraphs(remaining_graph)
                for c in remaining_components:
                    new_objects.append(OpenGraph(c))

        
        new_objects = new_objects + polygons
        z_order_graph = nx.DiGraph()
        z_order_graph.add_nodes_from(new_objects)
        
        for i in range(0, len(polygons)):
            polygon1 = polygons[i]
            for j in range(i + 1, len(polygons)):
                polygon2 = polygons[j]
                if polygon1 != polygon2:
                    if polygon1.contains(polygon2):
                        z_order_graph.add_edge(polygon1, polygon2)
                    elif polygon2.contains(polygon1):
                        z_order_graph.add_edge(polygon2, polygon1)
            
       
        for obj in new_objects:
            for edge in obj.edges():
                if 'top_of' in graph[edge[0]][edge[1]]:
                    top_of = graph[edge[0]][edge[1]]['top_of']
                    if top_of != None:
                        for obj_above in new_objects:
                            if obj != obj_above:
                                if obj_above.has_edge(top_of.start(), top_of.end()):
                                    z_order_graph.add_edge(obj, obj_above)
        cycles = nx.simple_cycles(z_order_graph)
        if cycles:
            warnings.warn("The diagram contains objects. that have an ambiguous z-order. Shaape estimates their z-order.", RuntimeWarning)
        for cycle in cycles:
            cycle_edges = [(cycle[i], cycle[i + 1]) for i in range(0, len(cycle) - 1)]
            for edge in cycle_edges:
                z_order_graph.remove_edge(edge[0], edge[1])
                       

        current_z_order = 0
        while z_order_graph.nodes():
            nodes_without_predecessors = [node for node in z_order_graph.nodes() if not z_order_graph.predecessors(node)]
            for node in nodes_without_predecessors:
                node.set_z_order(current_z_order)
            current_z_order = current_z_order + 1
            z_order_graph.remove_nodes_from(nodes_without_predecessors)

        drawable_objects = drawable_objects + new_objects

        self._drawable_objects = drawable_objects
        self._parsed_data = raw_data
        return
