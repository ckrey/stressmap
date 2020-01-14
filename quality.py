#!/usr/bin/env python -B
""" quality.py parses an .osm.json file and creates quality rated geojson files as overlays
"""

import getopt
import os
import sys
import json

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

def cycleway(old_level, tags):
    if effective_highway(tags, 'cycleway'):
        # 700 This way is a cycleway because highway='cycleway'.
        return 700

    return old_level # no cycleway

def cyclestreet(old_level, tags):
    if 'cyclestreet' in tags and tags['cyclestreet'] == 'yes':
        # 401 This way is a cyclestreet because cyclestreet='yes'.
        return 401
    if 'bicycle_road' in tags and tags['bicycle_road'] == 'yes':
        # 402 This way is a cyclestreet because bicycle_road='yes'.
        return 402

    return old_level # no cyclestreet

def separated_path(old_level, tags):
    if effective_highway(tags, 'path'):
        # 501 This way is a separated path because highway='path'.
        return 501

    return old_level # not separated

def track(old_level, tags):
    if tag_starts_with_value(tags, 'cycleway', 'track'):
        # 301 This way is a separated path because cycleway* is defined as 'track'.
        return 304

    if tag_starts_with_value(tags, 'cycleway', 'opposite_track'):
        # 302 This way is a separated path because cycleway* is defined as 'opposite_track'.
        return 305

    return old_level # not separated

def lane(old_level, tags):
    if tag_starts_with_value(tags, 'cycleway', 'lane'):
        # 201 This way has a lane because cycleway* is defined as 'lane'.
        return 201

    if tag_starts_with_value(tags, 'cycleway', 'opposite_lane'):
        # 202 This way has a lane cycleway* is defined as 'opposite_lane'.
        return 202

    return old_level # not separated

def biking_permitted(tags):
    if not 'highway' in tags and 'bicycle' in tags:
        print('!!!no highway, but bicycle', tags)

    if 'highway' in tags or 'bicycle' in tags:
        if effective_highway(tags, 'trunk-link'):
            print('tags', tags)
        if 'bicycle' in tags and tags['bicycle'] == 'no':
            # 1 Cycling not permitted due to bicycle='no' tag.
            return 1
        if 'bicycle' in tags and tags['bicycle'] == 'use_sidepath':
            # 10 Cycling not permitted due to bicycle='use_sidepath' tag.
            return 10
        if 'access' in tags and tags['access'] == 'no':
            if 'bicycle' in tags and not tags['bicycle'] == 'no':
                return 100
            # 2 Cycling not permitted due to access='no' tag without bicyle != 'no'.
            return 2

        if effective_highway(tags, 'motorway'):
            # 3 Cycling not permitted due to highway=\'motorway\' tag.
            return 3
        if effective_highway(tags, 'motorway_link'):
            # 4 Cycling not permitted due to highway='motorway_link' tag.
            return 4
        if effective_highway(tags, 'proposed'):
            # 5 Cycling not permitted due to highway='proposed' tag.
            return 5
        if effective_highway(tags, 'construction'):
            # 8 Cycling not permitted due to highway='construction' tag.
            return 8
        if effective_highway(tags, 'corridor'):
            # 11 Cycling not permitted due to highway='corridor' tag.
            return 11
        if effective_highway(tags, 'platform'):
            # 12 Cycling not permitted due to highway='platform' tag.
            return 12

        if 'footway' in tags and tags['footway'] == 'sidewalk':
            if 'bicycle' in tags and tags['bicycle'] == 'yes':
                return 100
            if effective_highway(tags, 'footway'):
                # 6 Cycling not permitted. When footway='sidewalk' is present,
                # 6 there must be a bicycle='yes' when the highway is 'footway'.
                return 6
            if effective_highway(tags, 'path'):
                # 7 Cycling not permitted. When footway='sidewalk' is present,
                # 7 there must be a bicycle='yes' when the highway is 'path'.
                return 7
            return 100

        if effective_highway(tags, 'footway') or effective_highway(tags, 'steps'):
            if tag_starts_with(tags, 'cycleway'):
                # 101 footway with cycleway
                return 101
            if 'bicycle' in tags and tags['bicycle'] == 'yes':
                # 102 footway with explicit bicycle
                return 102
            # 9 footway without explicit cycleway or bicycle
            return 9

        # 100 highway or bicycle in tags
        return 100
    # 0 Way has neither a highway tag nor a bicycle=yes tag. The way is not a highway.
    return 0

