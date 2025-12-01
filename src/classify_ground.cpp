/*****************************************************************************
 *   Copyright (c) 2025, Lutra Consulting Ltd. and Hobu, Inc.                *
 *                                                                           *
 *   All rights reserved.                                                    *
 *                                                                           *
 *   This program is free software; you can redistribute it and/or modify    *
 *   it under the terms of the GNU General Public License as published by    *
 *   the Free Software Foundation; either version 3 of the License, or       *
 *   (at your option) any later version.                                     *
 *                                                                           *
 ****************************************************************************/

#include <iostream>
#include <filesystem>
#include <thread>

#include <pdal/PipelineManager.hpp>
#include <pdal/Stage.hpp>
#include <pdal/util/ProgramArgs.hpp>
#include <pdal/pdal_types.hpp>
#include <pdal/Polygon.hpp>
#include <pdal/PipelineWriter.hpp>

#include <gdal_utils.h>

#include "utils.hpp"
#include "alg.hpp"
#include "vpc.hpp"

using namespace pdal;

namespace fs = std::filesystem;


void ClassifyGround::addArgs()
{
    argOutput = &programArgs.add("output,o", "Output point cloud file", outputFile);
    argOutputFormat = &programArgs.add("output-format", "Output format (las/laz/copc)", outputFormat);
    
    argAlgorithm = &programArgs.add("algorithm", "Ground Classification algorithm to use: smrf (Simple Morphological Filter) or pmf (Progressive Morphological Filter).", algorithm, "smrf");
    argCellSize = &programArgs.add("cell-size", "Cell size.", cellSize, 1.0);

    // PMF args
    argPmfExponential = &programArgs.add("pmf-exponential", "Use exponential growth for PMF window sizes?.", pmfExponential, true);
    argPmfInitialDistance = &programArgs.add("pmf-initial-distance", "Initial distance for PMF.", pmfInitialDistance, 0.15);
    argPmfMaxDistance = &programArgs.add("pmf-max-distance", "Maximum distance for PMF.", pmfMaxDistance, 2.5);
    argPmfMaxWindowSize = &programArgs.add("pmf-max-window-size", "Maximum window size for PMF.", pmfMaxWindowSize, 33.0);
    argPmfSlope = &programArgs.add("pmf-slope", "Slope for PMF.", pmfSlope, 1.0);

    // SMRF args
    argSmrfScalar = &programArgs.add("smrf-scalar", "Scalar for SMRF.", smrfScalar, 1.25);
    argSmrfSlope = &programArgs.add("smrf-slope", "Slope for SMRF.", smrfSlope, 0.15);
    argSmrfThreshold = &programArgs.add("smrf-threshold", "Threshold for SMRF.", smrfThreshold, 0.5);
    argSmrfWindowSize = &programArgs.add("smrf-window-size", "Window size for SMRF.", smrfWindowSize, 18.0);
}

bool ClassifyGround::checkArgs()
{
    if (!argOutput->set())
    {
        std::cerr << "missing output" << std::endl;
        return false;
    }

    if (argOutputFormat->set())
    {
        if (outputFormat != "las" && outputFormat != "laz" && outputFormat != "copc")
        {
            std::cerr << "unknown output format: " << outputFormat << std::endl;
            return false;
        }
    }
    else
        outputFormat = "las";  // uncompressed by default

    if (!argAlgorithm->set())
    {
        std::cerr << "missing algorithm" << std::endl;
        return false;
    }
    else
    {
        if (!(algorithm == "smrf" || algorithm == "pmf"))
        {
            std::cerr << "unknown algorithm: " << algorithm << std::endl;
            return false;
        }
    }


    if (algorithm == "pmf" && (argSmrfScalar->set() || argSmrfSlope->set() || argSmrfThreshold->set() || argSmrfWindowSize->set()))
    {
        std::cout << "smrf-* arguments are not supported with pmf algorithm" << std::endl;
    }

    if (algorithm == "smrf" && (argPmfExponential->set() || argPmfInitialDistance->set() || argPmfMaxDistance->set() || argPmfMaxWindowSize->set() || argPmfSlope->set()))
    {
        std::cout << "pmf-* arguments are not supported with smrf algorithm" << std::endl;
    }

    return true;
}

