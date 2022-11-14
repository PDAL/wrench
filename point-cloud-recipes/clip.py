
import argparse
import time
import pdal
from osgeo import ogr

from tqdm import tqdm


parser = argparse.ArgumentParser()
parser.add_argument('input_file')
parser.add_argument('-o', '--output', required=True)
parser.add_argument('-p', '--polygon', required=True)
args = parser.parse_args()
print(args)

# load polygons
polygon_wkts = []
ogr_file = ogr.Open(args.polygon)  # TODO: error handling
ogr_layer = ogr_file.GetLayer(0)
for feature in ogr_layer:
    geom = feature.GetGeometryRef()
    wkt = geom.ExportToWkt()
    polygon_wkts.append(wkt)
ogr_layer.ResetReading()
del ogr_layer
del ogr_file


r = pdal.Reader(args.input_file)

writer_args = {}
writer_args["forward"] = "all"

w = pdal.Writer(args.output, **writer_args)

# TODO: CRS handling - either here or by using "a_srs",
#  but "a_srs" would not have enough data about datum transforms

# filters.crop -- does not support OGR, more efficient point-in-polygon testing?
# -or-
# filters.overlay -- writes a dimension, does not filter

p = r | pdal.Filter.crop(polygon=polygon_wkts) | w

t0 = time.time()

total_pts = p.quickinfo['readers.las']['num_points']
total_pts_str = "{:.1f}M pts".format(total_pts/1000000)

# TODO: progress does not finish at 100%
#  (e.g. stopped at 70% when clipping 17% of points)
with tqdm(total=total_pts, desc="Clip", ncols=80, bar_format="{l_bar}{bar}| "+total_pts_str+" {remaining}") as pbar:
    pt = 0
    it = p.iterator(chunk_size=100000)
    for array in it:
        pt += 100000
        pbar.update(100000)
        #print("{:.1f} M / {:.1f} M pts".format(pt/1000000, total_pts/1000000))

#p.execute()
t1 = time.time()
print("total: " + str(t1-t0) + " sec")
