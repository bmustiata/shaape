from parser import Parser
from polygon import Polygon
from text import Text

class NameParser(Parser):
    def __init__(self):
        super(NameParser, self).__init__()
        return

    def run(self, raw_data, drawable_objects):
        self._parsed_data = raw_data
        self._drawable_objects = drawable_objects
        polygons = filter(lambda x: isinstance(x, Polygon), drawable_objects)
        texts = filter(lambda x: isinstance(x, Text), drawable_objects)
        
        for text in texts:
            text.add_name(text.text())
            position = (text.position()[0] + 0.5, text.position()[1] + 0.5)
            polygons_containing_this_text = [polygon for polygon in polygons if polygon.contains(position)]
            if len(polygons_containing_this_text) == 1:
                polygons_containing_this_text[0].add_name(text.text())
            else:
                for polygon in polygons_containing_this_text:
                    not_directly_named = False
                    for other_polygon in [p for p in polygons_containing_this_text if p != polygon]:
                        if polygon.contains(other_polygon): # pragma: no cover
                            not_directly_named = True
                            break

                    if not_directly_named == False:
                        polygon.add_name(text.text())
        return
