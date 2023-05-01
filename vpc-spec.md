# Virtual Point Cloud (VPC)

## Purpose

Draft specification for a file format that groups multiple point cloud files to be treated as a single dataset.

Inspired by GDAL's VRTs and PDAL's tindex.

Goals:
- load VPC in QGIS as a single point cloud layer (rather than each file as a separate map layer)
- run processing tools on a VPC as input
- simple format that's easy to read/write
- allow referencing both local and remote datasets
- allow working with both indexed (e.g. COPC or EPT) and non-indexed (e.g. LAS/LAZ) datasets

Non-goals:
- support other kinds of data than (georeferenced) point clouds

## File format

We are using [STAC API ItemCollection](https://github.com/radiantearth/stac-api-spec/blob/main/fragments/itemcollection/README.md) as the file format and expecting these STAC extensions:
 - [pointcloud](https://github.com/stac-extensions/pointcloud/)
 - [projection](https://github.com/stac-extensions/projection/)

Note: ItemCollection not the same thing as a [STAC Collection](https://github.com/radiantearth/stac-spec/blob/master/collection-spec/README.md). An ItemCollection is essentially a single JSON file representing a GeoJSON FeatureCollection containing STAC Items. A STAC Collection is also a JSON file,
but with a different structure and extra metadata, but more importantly, it only links to other standalone JSON files (STAC items) which
is impractical for our use case as we strongly prefer to have the whole virtual point cloud definition in a single file (for easy manipulation).

We use `.vpc` extension (to allow easy format recognition based on the extension).

Normally a virtual point cloud file will not provide any links to other STAC entities (e.g. to a parent, to a root or to self) because often it will be created ad-hoc.

Why STAC:
- it is a good fit into the larger ecosystem of data catalogs, avoiding creation of a new format
- supported natively by PDAL as well (readers.stac)
- search endpoint on STAC API servers returns the same ItemCollection that we use, so a search result can be fed directly as input
- the ItemCollection file is an ordinary GeoJSON and other clients can consume it (to at least show boundaries of individual files)

### Coordinate Reference Systems (CRS)

Each referenced file can have its own CRS and it is defined through the "projection" STAC extension - either using `proj:epsg` or `proj:wkt2` or `proj:projjson`. It is recommended that a single virtual point cloud only references files in the same CRS.

Please note that `proj:epsg` only allows a single EPSG code to be specified. When working with a compound CRS that has an EPSG code for both horizontal and vertical CRS (often written as `EPSG:1234+5678` where `EPSG:1234` is horizontal and `EPSG:5678` vertical), but there is no EPSG code for the compound CRS, this can't be encoded in `proj:epsg` and it is preferrable to use an alternative encoding (e.g. `proj:wkt2`).

### Statistics

The STAC pointcloud extension defines optional `pc:statistics` entry with statistics for each attribute. There is a limitation that currently it does not define how to store distinct values where it makes sense and their counts (e.g. Classification attribute) - see https://github.com/stac-extensions/pointcloud/issues/5.

### Boundaries

The format requires that boundaries of referenced files are defined in WGS 84 (since GeoJSON requires that) - either as a simple 2D or 3D bounding box or as a boundary geometry (polygon / multi-polygon). In addition to that, the "projection" STAC extension allows that the bounding box or boundary geometry can be specified in native coordinate reference system - this is strongly recommended and if `proj:bbox` or `proj:geometry` are present, they will be used instead of their WGS 84 equivalents.

It is also strongly recommended to provide bounding box in 3D rather than just 2D bounding box (3D viewers can correctly place the expected box in the 3D space rather than guessing the vertical range).

### Overviews

Overviews are useful for client software to show preview of the point cloud when zoomed out, without having to open all individual files and only rely on overviews
(the same idea as with overviews of raster layers).
Overviews are an optional feature, they do not need to be provided.

In a simple case, there would be a single overview point cloud for a whole VPC - using thinned original data (e.g. every 1000-th point) and merged from individual data files to a single file.

In case of very large point clouds, using a single overview point cloud may not be enough, and it may be useful to have a hierarchy of overviews with a tiling scheme (e.g.  1 overview at level 0, 4 overviews at level 1, 16 overviews at level 2 - each level having different density).

Overviews are defined as extra assets of STAC items in addition to the actual data file - it is expected that they have `overview` role defined. An overview point cloud may be referenced from multiple STAC items.

In case of a hierarchy of overviews, each STAC item may have multiple overview assets linked (e.g. one for level 0, one for level 1, one for level 2). STAC protocol does not provide a way to distinguish which overview is at what level (no place to write spacing between points or density), it is up to the client software to collect all referenced overviews and query their properties.

A sample of encoding overview point cloud in addition to the actual data:
```json
      "assets": {
        "data": {
          "href": "./mydata_54_1.copc.laz",
          "roles": [
            "data"
          ]
        },
        "overview": {
          "href": "./mydata-overview.copc.laz",
          "roles": [
            "overview"
          ]
        }
      }
```