static std::unique_ptr<PipelineManager> pipeline(ParallelJobInfo *tile, std::string algorithm, pdal::Options &filterOptions)
{
    std::unique_ptr<PipelineManager> manager( new PipelineManager );

    Options reader_opts;

    Stage& r = manager->makeReader( tile->inputFilenames[0], "", reader_opts);

    Stage *last = &r;

    // filtering
    if (!tile->filterBounds.empty())
    {
        Options filter_opts;
        filter_opts.add(pdal::Option("bounds", tile->filterBounds));

        if (readerSupportsBounds(r))
        {
            // Reader of the format can do the filtering - use that whenever possible!
            r.addOptions(filter_opts);
        }
        else
        {
            // Reader can't do the filtering - do it with a filter
            last = &manager->makeFilter( "filters.crop", *last, filter_opts);
        }
    }

    if (!tile->filterExpression.empty())
    {
        Options filter_opts;
        filter_opts.add(pdal::Option("expression", tile->filterExpression));
        last = &manager->makeFilter( "filters.expression", *last, filter_opts);
    }

    if (algorithm == "pmf")
    {
        last = &manager->makeFilter( "filters.pmf", *last, filterOptions);
    }
    else if (algorithm == "smrf")
    {
        last = &manager->makeFilter( "filters.smrf", *last, filterOptions);
    }

    pdal::Options writer_opts;
    // let's use the same offset & scale & header & vlrs as the input
    writer_opts.add(pdal::Option("forward", "all"));
       
    (void)manager->makeWriter( tile->outputFilename, "", *last, writer_opts);
        
    return manager;
}


void ClassifyGround::preparePipelines(std::vector<std::unique_ptr<PipelineManager>>& pipelines)
{   
    pdal::Options filterOptions;
    if (algorithm == "pmf")
    {
        filterOptions.add(pdal::Option("cell_size", cellSize));
        filterOptions.add(pdal::Option("exponential", pmfExponential));
        filterOptions.add(pdal::Option("initial_distance", pmfInitialDistance));
        filterOptions.add(pdal::Option("max_window_size", pmfMaxWindowSize));   
        filterOptions.add(pdal::Option("max_distance", pmfMaxDistance));   
        filterOptions.add(pdal::Option("slope", pmfSlope));
    }
    else if (algorithm == "smrf")
    {
        filterOptions.add(pdal::Option("cell", cellSize));
        filterOptions.add(pdal::Option("scalar", smrfScalar));
        filterOptions.add(pdal::Option("slope", smrfSlope));
        filterOptions.add(pdal::Option("threshold", smrfThreshold));
        filterOptions.add(pdal::Option("window", smrfWindowSize));
    }

    if (ends_with(inputFile, ".vpc"))
    {
        // for /tmp/hello.vpc we will use /tmp/hello dir for all results
        fs::path outputParentDir = fs::path(outputFile).parent_path();
        fs::path outputSubdir = outputParentDir / fs::path(outputFile).stem();
        fs::create_directories(outputSubdir);

        // VPC handling
        VirtualPointCloud vpc;
        if (!vpc.read(inputFile))
            return;

        for (const VirtualPointCloud::File& f : vpc.files)
        {
            ParallelJobInfo tile(ParallelJobInfo::FileBased, BOX2D(), filterExpression, filterBounds);
            tile.inputFilenames.push_back(f.filename);

            // for input file /x/y/z.las that goes to /tmp/hello.vpc,
            // individual output file will be called /tmp/hello/z.las
            fs::path inputBasename = fileStem(f.filename);

            if (!ends_with(outputFile, ".vpc"))
                tile.outputFilename = (outputSubdir / inputBasename).string() + ".las";
            else
                tile.outputFilename = (outputSubdir / inputBasename).string() + "." + outputFormat;

            tileOutputFiles.push_back(tile.outputFilename);

            pipelines.push_back(pipeline(&tile, algorithm, filterOptions));
        }
    }
    else
    {
        ParallelJobInfo tile(ParallelJobInfo::Single, BOX2D(), filterExpression, filterBounds);
        tile.inputFilenames.push_back(inputFile);
        tile.outputFilename = outputFile;

        pipelines.push_back(pipeline(&tile, algorithm, filterOptions));
    }
}

void ClassifyGround::finalize(std::vector<std::unique_ptr<PipelineManager>>&)
{
    if (tileOutputFiles.empty())
        return;

    std::vector<std::string> args;
    args.push_back("--output=" + outputFile);
    for (std::string f : tileOutputFiles)
        args.push_back(f);

    if (ends_with(outputFile, ".vpc"))
    {
        // now build a new output VPC
        buildVpc(args);
    }
    else
    {
        // merge all the output files into a single file        
        Merge merge;
        // for copc set isStreaming to false
        if (ends_with(outputFile, ".copc.laz"))
        {
            merge.isStreaming = false;
        }

        runAlg(args, merge);

        // remove files as they are not needed anymore - they are merged
        removeFiles(tileOutputFiles, true);
    }
}