
/*
TODO:
- add writing of VPC + reading of VPC by algs
- boundary: parallel run
- clip: parallel run  ... store pts as LAS/LAZ tiles, then A. make vpc-LAS or vpc-COPC or single-COPC ?
*/

#include <iostream>
#include <vector>

#include "alg.hpp"


int main(int argc, char* argv[])
{
#if 0
    if (argc < 2)
    {
        std::cerr << "need to specify command:" << std::endl;
        std::cerr << " - boundary" << std::endl;
        std::cerr << " - clip" << std::endl;
        std::cerr << " - density" << std::endl;
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
    args.push_back("--threads=4");
#elif 1
    std::string cmd = "boundary";
    std::vector<std::string> args;

    args.push_back("--input=/home/martin/qgis/point-cloud-sandbox/data/24-fixed.las");
    //args.push_back("--input=/home/martin/qgis/point-cloud-sandbox/data/merged.copc.laz"); // TODO: empty boundary???
    args.push_back("--output=/tmp/boundary.gpkg");
    //args.push_back("--resolution=1");
    //args.push_back("--tile-size=250");
    //args.push_back("--threads=4");
#else
    std::string cmd = "clip";
    std::vector<std::string> args;

    args.push_back("--input=/home/martin/qgis/point-cloud-sandbox/data/24-fixed.las");
    args.push_back("--polygon=/home/martin/qgis/point-cloud-sandbox/data/24-polygon.gpkg");
    args.push_back("--output=/tmp/clipped.las");
#endif

    std::cout << "command: " << cmd << std::endl;

    if (cmd == "density")
    {
        Density density;
        runStreamingAlg(args, density);
    }
    else if (cmd == "boundary")
    {
        Boundary boundary;
        runStreamingAlg(args, boundary);
    }
    else if (cmd == "clip")
    {
        Clip clip;
        runStreamingAlg(args, clip);
    }
    else
    {
        std::cerr << "unknown command: " << cmd << std::endl;
        return 1;
    }

    return 0;
}
