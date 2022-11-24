# will construct a pipeline according to the command line args and run it

import argparse
import time
import pdal

from tqdm import tqdm


parser = argparse.ArgumentParser()
parser.add_argument('input_file')
parser.add_argument('-o', '--output', required=True)
parser.add_argument('-r', '--resolution', type=float, required=True)
parser.add_argument('-a', '--attribute')
# TODO: pick
args = parser.parse_args()
print(args)

r = pdal.Reader(args.input_file)

# TODO: could export multiple raster files using multiple Writer() stages with different "where" clauses

# TODO: "combined product" - bands: DTM + HAG + DSM + noise point count + intensity + max num of returns
#              ... + attach names for bands  (+ attach RAT [return number/class])
#   (lerc for float bands [max_z_err = [scale of point clouds]]   / max. compatibility mode LZW)

radius = args.resolution * (2**0.5)
writer_args = {
    "resolution": args.resolution,
    "radius": radius,
}
if args.attribute is not None:
    writer_args["dimension"] = args.attribute
w = pdal.Writer(args.output, **writer_args)

# TODO: binmode=true for writer -- from pdal 2.5

# TODO: use COG by default? set up gdal options (compression...) ?

# TODO? could export raster attribute table gdal_opts/metadata

# TODO: control origin point (to line up) - optional input parameter

p = r | w

t0 = time.time()

total_pts = p.quickinfo['readers.las']['num_points']
total_pts_str = "{:.1f}M pts".format(total_pts/1000000)

with tqdm(total=total_pts, desc="Export raster", ncols=80, bar_format="{l_bar}{bar}| "+total_pts_str+" {remaining}") as pbar:
    pt = 0
    it = p.iterator(chunk_size=100000)
    for array in it:
        pt += 100000
        pbar.update(100000)
        #print("{:.1f} M / {:.1f} M pts".format(pt/1000000, total_pts/1000000))


t1 = time.time()
print("total: " + str(t1-t0) + " sec")
