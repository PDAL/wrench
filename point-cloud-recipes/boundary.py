

import argparse
import time
import pdal


parser = argparse.ArgumentParser()
parser.add_argument('input_file')
parser.add_argument('-o', '--output', required=True)
args = parser.parse_args()
print(args)

r = pdal.Reader(args.input_file)

# TODO: what edge size? (by default samples 5000 points if not specified
# TODO: set threshold ? (default at least 16 points to keep the cell)
# btw. if threshold=0, there are still missing points because of simplification (smooth=True)

p = r | pdal.Filter.hexbin(edge_size=1, threshold=0)

t0 = time.time()

print(p.execute_streaming())

t1 = time.time()
print("total: " + str(t1-t0) + " sec")

m = p.metadata['metadata']
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
