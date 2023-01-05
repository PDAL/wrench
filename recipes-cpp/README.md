
# Algorithms

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
| boundary | multi-threaded | |
| density | multi-threaded | must not have overlaps |
| clip | multi-threaded | |
