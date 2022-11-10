

import argparse
import time
import pdal


# TODO:
# - is it possible to get Reader metadata without executing pipeline? (like "pdal info --metadata")
# pipeline.metadata - need to access pipeline.metadata['metadata']  ...?
# pipeline.schema - need to access pipeline.schema['schema'] ...?

parser = argparse.ArgumentParser()
parser.add_argument('input_file')
#parser.add_argument('-o', '--output', required=True)
args = parser.parse_args()

pi = pdal.Pipeline([pdal.Reader(args.input_file)])
pi.execute()
reader_meta = pi.metadata['metadata']['readers.las']
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
for dim_info in pi.schema['schema']['dimensions']:
    dim_name = dim_info['name']
    dim_type_2 = _format_dim_type(dim_info['size'], dim_info['type'])
    print(f"  {dim_name:25} {dim_type_2}")
#print(pi.schema)

# TODO: stats of attributes (if requested)
