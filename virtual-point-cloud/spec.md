# Virtual Point Cloud (VPC)

Draft specification for a file format that groups multiple point cloud files to be treated as a single dataset.

Inspired by GDAL's VRTs and PDAL's tindex.

Goals:
- load VPC in QGIS as a single point cloud layer (rather than each file as a separate map layer)
- run processing tools on a VPC as input

Non-goals:
- ?

## File format

A vpc is a GeoPackage file with .vpc extension (to allow easy format recognition based on the extension).

Why GeoPackage:
- a single file
- standardized and well supported by tools (OGR, QGIS, ...)
- allows multiple tables
- supports various coordinate reference systems
- efficient storage / querying of data

## Tables

### files

The main table that references individual files in the dataset.

- polygon geometry (or multi-polygon) - file boundary - either a simple rectangle or more detailed shape
- attributes:
  - filename - relative or absolute path 
  - point count

### metadata

Key-value store for any kind of required and optional metadata.

- non-spatial table
- attributes:
  - key (string)
  - value (string)

Required:
- ?

Optional:
- stats - JSON with basic stats for each dimension

### overviews

An optional table that lists thinned/merged(?) versions of the raw data - this may be useful for viewers to display the point cloud when zoomed out a lot (the same idea as with overviews of raster layers).

- polygon geometry (or multi-polygon)
- attributes:
  - filename
  - point count
  - resolution / spacing / scale / ? - to give viewer information when to use the overview file
  
## Details

- referenced files should always have the same CRS

## To do

- dealing with remote files (?)
- other formats than just LAS/LAZ/COPC files (and implications?)


## Alternatives Considered

- STAC - it would require a directory of JSON files (one JSON file per LAS/LAZ/COPC file) which is impractical for our use case. Single-file STAC encoding deprecated: https://github.com/stac-extensions/single-file-stac
  - should be possible to have a relatively simple 1:1 conversion between VPC and STAC formats if needed
