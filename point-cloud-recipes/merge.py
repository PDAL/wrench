



import argparse
import time
import pdal


parser = argparse.ArgumentParser()
parser.add_argument('input_files', metavar='input_file', nargs='+')
parser.add_argument('-o', '--output', required=True)
args = parser.parse_args()
print(args)

pipe = [ pdal.Reader(f) for f in args.input_files ]
pipe.append( pdal.Writer(args.output, forward="all"))

# forward="all" means forwarding of:
# - "header" - major_version, minor_version, dataformat_id, filesource_id, global_encoding,
#              project_id, system_id, software_id, creation_doy, creation_year
# - "scale"  - scale_x, scale_y, scale_z
# - "offset" - offset_x, offset_y, offset_z
# - "vlr"    - VLRs can be forwarded by using the special value vlr. VLRs containing the following
#              User IDs are NOT forwarded: LASF_Projection, liblas, laszip encoded. VLRs with the User ID
#              LASF_Spec and a record ID other than 0 or 3 are also not forwarded. These VLRs are known
#              to contain information regarding the formatting of the data and will be rebuilt properly
#              in the output file as necessary. Unlike header values, VLRs from multiple input files are
#              accumulated and each is written to the output file. Forwarded VLRs may contain duplicate
#              User ID/Record ID pairs.
#
# !!! If a LAS file is the result of multiple LAS input files,
# the header values to be forwarded must match or they will be ignored and a default will be used instead.

p = pdal.Pipeline(pipe)

t0 = time.time()

print(p.execute_streaming())

t1 = time.time()
print("total: " + str(t1-t0) + " sec")
