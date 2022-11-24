
import argparse
import time
import pdal

from tqdm import tqdm


parser = argparse.ArgumentParser()
parser.add_argument('input_file')
parser.add_argument('-o', '--output', required=True)
args = parser.parse_args()
print(args)

"""
Warning: PDAL 2.3.0 (ubuntu 22.04) crashes on any format. Fixed in 2.4.0 (https://github.com/PDAL/PDAL/pull/3618)
Warning: GeoPackage working only in PDAL >= 2.5.0: https://github.com/PDAL/PDAL/pull/3865
"""

# TODO: only from PDAL >= 2.5 it is possible to save extra attributes:
#   https://github.com/PDAL/PDAL/pull/3837

# TODO: limit of points? 4M pts creates roughly 400 MB gpkg or 250 MB shp

r = pdal.Reader(args.input_file)

writer_args = {
    'filename': args.output,
    'ogrdriver': 'GPKG'
}
w = pdal.Writer.ogr(**writer_args)

p = r | w

t0 = time.time()

total_pts = p.quickinfo['readers.las']['num_points']
total_pts_str = "{:.1f}M pts".format(total_pts/1000000)

with tqdm(total=total_pts, desc="Export to vector", ncols=80, bar_format="{l_bar}{bar}| "+total_pts_str+" {remaining}") as pbar:
    pt = 0
    it = p.iterator(chunk_size=100000)
    for array in it:
        pt += 100000
        pbar.update(100000)
        #print("{:.1f} M / {:.1f} M pts".format(pt/1000000, total_pts/1000000))

t1 = time.time()
print("total: " + str(t1-t0) + " sec")
