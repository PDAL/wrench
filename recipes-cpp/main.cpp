
/*
TODO:
- algs that output point cloud: support multi-copc or single-copc output - as a post-processing step?
- VPC: overlapping files? do not allow - require tiling
*/

#include <iostream>
#include <vector>

#include "alg.hpp"
#include "vpc.hpp"


int main(int argc, char* argv[])
{
#if 0
    if (argc < 2)
    {
        std::cerr << "need to specify command:" << std::endl;
        std::cerr << " - boundary" << std::endl;
        std::cerr << " - clip" << std::endl;
        std::cerr << " - density" << std::endl;
        std::cerr << " - build_vpc" << std::endl;
        std::cerr << " - merge" << std::endl;
        std::cerr << " - to_raster" << std::endl;
        std::cerr << " - to_raster_tin" << std::endl;
        return 1;
    }
    std::string cmd = argv[1];

    std::vector<std::string> args;
    for ( int i = 2; i < argc; ++i )
        args.push_back(argv[i]);
#elif 0
    std::string cmd = "density";
    std::vector<std::string> args;
    // args.push_back("-i");
    // args.push_back("/home/martin/qgis/point-cloud-sandbox/data/24-fixed.las");
    // args.push_back("-o");
    // args.push_back("/tmp/dens.tif");
    // args.push_back("-r");
    // args.push_back("1");
    //args.push_back("xxx");

    args.push_back("--input=/home/martin/qgis/point-cloud-sandbox/data/merged.copc.laz");
    args.push_back("--output=/tmp/densX.tif");
    args.push_back("--resolution=1");
    args.push_back("--tile-size=250");
    args.push_back("--tile-origin-x=0");
    args.push_back("--tile-origin-y=0");
    args.push_back("--threads=4");
#elif 0
    std::string cmd = "boundary";
    std::vector<std::string> args;

    args.push_back("--input=/home/martin/qgis/point-cloud-sandbox/data/24-fixed.las");
    //args.push_back("--input=/home/martin/qgis/point-cloud-sandbox/data/merged.copc.laz"); // TODO: empty boundary???
    args.push_back("--output=/tmp/boundary.gpkg");
    //args.push_back("--resolution=1");
    //args.push_back("--tile-size=250");
    //args.push_back("--threads=4");
#elif 0
    std::string cmd = "clip";
    std::vector<std::string> args;

    args.push_back("--input=/home/martin/qgis/point-cloud-sandbox/data/24-fixed.las");
    args.push_back("--polygon=/home/martin/qgis/point-cloud-sandbox/data/24-polygon.gpkg");
    args.push_back("--output=/tmp/clipped.las");
#elif 0
    std::string cmd = "build_vpc";
    std::vector<std::string> args;
    args.push_back("--output=/tmp/tatry-9.vpc");
    args.push_back("/home/martin/tatry-tiles/tatry_0_1.laz");
    args.push_back("/home/martin/tatry-tiles/tatry_0_2.laz");
    args.push_back("/home/martin/tatry-tiles/tatry_0_3.laz");
    args.push_back("/home/martin/tatry-tiles/tatry_1_1.laz");
    args.push_back("/home/martin/tatry-tiles/tatry_1_2.laz");
    args.push_back("/home/martin/tatry-tiles/tatry_1_3.laz");
    args.push_back("/home/martin/tatry-tiles/tatry_2_1.laz");
    args.push_back("/home/martin/tatry-tiles/tatry_2_2.laz");
    args.push_back("/home/martin/tatry-tiles/tatry_2_3.laz");
#elif 0
    std::string cmd = "clip";
    std::vector<std::string> args;

    args.push_back("--input=/tmp/tatry-9.vpc");
    args.push_back("--polygon=/home/martin/qgis/point-cloud-sandbox/data/tatry.gpkg");
    args.push_back("--output=/tmp/tatry-clipped.vpc");
    //args.push_back("--output-format=laz");

#elif 0
    std::string cmd = "density";
    std::vector<std::string> args;
    args.push_back("--input=/tmp/first.vpc");
    args.push_back("--output=/tmp/first.tif");
    args.push_back("--resolution=1");
    args.push_back("--threads=4");
    // for good alignment of input and output
    args.push_back("--tile-origin-x=377250");
    args.push_back("--tile-origin-y=5441420");

#elif 0
    std::string cmd = "boundary";
    std::vector<std::string> args;
    args.push_back("--input=/tmp/tatry-9.vpc");
    args.push_back("--output=/tmp/tatry-9-boundary.gpkg");
#elif 0
    std::string cmd = "merge";
    std::vector<std::string> args;
    args.push_back("--output=/tmp/merged.las");
    args.push_back("/home/martin/qgis/point-cloud-sandbox/data/trencin-2-ground.laz");
    args.push_back("/home/martin/qgis/point-cloud-sandbox/data/trencin-6-buildings.laz");
#elif 0
    std::string cmd = "to_raster_tin";
    std::vector<std::string> args;
    args.push_back("--input=/home/martin/qgis/point-cloud-sandbox/data/trencin-2-ground.laz");
    args.push_back("--output=/tmp/raster_tin.tif");
    args.push_back("--resolution=1");
#elif 1
    std::string cmd = "to_raster";
    std::vector<std::string> args;

    args.push_back("--input=/tmp/first.vpc");
    args.push_back("--output=/tmp/first-dem.tif");
    args.push_back("--resolution=1");
#else
    std::string cmd = "to_raster_tin";
    std::vector<std::string> args;

    // args.push_back("--input=/home/martin/qgis/point-cloud-sandbox/data/merged.copc.laz");
    // args.push_back("--output=/tmp/merged-tin.tif");
    // args.push_back("--resolution=1");
    // args.push_back("--tile-size=250");
    // args.push_back("--tile-origin-x=0");
    // args.push_back("--tile-origin-y=0");
    // args.push_back("--threads=1");

    args.push_back("--input=/tmp/first.vpc");
    args.push_back("--output=/tmp/first-tin.tif");
    args.push_back("--resolution=1");
    args.push_back("--threads=1");
    args.push_back("--tile-size=500");
    // for good alignment of input and output
    args.push_back("--tile-origin-x=377250");
    args.push_back("--tile-origin-y=5441420");
#endif

    std::cout << "command: " << cmd << std::endl;

    if (cmd == "density")
    {
        Density density;
        runAlg(args, density);
    }
    else if (cmd == "boundary")
    {
        Boundary boundary;
        runAlg(args, boundary);
    }
    else if (cmd == "clip")
    {
        Clip clip;
        runAlg(args, clip);
    }
    else if (cmd == "build_vpc")
    {
        buildVpc(args);
    }
    else if (cmd == "merge")
    {
        Merge merge;
        runAlg(args, merge);
    }
    else if (cmd == "to_raster")
    {
        ToRaster toRaster;
        runAlg(args, toRaster);
    }
    else if (cmd == "to_raster_tin")
    {
        ToRasterTin toRasterTin;
        runAlg(args, toRasterTin);
    }
    else
    {
        std::cerr << "unknown command: " << cmd << std::endl;
        return 1;
    }

    return 0;
}
