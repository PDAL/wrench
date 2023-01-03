
#include "alg.hpp"

#include "utils.hpp"

#include <thread>

#include <pdal/QuickInfo.hpp>

using namespace pdal;


bool runStreamingAlg(std::vector<std::string> args, StreamingAlg &alg)
{

    if ( !alg.parseArgs(args) )
        return false;

    QuickInfo qi = getQuickInfo(alg.inputFile);
    point_count_t totalPoints = qi.m_pointCount;

    std::vector<std::unique_ptr<PipelineManager>> pipelines;

    alg.preparePipelines(pipelines, qi.m_bounds);

    if (pipelines.empty())
        return false;

    runPipelineParallel(totalPoints, pipelines, alg.max_threads);

    alg.finalize(pipelines);

    return true;
}


bool StreamingAlg::parseArgs(std::vector<std::string> args)
{ 
    pdal::Arg& argInput = programArgs.add("input,i", "Input point cloud file", inputFile);
    addArgs();  // impl in derived

    // parallel run support (generic)
    pdal::Arg& argThreads = programArgs.add("threads", "Max number of concurrent threads for parallel runs", max_threads);
    pdal::Arg& argTileSize = programArgs.add("tile-size", "Size of a tile for parallel runs", tile_size);

    try
    {
        programArgs.parseSimple(args);
    }
    catch(pdal::arg_error err)
    {
        // TODO
        std::cerr << "uh oh" << std::endl;
        return false;
    }

    // TODO: ProgramArgs does not support required options
    if (!argInput.set())
    {
        std::cerr << "missing input" << std::endl;
        return false;
    }

    if (!checkArgs())  // impl in derived class
        return false;

    if (!args.empty())
    {
        std::cout << "unexpected args!" << std::endl;
        for ( auto & a : args )
            std::cout << " - " << a << std::endl;
        return false;
    }

    // TODO: not sure why ProgramArgs cleans the default value
    if (!argTileSize.set())
    {
        tile_size = 1000;
    }

    if (!argThreads.set())  // in such case our value is reset to zero
    {
        // use number of cores if not specified by the user
        max_threads = std::thread::hardware_concurrency();
        if (max_threads == 0)
        {
            // in case the value can't be detected, use something reasonable...
            max_threads = 4;
        }
    }

    return true;
}
