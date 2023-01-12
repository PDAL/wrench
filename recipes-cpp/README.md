
# Algorithms

## info

Prints basic metadata from the point cloud file:

```
pdal_workbench info --input=data.las
```

## translate

Convert to a different file format (e.g. create compressed LAZ):

```
pdal_workbench translate --input=data.las --output=data.laz
```

Reproject point cloud to a different coordinate reference system:

```
pdal_workbench translate --input=data.las --output=reprojected.las --transform-crs=EPSG:3857
```

Fix coordinate reference system (if not present or wrong):

```
pdal_workbench translate --input=data-with-invalid-crs.las --output=data.las --assign-crs=EPSG:3857
```


## boundary

Exports a polygon file containing boundary. It may contain holes and it may be a multi-part polygon.

```
pdal_workbench boundary --input=data.las --output=boundary.gpkg
```

## density

Exports a raster file where each cell contains number of points that are in that cell's area.

```
pdal_workbench density --input=data.las --resolution=1 --output=density.tif
```

## clip

Outputs only points that are inside of the clipping polygons.

```
pdal_workbench clip --input=data.las --polygon=clip.gpkg --output=data_clipped.las
```

## merge

Merges multiple point cloud files to a single one.

```
pdal_workbench merge --output=merged.las data1.las data2.las data3.las
```

## thin

Creates a thinned version of the point cloud by only keeping every N-th point. This will only keep every 20th point, so only 5% of points will be in the output:

```
pdal_workbench thin --output=thinned.las --step=20 data.las
```

## to_raster

Exports point cloud data to a 2D raster grid, having cell size of given resolution, writing values from the specified attribute. Uses inverse distance weighting.

```
pdal_workbench to_raster --output=raster.tif --resolution=1 --attribute=Z data.las
```

## to_raster_tin

Exports point cloud data to a 2D raster grid like `to_raster` does, but using a triangulation of points and then interpolating cell values from triangles. It does not produce any "holes" when some data are missing. Only supports output of Z attribute.

```
pdal_workbench to_raster_tin --output=raster.tif --resolution=1 data.las
```

## to_vector

Exports point cloud data to a vector layer with 3D points (a GeoPackage), optionally with extra attributes:

```
pdal_workbench to_vector --output=data.gpkg data.las
```

# Virtual Point Clouds (VPC)

This is similar to GDAL's VRT - a single file referring to other files that contain actual data. Software then may handle all data as a single dataset.

To create a virtual point cloud:
```
pdal_workbench build_vpc --output=hello.vpc data1.las data2.las data3.las
```

Afterwards, other algorithms can be applied to a VPC:
```
pdal_workbench clip --input=hello.vpc --polygon=clip.gpkg --output=hello_clipped.vpc
```

This will create a grid for each data file separately in parallel and then merge the results to a final GeoTIFF:
```
pdal_workbench density --input=hello.vpc --resolution=1 --output=density.tif
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
| thin | multi-threaded | per file |
| to_raster | multi-threaded | spatial tiling |
| to_raster_tin | multi-threaded | spatial tiling |
| to_vector | multi-threaded | per file |
| translate | multi-threaded | per file |
