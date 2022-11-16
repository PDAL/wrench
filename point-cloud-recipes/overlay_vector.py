# assign a value to each point based on 2D polygons

import argparse
import time
import pdal

from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument('input_file')
parser.add_argument('-o', '--output', required=True)
parser.add_argument('-oa', '--output-attribute', required=True)
parser.add_argument('-p', '--polygon', required=True)
parser.add_argument('-pa', '--polygon-attribute', required=True)

args = parser.parse_args()
#print(args)

r = pdal.Reader(args.input_file)

# TODO: not sure what's wrong, all points get assigned zero in my test

overlay_args = {
    "dimension": args.output_attribute,
    "datasource": args.polygon,
    "column": args.polygon_attribute,
}

p = r | pdal.Filter.overlay(**overlay_args) | pdal.Writer(args.output, forward="all")

t0 = time.time()

total_pts = p.quickinfo['readers.las']['num_points']
total_pts_str = "{:.1f}M pts".format(total_pts/1000000)

with tqdm(total=total_pts, desc="Overlay vector", ncols=80, bar_format="{l_bar}{bar}| "+total_pts_str+" {remaining}") as pbar:
    pt = 0
    it = p.iterator(chunk_size=100000)
    for array in it:
        pt += 100000
        pbar.update(100000)
        #print("{:.1f} M / {:.1f} M pts".format(pt/1000000, total_pts/1000000))

t1 = time.time()
