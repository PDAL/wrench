# will construct a pipeline according to the command line args and run it

import argparse
import time
import pdal


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

p.execute()
t1 = time.time()
print("total: " + str(t1-t0) + " sec")

"""
r = pdal.Reader("trencin-2-ground.laz")
hb = pdal.Filter.hexbin(edge_size=1)
#w = pdal.Writer("/tmp/out.las")

p = pdal.Pipeline([r, hb])
print(p.execute_streaming())
#hb.metadata
print(p.metadata.keys())
m = p.metadata['metadata']
print(m)
print(m['filters.hexbin']['boundary'])
"""
