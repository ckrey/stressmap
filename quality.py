#!/usr/bin/env python -B
""" quality.py parses an .osm file and creates quality rated geojson files as overlays
"""

import xml.sax
import getopt
import os
import sys

DEBUG_OUT = open(os.devnull, "w")
WAYS = {}
OSM_NODES = {}
HIGHWAY_TYPES = {}
ELEMENT_TYPES = {}
USED_NODES = {}

class OSMNode:
    """ OSMNode represents an OSM Node
    """
    def __init__(self, identifier, lon, lat):
        self.identifier = identifier
        self.lon = lon
        self.lat = lat

def tag_starts_with(tags, start):
    for tag in tags:
        if tag.startswith(start):
            return True
    return False

def tag_starts_with_value(tags, start, value):
    for tag in tags:
        if tag.startswith(start):
            tag_value = tags[tag]
            if tag_value == value:
                return True
    return False

def effective_highway(tags, value):
    if 'highway' in tags:
        return tags['highway'] == value
    return False

def separated_path(old_level, tags):
    if effective_highway(tags, 'path'):
        # This way is a separated path because highway='path'.
        return 501

    if effective_highway(tags, 'footway'):
        if 'footway' not in tags or tags['footway'] != 'crossing':
            # This way is a separated path because highway='footway' but it is not a crossing.
            return 502

    if effective_highway(tags, 'cycleway'):
        # This way is a separated path because highway='cycleway'.
        return 503

    if tag_starts_with_value(tags, 'cycleway', 'track'):
        # This way is a separated path because cycleway* is defined as \'track\'.
        return 504

    if tag_starts_with_value(tags, 'cycleway', 'opposite_track'):
        # This way is a separated path because cycleway* is defined as \'opposite_track\'.
        return 505

    return old_level # not separated

def biking_permitted(tags):
    if not 'highway' in tags and 'bicycle' in tags:
        print('!!!no highway, but bicycle', tags)

    if 'highway' in tags or 'bicycle' in tags:
        if 'bicycle' in tags and tags['bicycle'] == 'no':
            return 1 # Cycling not permitted due to bicycle='no' tag.
        if 'bicycle' in tags and tags['bicycle'] == 'use_sidepath':
            return 10 # Cycling not permitted due to bicycle='use_sidepath' tag.
        if 'access' in tags and tags['access'] == 'no':
            return 2 # Cycling not permitted due to access='no' tag.

        if effective_highway(tags, 'motorway'):
            return 3 # Cycling not permitted due to highway=\'motorway\' tag.
        if effective_highway(tags, 'motorway_link'):
            return 4 # Cycling not permitted due to highway='motorway_link' tag.
        if effective_highway(tags, 'proposed'):
            return 5 # Cycling not permitted due to highway='proposed' tag.
        if effective_highway(tags, 'construction'):
            return 8 # Cycling not permitted due to highway='construction' tag.

        if 'footway' in tags and tags['footway'] == 'sidewalk':
            if 'bicycle' in tags and tags['bicycle'] == 'yes':
                return 100
            if effective_highway(tags, 'footway'):
                # Cycling not permitted. When footway='sidewalk' is present,
                # there must be a bicycle='yes' when the highway is 'footway'.
                return 6
            if effective_highway(tags, 'path'):
                # Cycling not permitted. When footway='sidewalk' is present,
                # there must be a bicycle='yes' when the highway is 'path'.
                return 7
            return 100

        if effective_highway(tags, 'footway') or effective_highway(tags, 'steps'):
            if tag_starts_with(tags, 'cycleway'):
                return 100 # footway with cycleway
            if 'bicycle' in tags and tags['bicycle'] == 'yes':
                return 100 # footway with explicit bicycle
            return 9 # footway without explicit cycleway or bicycle

        return 100 # highway or bicycle in tags
    return 0 # Way has neither a highway tag nor a bicycle=yes tag. The way is not a highway.

def compute_level(tags):
    _level = biking_permitted(tags)
    if _level >= 100:
        _level = separated_path(_level, tags)
    return _level

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
            node_ref = int(attrs['ref'])
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
                _highway = self.tags['highway']
                _level = compute_level(self.tags)
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
            OSM_NODES[int(self.nodeid)] = _osm_node
            self.tags = {}

def usage(argv0):
    print('{} [-o <output directory>] [-i <input file>]'.format(argv0))

if __name__ == "__main__":
    IN_FILE = 'default.osm'
    OUT_DIR = '.'
    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:], "hdi:o:", ["help", "debug", "ifile=", "odir="])
    except getopt.GetoptError:
        usage(sys.argv[0])
        sys.exit(2)
    for opt, arg in OPTS:
        if opt in ('-h', '--help'):
            usage(sys.argv[0])
            sys.exit()
        elif opt in ('-d', '--debug'):
            DEBUG_OUT = sys.stderr
        elif opt in ("-o", "--odir"):
            OUT_DIR = arg
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

    print('creating files...')

    try:
        os.stat(OUT_DIR)
    except OSError:
        os.mkdir(OUT_DIR)

    for outputLevel in range(0, 10):
        path = OUT_DIR + '/quality_%d.json' % outputLevel
        outfile = open(path, "w")

        outfile.write('{"type":"FeatureCollection","features":[\n')
        waysSeparator = ''
        for way_id in WAYS:
            way = WAYS[way_id]
            wayTags = way['tags']
            level = 0
            if 'level' in way:
                level = way['level']
            if int(level / 100) == outputLevel:
                outfile.write('{s:s}{{"type":"Feature","id":"way/{w:s}"\n'.format(
                    s=waysSeparator, w=way_id))
                waysSeparator = ','
                outfile.write(',"properties":{{"id":"way/{w:s}"\n'.format(w=way_id))
                if 'name' in wayTags:
                    way_name = wayTags['name']
                    way_name = way_name.replace('"', '\\"')
                    outfile.write(',"name":"{n:s}"\n'.format(n=way_name))
                outfile.write('},"geometry":{"type":"LineString","coordinates":[\n')
                way_nodes = way['nodes']
                coordinateSeparator = ''
                for nodeId in way_nodes:
                    osm_node = OSM_NODES[nodeId]
                    outfile.write('{0:s}[{1:.6f},{2:.6f}]\n'.format(
                        coordinateSeparator, osm_node.lon, osm_node.lat))
                    coordinateSeparator = ','
                outfile.write(']}}\n')
        outfile.write(']}\n')
        outfile.close()

    print('finished!')
