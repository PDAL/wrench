
# PDAL wrench

A collection of easy to use command line tools for processing of point cloud data:

- basic management of data (info, translate, merge, tile, thin, clip, boundary, density, to_vector, height_above_ground)
- export of raster grids (to_raster, to_raster_tin)
- classification (filter_noise, classify_ground)
- handle [virtual point clouds](vpc-spec.md) (build_vpc)

And more algorithms will be added in the future!

The whole suite of tools has been integrated into the QGIS Processing framework in QGIS starting from QGIS 3.32 (release in June 2023).
There is no plugin to install - everything is available in QGIS core - just open the Processing toolbox and search for point cloud algorithms.

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

# Parallel processing

PDAL runs point cloud pipelines in a single thread and any parallelization is up to users of the library.
PDAL wrench has parallel processing built in and tries to run pipelines in parallel. This generally happens in two scenarios:

- input dataset is in COPC or EPT format - these formats allow efficient spatial queries (to access only data in a particular bounding box),
  so PDAL wrench can split the input into multiple tiles that can be processed independently in parallel
- input dataset is a [virtual point cloud (VPC)](vpc-spec.md) - such datasets are composed of a number of files, so the whole work can be split into jobs
  where each parallel job processes one or more input files

If the input is a single LAS/LAZ file, no parallelization is attempted. This may change in the future with introduction of more complex algorithms (where the cost of reading the input is much lower than the cost of the actual algorithm).

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

Assign coordinate reference system (if not present or wrong):

```
pdal_wrench translate --input=data-with-invalid-crs.las --output=data.las --assign-crs=EPSG:3857
```

Transform data using a 4x4 transformation matrix:

```
pdal_wrench translate --input=data.las --output=data.las --transform-matrix="1 0 0 100 0 1 0 200 0 0 1 300 0 0 0 1"
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

Alternatively, it is possible to merge files whose paths are specified in a text file (one file per line)

```
pdal_wrench merge --output=merged.las --input-file-list=my_list.txt
```

## tile

Creates tiles from input data. For example to get tiles sized 100x100:

```
pdal_wrench tile --length=100 --output=/data/tiles data1.las data2.las data3.las
```

This tool can also read input data from a text file (one file per line)

```
pdal_wrench tile --length=100 --output=/data/tiles --input-file-list=my_list.txt
```

## thin

Creates a thinned version of the point cloud by only keeping every N-th point (`every-nth` mode) or keep points based on their distance (`sample` mode).

For example, to only keep every 20th point, so only 5% of points will be in the output:

```
pdal_wrench thin --output=thinned.las --mode=every-nth --step-every-nth=20 --input=data.las
```

Alternatively, to sample points using Poisson sampling of the input:

```
pdal_wrench thin --output=thinned.las --mode=sample --step-sample=20 --input=data.las
```

## to_raster

Exports point cloud data to a 2D raster grid, having cell size of given resolution, writing values from the specified attribute. Uses inverse distance weighting.

```
pdal_wrench to_raster --output=raster.tif --resolution=1 --attribute=Z --input=data.las
```

## to_raster_tin

Exports point cloud data to a 2D raster grid like `to_raster` does, but using a triangulation of points and then interpolating cell values from triangles. It does not produce any "holes" when some data are missing. Only supports output of Z attribute.

```
pdal_wrench to_raster_tin --output=raster.tif --resolution=1 --input=data.las
```

It is possible to prevent interpolation of large triangles using `max-triangle-edge-length` argument:

```
pdal_wrench to_raster_tin --output=raster.tif --resolution=1 --max-triangle-edge-length=100 --input=data.las
```

## to_vector

Exports point cloud data to a vector layer with 3D points (a GeoPackage), optionally with extra attributes:

```
pdal_wrench to_vector --output=data.gpkg --input=data.las
```

## classify_ground

Classify points as ground/non-ground using Simple Morphological Filter (SMRF).

```
pdal_wrench classify_ground --input=data.las --output=data_classified.las --cell-size=1 --scalar=1.25 --slope=0.15 --threshold=0.5 --window-size=18
```

## filter_noise

Classify points as noise/non-noise using either statistical or radius method.

```
pdal_wrench filter_noise --input=data.las --output=data_classified.las --algorithm=radius --radius-min-k=2 --radius-radius=1.0
```

```
pdal_wrench filter_noise --input=data.las --output=data_classified.las --algorithm=statistical --statistical-mean-k=8 --statistical-multiplier=2.0
```

## height_above_ground

Calculates height above ground either using Nearest Neighbor or Delaunay method. The algorithm adds HeightAboveGround dimension to the point cloud and can optionally replace Z values with height above ground.

```
pdal_wrench height_above_ground --input=data.las --output=data_hag.las --algorithm=nn --replace-z=false --nn-count=1 --nn-max-distance=0.0
```

```
pdal_wrench height_above_ground --input=data.las --output=data_hag.las --algorithm=delaunay --replace-z=true --delaunay-count=10
```

## compare

Compares two point clouds using M3C2 algorithm and outputs a point cloud with new dimensions: m3c2_distance, m3c2_uncertainty, m3c2_significant, m3c2_std_dev1, m3c2_std_dev2, m3c2_count1 and m3c2_count2. The input data is subsampled to create set of core points, subsampling can be modified using subsampling-cell-size parameter, if it is set to 0.0, no subsampling is done and all points are used.

```
pdal_wrench compare --input=first.las --input-compare=second.las --output=changes.las --subsampling-cell-size=1.0 --normal-radius=2.0 --cyl-radius=2.0 --cyl-halflen=5.0 --reg-error=0.0 --cyl-orientation=up
```


# Virtual Point Clouds (VPC)

This is similar to GDAL's VRT - a single file referring to other files that contain actual data. Software then may handle all data as a single dataset.

Virtual point clouds based on STAC protocol's ItemCollection, which is in fact a GeoJSON feature collection with extra metadata written in a standard way. See [VPC spec](vpc-spec.md) for more details on the file format.

To create a virtual point cloud:
```
pdal_wrench build_vpc --output=hello.vpc data1.las data2.las data3.las
```

Or, if the inputs are listed in a text file:
```
data1.las
data2.las
data3.las
```

You can provide that file as input:
```
pdal_wrench build_vpc --output=hello.vpc --input-file-list=inputs.txt
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
| merge | single-threaded | |
| tile | multi-threaded | per file |
| thin | multi-threaded | per file |
| to_raster | multi-threaded | spatial tiling |
| to_raster_tin | multi-threaded | spatial tiling |
| to_vector | multi-threaded | per file |
| translate | multi-threaded | per file |
| height_above_ground | multi-threaded | per file |
| filter_noise | multi-threaded | per file |
| classify_ground | multi-threaded | per file |
| compare | no | only available in PDAL Version > 2.10 |
