

import argparse
import time
import pdal


parser = argparse.ArgumentParser()
parser.add_argument('input_file')
parser.add_argument('-o', '--output', required=True)
parser.add_argument('-r', '--resolution', type=float, required=True)
#parser.add_argument('-a', '--attribute')  # other attributes not supported
args = parser.parse_args()

r = pdal.Reader(args.input_file)

p = r | pdal.Filter.delaunay() | pdal.Filter.faceraster(resolution=args.resolution) | pdal.Writer.raster(filename=args.output)

# TODO: use COG by default? set up gdal options (compression...) ?

t0 = time.time()

p.execute()
t1 = time.time()
print("total: " + str(t1-t0) + " sec")
