#!/usr/bin/env python

from TileCache.Layer import Layer
from TileCache import Service
import urllib2
import os
import sys


# based off of Client.py in TileCache
# instead of seeding the tile it downloads a remote tile to a local tilecache directory
# requires TileCache
# works only with 900913 now
# may need patch that is included layer.patch for TileCache


# Example 
# tilescrape.py osm_haiti_overlay_900913 14 15 -b -8060524.4099415,2098983.5250667,-8047405.9078053,2105069.822124 -l /tmp/tilecache -n http://http://tile1.dbsgeo.com/1.0.0 -e png


# download each tile for this level, and put it in the appropriate directory
# need to use portable paths
def location(x, y, z):
    components = "%02d/%03d/%03d/%03d/%03d/%03d" % ( z, int(x / 1000000), ((int(x) / 1000) % 1000), (int(x) % 1000),  int(y / 1000000),  (int(y / 1000) % 1000)) 
    return components


def scrape(layer, zoom_start, zoom_end, bbox, network_tilecache, local_tilecache, extension):
    lyr = Layer(layer, spherical_mercator="yes", size="256,256")
    # extent over haiti
    #bbox = (-8060524.4099415,2098983.5250667,-8047405.9078053,2105069.8221249)


    rangez = range(zoom_start, zoom_end)
    
    for z in rangez:          
        # get the tiles on the bottomleft and topright
        bottomleft = lyr.getClosestCell(z, bbox[0:2])
        topright   = lyr.getClosestCell(z, bbox[2:4])

        # get a list of the cell locations for the extent
        rangex =  range(bottomleft[0], topright[0] + 1)
        rangey = range(bottomleft[1], topright[1] + 1)
    
        for x in rangex:
            for y in rangey: 
                tile_location = "/%s/%s/%s" % ( local_tilecache, layer, location(x, y, z) )
                tile_name = "%03d.png" % (int(y) % 1000)

                if not os.path.exists(tile_location):
                    os.makedirs(tile_location)
                
                url = "%s/%s/%s/%s/%s/%s" % (network_tilecache, layer, z, x, y, extension)                        
                print url
                #sys.exit()
                tile = urllib2.urlopen(url)
                full_tile = "%s/%s" % (tile_location, tile_name)
                print full_tile
                tile_out = open(full_tile, "w")
                tile_out.write(tile.read())


def main():
    try:
        from optparse import OptionParser
    except:
        raise Exception("tilescraper needs optparse. You need a newer version of Python.")

    usage = "usage: %prog <layer> [<zoom start> <zoom stop>]"
    parser = OptionParser(usage=usage, version="tilecache.py 0.1")
    parser.add_option('-b', '--bbox', action='store', type='string', dest='bbox',default=None, help="restrict to specific bounding box")
    parser.add_option('-l', '--local_tilecache', action='store', type='string', dest='local_tilecache', default=None, help="place to put the tiles locally")
    parser.add_option('-n', '--network_tilecache', action='store', type='string', dest='network_tilecache', default=None, help="place to scrape tiles, input url like http://foo.com/1.0.0, if it is a TMS")
    parser.add_option('-e', '--extension', action='store', type='string', dest='extension', default=None, help="file extension that the tiles are stored in, e.g. png")
    
    
    (options, args) = parser.parse_args()

    if len(args)>3:
        parser.error("Too many arguments")

    if len(args)<1:
        parser.print_help()
        exit(-1)

    layer = args[0]
    if options.bbox:
        bboxlist = map(float,options.bbox.split(","))
    else:
        bboxlist=None

    zoom_start = int(args[1])
    zoom_end = int(args[2])
    
    scrape(layer, zoom_start, zoom_end, bboxlist, options.network_tilecache, options.local_tilecache, options.extension)
    
    
    
if __name__ == '__main__':
    main()



