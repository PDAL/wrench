
import argparse
import time
import pdal


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

pi = pdal.Pipeline()
pi |= pdal.Reader(args.input_file, **reader_args)
if args.reproject is not None:
    # TODO: try to parse & validate CRS first
    # TODO: try to figure out good scale+offset
    pi |= pdal.Filter.reprojection(out_srs=args.reproject)


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
pi |= pdal.Writer(args.output, **writer_args)

#pi.execute()
pi.execute_streaming()
