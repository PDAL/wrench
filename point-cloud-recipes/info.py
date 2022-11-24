

import argparse
import time
import pdal

from tqdm import tqdm


# TODO:
# pipeline.metadata - need to access pipeline.metadata['metadata']  ...?
# pipeline.schema - need to access pipeline.schema['schema'] ...?

parser = argparse.ArgumentParser()
parser.add_argument('input_file')
#parser.add_argument('-o', '--output', required=True)
args = parser.parse_args()

# TODO: an ugly alternative to avoid executing full pipeline would be to run "pdal info"
# import json
# import subprocess
# pdal_info = subprocess.run(['pdal', 'info', args.input_file, '--metadata', '--schema'],
#                            stderr=subprocess.PIPE,
#                            stdout=subprocess.PIPE)
# info = json.loads(pdal_info.stdout.decode())
# reader_meta = info['metadata']
# schema_info = info['schema']

# TODO: unable to extract reader metadata+schema without
#  going through the whole dataset: for metadata it's enough to do at least one "next"
#  call, but for schema it's throwing "Pipeline has not been executed!" runtime error
#  unless all points get iterated through

p = pdal.Pipeline([pdal.Reader(args.input_file)])
total_pts = p.quickinfo['readers.las']['num_points']
total_pts_str = "{:.1f}M pts".format(total_pts/1000000)

with tqdm(total=total_pts, desc="Info", ncols=80, bar_format="{l_bar}{bar}| "+total_pts_str+" {remaining}") as pbar:
    pt = 0
    it = p.iterator(chunk_size=100000)
    for array in it:
        pt += 100000
        pbar.update(100000)

reader_meta = it.metadata['metadata']['readers.las']
schema_info = it.schema['schema']

#print(reader_meta.keys())
file_type = "LAS" if not reader_meta['compressed'] else "LAZ"
crs = reader_meta['srs']['wkt']    # TODO: nicer printing (e.g. only CRS name + EPSG ID)
if not crs:
    crs = "(unknown)"
print(f"LAS           {reader_meta['major_version']}.{reader_meta['minor_version']}")
print(f"point format  {reader_meta['dataformat_id']}")
print(f"count         {reader_meta['count']}")
print(f"scale         {reader_meta['scale_x']} {reader_meta['scale_y']} {reader_meta['scale_z']}")
print(f"offset        {reader_meta['offset_x']} {reader_meta['offset_y']} {reader_meta['offset_z']}")
print(f"extent        {reader_meta['minx']} {reader_meta['miny']} {reader_meta['minz']}")
print(f"              {reader_meta['maxx']} {reader_meta['maxy']} {reader_meta['maxz']}")
print(f"crs           {crs}")

# TODO: possibly show extra metadata: (probably --verbose mode)
# - creation date + software ID + system ID
# - filesource ID
# - VLR info

print("")
print("Attributes:")

def _format_dim_type(dim_size, dim_type):
    #dim_bits = dim_size * 8
    if dim_type == "floating":
        dim_str = "float"
    elif dim_type == "unsigned" or dim_type == "signed":
        dim_str = "int"
    else:
        dim_str = "???"
    return f"{dim_size}-byte " + dim_str

# what attributes are available
for dim_info in schema_info['dimensions']:
    dim_name = dim_info['name']
    dim_type_2 = _format_dim_type(dim_info['size'], dim_info['type'])
    print(f"  {dim_name:25} {dim_type_2}")
#print(pi.schema)

# TODO: stats of attributes (if requested)