def compute_level(tags):
    """ compute the quality level of a highway by its tags
    """
    _level = biking_permitted(tags)
    if _level >= 100:
        _level = cycleway(_level, tags)
        _level = cyclestreet(_level, tags)
        _level = lane(_level, tags)
        _level = track(_level, tags)
        _level = separated_path(_level, tags)

    return _level

def usage(argv0):
    print('{} [-o <output directory>] [-i <input file>]'.format(argv0))

if __name__ == "__main__":
    IN_FILE = 'default.osm.json'
    OUT_DIR = '.'
    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:], "hi:o:", ["help", "ifile=", "odir="])
    except getopt.GetoptError:
        usage(sys.argv[0])
        sys.exit(2)
    for opt, arg in OPTS:
        if opt in ('-h', '--help'):
            usage(sys.argv[0])
            sys.exit()
        elif opt in ("-o", "--odir"):
            OUT_DIR = arg
        elif opt in ("-i", "--ifile"):
            IN_FILE = arg
        else:
            usage(sys.argv[0])
            sys.exit(3)

    print('loading intermediates...')
    INTERMEDIATE_PATH = '%s' % IN_FILE
    INTERMEDIATE_INFILE = open(INTERMEDIATE_PATH, "r")
    INTERMEDIATE = json.load(INTERMEDIATE_INFILE)
    OSM_NODES = INTERMEDIATE['nodes']
    WAYS = INTERMEDIATE['ways']
    INTERMEDIATE_INFILE.close()

    print('calculating levels...')
    HIGHWAY_TYPES = {}
    ACCESS_TYPES = {}
    LEVELS = {}
    AREAS = 0
    PLATFORMS = 0

    for way_id in WAYS:
        _way = WAYS[way_id]
        _tags = _way['tags']

        _highway = _tags['highway']

        _count = 1
        if _highway in HIGHWAY_TYPES:
            _count = HIGHWAY_TYPES[_highway]
            _count = _count + 1
        HIGHWAY_TYPES[_highway] = _count

        if 'access' in _tags:
            _access = _tags['access']
            _count = 1
            if _access in ACCESS_TYPES:
                _count = ACCESS_TYPES[_access]
                _count = _count + 1
            ACCESS_TYPES[_access] = _count

        if 'area' in _tags and _tags['area'] == 'yes':
            AREAS = AREAS + 1
            continue

        if _highway == 'platform':
            PLATFORMS = PLATFORMS + 1
            continue

        _level = compute_level(_tags)

        _count = 1
        if _level in LEVELS:
            _count = LEVELS[_level]
            _count = _count + 1
        LEVELS[_level] = _count

        _way['level'] = _level

    print('AREAS {}'.format(AREAS))
    print('PLATFORMS {}'.format(PLATFORMS))
    print('LEVELS\n{}'.format(json.dumps(LEVELS, indent=4, sort_keys=True)))
    print('HIGHWAY_TYPES\n{}'.format(json.dumps(HIGHWAY_TYPES, indent=4, sort_keys=True)))
    print('ACCESS_TYPES\n{}'.format(json.dumps(ACCESS_TYPES, indent=4, sort_keys=True)))

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
            level = -1
            if 'level' in way:
                level = way['level']
            if int(level / 100) == outputLevel:
                outfile.write('{s:s}{{"type":"Feature","id":"way/{w:s}"\n'.format(
                    s=waysSeparator, w=way_id))
                waysSeparator = ','
                outfile.write(',"properties":{{"id":"way/{w:s}"\n'.format(w=way_id))
                outfile.write(',"quality":{q:d}\n'.format(q=level))
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
                        coordinateSeparator, osm_node['lon'], osm_node['lat']))
                        #coordinateSeparator, osm_node.lon, osm_node.lat))
                    coordinateSeparator = ','
                outfile.write(']}}\n')
        outfile.write(']}\n')
        outfile.close()

    print('finished!')
