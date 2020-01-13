#!/usr/bin/env python -B
""" quality.py parses an .osm file and creates an intermediat .osm.json file
"""

import xml.sax
import getopt
import os
import sys
import json

DEBUG_OUT = open(os.devnull, "w")
WAYS = {}
OSM_NODES = {}
HIGHWAY_TYPES = {}
LEVELS = {}
AREAS = 0
PLATFORMS = 0
ELEMENT_TYPES = {}
ACCESS_TYPES = {}
USED_NODES = {}

class OSMNode(dict):
    """ OSMNode represents an OSM Node
    """
    def __init__(self, identifier, lon, lat):
        self['identifier'] = identifier
        self['lon'] = lon
        self['lat'] = lat

class NodeHandler(xml.sax.ContentHandler):
    def __init__(self):
        super().__init__()
        self.nodeid = 0
        self.lat = 0.0
        self.lon = 0.0
        self.tags = {}
        self.way_id = 0
        self.way_nodes = []
        self.tags = {}

    def startElement(self, name, attrs):
        if len(OSM_NODES) % 1000 == 1 or len(WAYS) % 100 == 1 or len(USED_NODES) % 1000 == 1:
            sys.stderr.write('Nodes {} Ways {} using {} nodes\r'.format(len(OSM_NODES), len(WAYS), len(USED_NODES)))
        DEBUG_OUT.write('startElement {}\n'.format(name))
        _count = 1
        if name in ELEMENT_TYPES:
            _count = ELEMENT_TYPES[name]
            _count = _count + 1
        ELEMENT_TYPES[name] = _count

        for attr_name in attrs.getNames():
            attr_type = attrs.getType(attr_name)
            attr_value = attrs.getValue(attr_name)
            DEBUG_OUT.write('    attribute {} {} {}\n'.format(attr_name, attr_type, attr_value))

        if name == 'way':
            self.way_id = attrs['id']
            self.way_nodes = []
            self.tags = {}

        if name == 'node':
            self.nodeid = attrs['id']
            self.lat = attrs['lat']
            self.lon = attrs['lon']
            self.tags = {}

        if name == 'nd':
            node_ref = attrs['ref']
            self.way_nodes.append(node_ref)
            USED_NODES[node_ref] = 1

        if name == 'tag':
            _tag_key = attrs['k']
            _tag_value = attrs['v']
            self.tags[_tag_key] = _tag_value

    def endElement(self, name):
        DEBUG_OUT.write('endElement {}\n'.format(name))

        if name == 'way':
            if 'highway' in self.tags:
                if 'area' in self.tags and self.tags['area'] == 'yes':
                    global AREAS
                    AREAS = AREAS + 1
                    return

                if 'access' in self.tags:
                    _access = self.tags['access']
                    _count = 1
                    if _access in ACCESS_TYPES:
                        _count = ACCESS_TYPES[_access]
                        _count = _count + 1
                    ACCESS_TYPES[_access] = _count

                _highway = self.tags['highway']
                if _highway == 'platform':
                    global PLATFORMS
                    PLATFORMS = PLATFORMS + 1
                    return

                _level = -1
                _way = {
                    'id': self.way_id,
                    'tags': self.tags,
                    'nodes': self.way_nodes,
                    'level': _level,
                }
                DEBUG_OUT.write('endElement {} {}\n'.format(name, _way))
                WAYS[self.way_id] = _way

                _count = 1
                if _highway in HIGHWAY_TYPES:
                    _count = HIGHWAY_TYPES[_highway]
                    _count = _count + 1
                HIGHWAY_TYPES[_highway] = _count


                self.way_nodes = {}
                self.tags = {}

        if name == 'node':
            _osm_node = OSMNode(int(self.nodeid), float(self.lon), float(self.lat))

            DEBUG_OUT.write('endElement {} {}\n'.format(name, _osm_node))
            OSM_NODES[self.nodeid] = _osm_node
            self.tags = {}

def usage(argv0):
    print('{} [-i <input file>]'.format(argv0))

if __name__ == "__main__":
    IN_FILE = 'default.osm'
    OUT_DIR = '.'
    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:], "hdi:", ["help", "debug", "ifile="])
    except getopt.GetoptError:
        usage(sys.argv[0])
        sys.exit(2)
    for opt, arg in OPTS:
        if opt in ('-h', '--help'):
            usage(sys.argv[0])
            sys.exit()
        elif opt in ('-d', '--debug'):
            DEBUG_OUT = sys.stderr
        elif opt in ("-i", "--ifile"):
            IN_FILE = arg
        else:
            usage(sys.argv[0])
            sys.exit(3)

    print('parsing...')

    PARSER = xml.sax.make_parser()
    PARSER.setFeature(xml.sax.handler.feature_namespaces, 0)
    HANDLER = NodeHandler()
    PARSER.setContentHandler(HANDLER)
    PARSER.parse(IN_FILE)

    print('finished parsing {} nodes and {} ways using {} nodes!'.format(len(OSM_NODES), len(WAYS), len(USED_NODES)))

    print('ELEMENT_TYPES {}'.format(ELEMENT_TYPES))
    print('HIGHWAY_TYPES {}'.format(HIGHWAY_TYPES))
    print('ACCESS_TYPES {}'.format(ACCESS_TYPES))
    print('AREAS {}'.format(AREAS))
    print('PLATFORMS {}'.format(PLATFORMS))
    print('LEVELS {}'.format(LEVELS))

    print('saving intermediates...')
    intermediate = {'nodes': OSM_NODES, 'ways': WAYS}
    intermediate_path = '%s.json' % IN_FILE
    intermediate_outfile = open(intermediate_path, "w")
    json.dump(intermediate, intermediate_outfile)
    intermediate_outfile.close()

    print('finished!')
