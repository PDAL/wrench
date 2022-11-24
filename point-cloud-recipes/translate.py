
import argparse
import time
import pdal

from tqdm import tqdm


parser = argparse.ArgumentParser()
parser.add_argument('input_file')
parser.add_argument('-o', '--output', required=True)
parser.add_argument('-a_crs', '--assign-crs')
parser.add_argument('-o_crs', '--reproject')
args = parser.parse_args()


reader_args = {}
if args.assign_crs is not None:
    # TODO: try to parse & validate CRS first
    reader_args['override_srs'] = args.assign_crs

p = pdal.Pipeline()
p |= pdal.Reader(args.input_file, **reader_args)
if args.reproject is not None:
    # TODO: try to parse & validate CRS first
    # TODO: try to figure out good scale+offset
    p |= pdal.Filter.reprojection(out_srs=args.reproject)


writer_args = {
    "forward": "all",
}
if args.reproject is not None:
    # avoid adding offset as it probably wouldn't work
    # TODO: maybe adjust scale as well - depending on the CRS
    writer_args["forward"] = "header,scale,vlr"
    writer_args["offset_x"] = "auto"
    writer_args["offset_y"] = "auto"
    writer_args["offset_z"] = "auto"
p |= pdal.Writer(args.output, **writer_args)

#pi.execute()
#pi.execute_streaming()

total_pts = p.quickinfo['readers.las']['num_points']
total_pts_str = "{:.1f}M pts".format(total_pts/1000000)

with tqdm(total=total_pts, desc="Translate", ncols=80, bar_format="{l_bar}{bar}| "+total_pts_str+" {remaining}") as pbar:
    pt = 0
    it = p.iterator(chunk_size=100000)
    for array in it:
        pt += 100000
        pbar.update(100000)
        #print("{:.1f} M / {:.1f} M pts".format(pt/1000000, total_pts/1000000))
