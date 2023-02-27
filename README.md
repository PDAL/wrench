
# PDAL wrench

A collection of easy to use command line tools for processing of point cloud data:

- basic management of data (info, translate, merge, tile, thin, clip, boundary, density, to_vector)
- export of raster grids (to_raster, to_raster_tin)

And more algorithms will be added in the future!

Most of the tools are multi-threaded, making good use of all available CPUs for fast processing.

All tools are based on PDAL pipelines, also using the other usual geospatial libraries: GDAL/OGR, GEOS and PROJ.

Some may ask why not let users build their pipelines in PDAL directly. There are several reasons:

- ease of use: PDAL is great for advanced users, but not everyone finds it easy to manually craft JSON files with pipelines, study manuals of the many stages and read details about file formats involved
- parallel execution: PDAL runs pipelines in a single thread - only one CPU gets to do the work normally - and users need to implement their own parallelism if they wish so

# How to build

You will need: PDAL >= 2.5 and GDAL >= 3.0, both with development files.

Building is done with CMake:
```
mkdir build
cd build
cmake ..
make
```

If PDAL is not installed in the usual system paths (e.g. in `/usr`), then add `PDAL_DIR` parameter when running CMake - for example if your PDAL installation dir is `/home/martin/pdal-inst`:
```
cmake -DPDAL_DIR=/home/martin/pdal-inst/lib/cmake/PDAL ..
```

# Commands

## info

Prints basic metadata from the point cloud file:

```
pdal_wrench info --input=data.las
```

## translate

Convert to a different file format (e.g. create compressed LAZ):

```
pdal_wrench translate --input=data.las --output=data.laz
```

Reproject point cloud to a different coordinate reference system:

```
pdal_wrench translate --input=data.las --output=reprojected.las --transform-crs=EPSG:3857
```

Fix coordinate reference system (if not present or wrong):

```
pdal_wrench translate --input=data-with-invalid-crs.las --output=data.las --assign-crs=EPSG:3857
```


## boundary

Exports a polygon file containing boundary. It may contain holes and it may be a multi-part polygon.

```
pdal_wrench boundary --input=data.las --output=boundary.gpkg
```

## density

Exports a raster file where each cell contains number of points that are in that cell's area.

```
pdal_wrench density --input=data.las --resolution=1 --output=density.tif
```

## clip

Outputs only points that are inside of the clipping polygons.

```
pdal_wrench clip --input=data.las --polygon=clip.gpkg --output=data_clipped.las
```

## merge

Merges multiple point cloud files to a single one.

```
pdal_wrench merge --output=merged.las data1.las data2.las data3.las
```

## tile

Creates tiles from input data. For example to get tiles sized 100x100:

```
pdal_wrench tile --length=100 --output=/data/tiles data1.las data2.las data3.las
```

## thin

Creates a thinned version of the point cloud by only keeping every N-th point (`every-nth` mode) or keep points based on their distance (`sample` mode).

For example, to only keep every 20th point, so only 5% of points will be in the output:

```
pdal_wrench thin --output=thinned.las --mode=every-nth --step-every-nth=20 data.las
```

Alternatively, to sample points using Poisson sampling of the input:

```
pdal_wrench thin --output=thinned.las --mode=sample --step-sample=20 data.las
```

## to_raster

Exports point cloud data to a 2D raster grid, having cell size of given resolution, writing values from the specified attribute. Uses inverse distance weighting.

```
pdal_wrench to_raster --output=raster.tif --resolution=1 --attribute=Z data.las
```

## to_raster_tin

Exports point cloud data to a 2D raster grid like `to_raster` does, but using a triangulation of points and then interpolating cell values from triangles. It does not produce any "holes" when some data are missing. Only supports output of Z attribute.

```
pdal_wrench to_raster_tin --output=raster.tif --resolution=1 data.las
```

## to_vector

Exports point cloud data to a vector layer with 3D points (a GeoPackage), optionally with extra attributes:

```
pdal_wrench to_vector --output=data.gpkg data.las
```

# Virtual Point Clouds (VPC)

This is similar to GDAL's VRT - a single file referring to other files that contain actual data. Software then may handle all data as a single dataset.

To create a virtual point cloud:
```
pdal_wrench build_vpc --output=hello.vpc data1.las data2.las data3.las
```

Afterwards, other algorithms can be applied to a VPC:
```
pdal_wrench clip --input=hello.vpc --polygon=clip.gpkg --output=hello_clipped.vpc
```

This will create a grid for each data file separately in parallel and then merge the results to a final GeoTIFF:
```
pdal_wrench density --input=hello.vpc --resolution=1 --output=density.tif
```

When algorithms create derived VPCs, by default they use uncompressed LAS, but `--output-format=laz` option can switch to compressed LAZ.

## VPC support in algorithms

| Algorithm | VPC | Notes |
|--------------|-----------|--|
| info | yes | |
| boundary | multi-threaded | per file |
| density | multi-threaded | spatial tiling |
| clip | multi-threaded | per file |
| merge | not supported | |
| tile | multi-threaded | per file |
| thin | multi-threaded | per file |
| to_raster | multi-threaded | spatial tiling |
| to_raster_tin | multi-threaded | spatial tiling |
| to_vector | multi-threaded | per file |
| translate | multi-threaded | per file |
