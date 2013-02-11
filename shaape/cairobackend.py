import cairo
import os
import errno
import math
import numpy as np
from scipy import ndimage
from drawingbackend import DrawingBackend
import networkx as nx
from translatable import Translatable
from rotatable import Rotatable

class CairoBackend(DrawingBackend):
    DEFAULT_MARGIN = (10, 10, 10, 10)
    SHADOW_OPAQUENESS = 0.4
    def __init__(self):
        super(CairoBackend, self).__init__()
        self.set_margin(*(CairoBackend.DEFAULT_MARGIN))
        self.set_image_size(0, 0)
        self.__surfaces = []
        self.__ctx = None
        self.__drawn_graph = None
        return

    def blur_surface(self):
        blurred_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(math.ceil(self.__image_size[0] + self.__margin[0] + self.__margin[1])), int(math.ceil(self.__image_size[1] + self.__margin[2] + self.__margin[3])))
        top_surface = self.__surfaces[-1]
        width = top_surface.get_width()
        height = top_surface.get_height()
        src = np.frombuffer(top_surface.get_data(), np.uint8)
        src.shape = (height, width, 4)
        dst = np.frombuffer(blurred_surface.get_data(), np.uint8)
        dst.shape = (height, width, 4)
        dst[:,:,3] = ndimage.gaussian_filter(src[:,:,3], sigma=3)
        dst[:,:,0] = ndimage.gaussian_filter(src[:,:,0], sigma=3)
        dst[:,:,1] = ndimage.gaussian_filter(src[:,:,1], sigma=3)
        dst[:,:,2] = ndimage.gaussian_filter(src[:,:,2], sigma=3)
        blurred_image = cairo.ImageSurface.create_for_data(dst, cairo.FORMAT_ARGB32, width, height)
        self.__ctx.set_source_surface(blurred_image)
        self.__ctx.set_operator(cairo.OPERATOR_SOURCE)
        self.__ctx.paint()

    def new_surface(self, name = None):
        return cairo.ImageSurface(cairo.FORMAT_ARGB32, int(math.ceil(self.image_size()[0] + self.margin()[0] + self.margin()[1])), int(math.ceil(self.image_size()[1] + self.margin()[2] + self.margin()[3])))

    def push_surface(self):
        surface = self.new_surface()
        self.__surfaces.append(surface)
        self.__ctx = cairo.Context(surface)
        self.__drawn_graph = nx.Graph()

    def pop_surface(self):
        surface = self.__surfaces.pop()
        self.__ctx = cairo.Context(self.__surfaces[-1])
        self.__ctx.set_source_surface(surface)
        self.__ctx.set_operator(cairo.OPERATOR_OVER)
        self.__ctx.paint()
        self.__drawn_graph = None

    def surfaces(self):
        return self.__surfaces

    def set_image_size(self, width, height):
        self.__image_size = (width, height)

    def image_size(self):
        return self.__image_size

    def set_margin(self, left, right, top, bottom):
        self.__margin = (left, right, top, bottom)

    def margin(self):
        return self.__margin

    def create_canvas(self):
        self.set_image_size(self._canvas_size[0], self._canvas_size[1])
        self.push_surface()
        self.__ctx.set_source_rgb(1, 1, 1)
        self.__ctx.rectangle(0.0, 0.0, self.__image_size[0] + self.__margin[0] + self.__margin[1], self.__image_size[1] + self.__margin[2] + self.__margin[3])
        self.__ctx.translate(self.__margin[0], self.__margin[2])
        return
    
    def apply_dash(self, drawable):
        if drawable.style().fill_type() == 'dashed':
            width = drawable.style().width() * self._scale
            dash_list = [ width * 4, width]
            self.__ctx.set_dash(dash_list)
        elif drawable.style().fill_type() == 'dotted':
            width = drawable.style().width() * self._scale
            dash_list = [ width, width]
            self.__ctx.set_dash(dash_list)
        elif drawable.style().fill_type() == 'dash-dotted':
            width = drawable.style().width() * self._scale
            dash_list = [ width * 4, width, width, width]
            self.__ctx.set_dash(dash_list)
        else:
            self.__ctx.set_dash([])

    def apply_line(self, drawable, opaqueness = 1.0, shadow = False):
        self.__ctx.set_line_cap(cairo.LINE_CAP_BUTT)
        self.__ctx.set_line_join (cairo.LINE_JOIN_ROUND)
        width =  math.floor(drawable.style().width() * self._scale)
        color = drawable.style().color()[0]
        if len(color) == 3:
            adapted_color = tuple(color[:3]) + tuple([opaqueness])
        else:
            adapted_color = tuple(color[:3]) + tuple([color[3] * opaqueness])
        if shadow:
            adapted_color = map(lambda x: (1 - adapted_color[3]) * x, adapted_color[:3]) + [adapted_color[3]]
        self.__ctx.set_source_rgba(*adapted_color)
        self.apply_dash(drawable)
        self.__ctx.set_line_width(width)
        return

    def apply_fill(self, drawable, opaqueness = 1.0, shadow = False):
        minimum = drawable.min()
        maximum = drawable.max()
        colors =  drawable.style().color()
        if len(colors) > 1:
            linear_gradient = cairo.LinearGradient(minimum[0], minimum[1], maximum[0], maximum[1])
            n = 0
            for color in colors:
                stop = n * (1.0 / (len(colors) - 1))
                if len(color) == 3:
                    color = tuple(color) + tuple([1])
                if shadow:
                    color = map(lambda x: (1 - color[3]) * x, color[:3]) + [color[3]]
                adapted_color = tuple(color[:3]) + tuple([color[3] * opaqueness])
                linear_gradient.add_color_stop_rgba(stop, *adapted_color)
                n = n + 1
            self.__ctx.set_source(linear_gradient)
        else:
            color = colors[0]
            if len(color) == 3:
                color = tuple(color) + tuple([1])
            if shadow:
                color = map(lambda x: (1 - color[3]) * x, color[:3]) + [color[3]]
            adapted_color = tuple(color[:3]) + tuple([color[3] * opaqueness])
            self.__ctx.set_source_rgba(*adapted_color)
    
    def draw_polygon(self, polygon):
        self.__ctx.save()
        self.apply_fill(polygon)
        self.apply_transform(polygon)
        nodes = polygon.nodes()
        if len(nodes) > 1 and nodes[0] != nodes[-1]:
            nodes = nodes + [nodes[0]]
        nodes = [nodes[-2]] + nodes
        self.apply_path(nodes)
                
        self.__ctx.fill()
        self.__ctx.restore()
        return

    def draw_polygon_shadow(self, polygon):
        self.__ctx.save()
        self.apply_fill(polygon, opaqueness = self.SHADOW_OPAQUENESS, shadow = True)
        self.__ctx.set_operator(cairo.OPERATOR_SOURCE)
        self.apply_transform(polygon)
        nodes = polygon.nodes()
        if len(nodes) > 1 and nodes[0] != nodes[-1]:
            nodes = nodes + [nodes[0]]
        nodes = [nodes[-2]] + nodes
        self.apply_path(nodes)
        self.__ctx.fill()
        self.__ctx.restore()
        return

    def draw_open_graph_shadow(self, open_graph):
        self.apply_line(open_graph, opaqueness = self.SHADOW_OPAQUENESS, shadow = True)
        self.__ctx.save()
        self.apply_transform(open_graph)
        self.__ctx.set_operator(cairo.OPERATOR_SOURCE)
        paths = open_graph.paths()
        if len(paths) > 0:
            for path in paths:
                if path[0] == path[-1]:
                    nodes = [path[-2]] + path 
                else:
                    nodes = [path[0]] + path + [path[-1]]
                self.apply_line(open_graph, opaqueness = self.SHADOW_OPAQUENESS, shadow = True)
                self.apply_path(nodes)
                self.__ctx.set_operator(cairo.OPERATOR_SOURCE)
                self.__ctx.stroke()
        self.__ctx.restore()
        return

    def _transform_to_sharp_space(self, node):
        if self.__ctx.get_line_width() % 2 == 1:
            return (node[0] + 0.5, node[1] + 0.5)
        else:
            return node


    def apply_path(self, nodes):
        if nodes[0].style() == 'curve':
            line_end = nodes[1] + ((nodes[0] - nodes[1]) * 0.5)
        else: 
            line_end = nodes[0]
        self.__ctx.move_to(*self._transform_to_sharp_space(line_end))
        for i in range(1, len(nodes) - 1):
            if nodes[i].style() == 'curve':
                if i > 0 and nodes[i - 1].style() == 'miter':
                    temp_end = nodes[i - 1] + ((nodes[i] - nodes[i - 1]) * 0.5)
                    self.__ctx.line_to(*self._transform_to_sharp_space(temp_end))
                line_end = nodes[i] + ((nodes[i + 1] - nodes[i]) * 0.5)
                cp1 = nodes[i - 1] + ((nodes[i] - nodes[i - 1]) * 0.9)
                cp2 = nodes[i + 1] + ((nodes[i] - nodes[i + 1]) * 0.9)
                cp1 = self._transform_to_sharp_space(cp1)
                cp2 = self._transform_to_sharp_space(cp2)
                self.__ctx.curve_to(cp1[0], cp1[1], cp2[0], cp2[1], *self._transform_to_sharp_space(line_end))
            else:
                self.__ctx.line_to(*self._transform_to_sharp_space(nodes[i]))
                line_end = nodes[i]
        return

    def draw_open_graph(self, open_graph):
        self.__ctx.save()
        self.apply_transform(open_graph)
        paths = open_graph.paths()
        if len(paths) > 0:
            for path in paths:
                if path[0] == path[-1]:
                    nodes = [path[-2]] + path 
                else:
                    nodes = [path[0]] + path + [path[-1]]
                self.apply_line(open_graph)
                self.apply_path(nodes)
                self.__ctx.set_operator(cairo.OPERATOR_CLEAR)
                self.__ctx.set_dash([])
                self.__ctx.stroke_preserve()
                self.apply_line(open_graph)
                self.__ctx.set_operator(cairo.OPERATOR_SOURCE)
                self.__ctx.stroke()
        self.__ctx.restore()
        return

    def draw_text(self, text_obj):
        text = text_obj.text()
        self.__ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        xbearing, ybearing, width, height, xadvance, yadvance = self.__ctx.text_extents(text)
        self.__ctx.save()
        self.apply_line(text_obj)
        self.__ctx.set_font_size(text_obj.font_size() / 0.7)
        fascent, fdescent, fheight, fxadvance, fyadvance = self.__ctx.font_extents()
        for cx, letter in enumerate(text):
            xbearing, ybearing, width, height, xadvance, yadvance = (self.__ctx.text_extents(letter))
            self.__ctx.move_to(text_obj.position()[0] + cx * (text_obj.font_size()), text_obj.position()[1] + text_obj.font_size() - fdescent + fheight / 2)
            self.__ctx.show_text(letter)
        self.__ctx.restore()
        return

    def apply_transform(self, obj):
        if isinstance(obj, Translatable):
            self.__ctx.translate(obj.position()[0], obj.position()[1])
        if isinstance(obj, Rotatable):
            self.__ctx.rotate(math.radians(obj.angle()))
        return

    def export_to_file(self, filename):
        path = os.path.dirname(filename)
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        self.__surfaces[-1].write_to_png(filename)
        return

    def ctx(self):
        return self.__ctx

    def translate(self, x, y):
        self.ctx().translate(x, y)
