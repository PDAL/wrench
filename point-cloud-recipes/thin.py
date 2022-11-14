
import argparse
import time
import pdal

from tqdm import tqdm


parser = argparse.ArgumentParser()
parser.add_argument('input_file')
parser.add_argument('-o', '--output', required=True)
parser.add_argument('-s', '--step', type=int, required=True)
args = parser.parse_args()
print(args)


r = pdal.Reader(args.input_file)

writer_args = {}
writer_args["forward"] = "all"  # TODO: maybe could use lower scale than the original

w = pdal.Writer(args.output, **writer_args)

# there are more options:
# - [str] filters.decimation - keep every N-th point
# - [not] filters.fps
# - [not] filters.relaxationdartthrowing - similar to filters.sample, shrinks radius each pass to get desired number of pts
# - [str] filters.sample
# - [not] filters.voxelcenternearestneighbor
# - [not] filters.voxelcentroidnearestneighbor
# - [str] filters.voxeldownsize

p = r | pdal.Filter.decimation(step=args.step) | w

t0 = time.time()

total_pts = p.quickinfo['readers.las']['num_points']
total_pts_str = "{:.1f}M pts".format(total_pts/1000000)

with tqdm(total=total_pts, desc="Thin", ncols=80, bar_format="{l_bar}{bar}| "+total_pts_str+" {remaining}") as pbar:
    pt = 0
    it = p.iterator(chunk_size=100000)
    for array in it:
        pt += 100000
        pbar.update(100000)
        #print("{:.1f} M / {:.1f} M pts".format(pt/1000000, total_pts/1000000))

t1 = time.time()
print("total: " + str(t1-t0) + " sec")
