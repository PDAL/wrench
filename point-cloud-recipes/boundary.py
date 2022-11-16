

import argparse
import time
import pdal

from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument('input_file')
parser.add_argument('-o', '--output', required=True)
args = parser.parse_args()
#print(args)

r = pdal.Reader(args.input_file)

# TODO: what edge size? (by default samples 5000 points if not specified
# TODO: set threshold ? (default at least 16 points to keep the cell)
# btw. if threshold=0, there are still missing points because of simplification (smooth=True)

p = r | pdal.Filter.hexbin(edge_size=1, threshold=0)

# TODO: if COPC/EPT used as input - could do just a low resolution boundary

# TODO: maybe use binmode=true from PDAL 2.5 - get raster, then extract boundary

t0 = time.time()

total_pts = p.quickinfo['readers.las']['num_points']
total_pts_str = "{:.1f}M pts".format(total_pts/1000000)

with tqdm(total=total_pts, desc="Boundary", ncols=80, bar_format="{l_bar}{bar}| "+total_pts_str+" {remaining}") as pbar:
    pt = 0
    it = p.iterator(chunk_size=100000)
    for array in it:
        pt += 100000
        pbar.update(100000)
        #print("{:.1f} M / {:.1f} M pts".format(pt/1000000, total_pts/1000000))

t1 = time.time()
#print("total: " + str(t1-t0) + " sec")

#m = p.metadata['metadata']   # when pipeline executes in "standard" mode: p.execute()
m = it.metadata['metadata']
wkt = m['filters.hexbin']['boundary']
is_multi = wkt.startswith("MULTI")


import osgeo.ogr as ogr
import osgeo.osr as osr

srs = osr.SpatialReference()
srs.ImportFromEPSG(5514)  # TODO

# write geopackage with boundary
driver = ogr.GetDriverByName("GPKG")  # TODO: other drivers
data_source = driver.CreateDataSource(args.output)
layer = data_source.CreateLayer("boundary", srs, ogr.wkbMultiPolygon if is_multi else ogr.wkbPolygon)
feature = ogr.Feature(layer.GetLayerDefn())
point = ogr.CreateGeometryFromWkt(wkt)
feature.SetGeometry(point)
layer.CreateFeature(feature)
feature = None
data_source = None
