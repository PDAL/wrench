
# TODO: this needs PDAL 2.5 because of "binmode" option in writers.gdal

import argparse
import time
import pdal

from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument('input_file')
parser.add_argument('-o', '--output', required=True)
parser.add_argument('-r', '--resolution', required=True, type=float)
args = parser.parse_args()
#print(args)

# TODO: some reasonable GDAL writer options (COG?, compression?)

r = pdal.Reader(args.input_file)

w = pdal.Writer(args.output, binmode=True, output_type="count", resolution=args.resolution)

p = r | w

t0 = time.time()

total_pts = p.quickinfo['readers.las']['num_points']
total_pts_str = "{:.1f}M pts".format(total_pts/1000000)

with tqdm(total=total_pts, desc="Density", ncols=80, bar_format="{l_bar}{bar}| "+total_pts_str+" {remaining}") as pbar:
    pt = 0
    it = p.iterator(chunk_size=100000)
    for array in it:
        pt += 100000
        pbar.update(100000)
        #print("{:.1f} M / {:.1f} M pts".format(pt/1000000, total_pts/1000000))

t1 = time.time()
#print("total: " + str(t1-t0) + " sec")
