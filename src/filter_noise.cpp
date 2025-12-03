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

void FilterNoise::addArgs()
{
    argOutput = &programArgs.add("output,o", "Output point cloud file", outputFile);
    argOutputFormat = &programArgs.add("output-format", "Output format (las/laz/copc)", outputFormat);
    
    argAlgorithm = &programArgs.add("algorithm", "Noise filtering algorithm to use: statistical or radius.", algorithm, "statistical");
    
    // radius args
    argRadiusMinK = &programArgs.add("radius-min-k", "Minimum number of neighbors in radius (radius algorithm only).", radiusMinK, 2.0);
    argRadiusRadius = &programArgs.add("radius-radius", "Radius (radius method only).", radiusRadius, 1.0);

    // statistical args
    argStatisticalMeanK = &programArgs.add("statistical-mean-k", "Mean number of neighbors (statistical method only)", statisticalMeanK, 8);
    argStatisticalMultiplier = &programArgs.add("statistical-multiplier", "Standard deviation threshold (statistical method only).", statisticalMultiplier, 2.0);
}

bool FilterNoise::checkArgs()
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
        if (!(algorithm == "statistical" || algorithm == "radius"))
        {
            std::cerr << "unknown algorithm: " << algorithm << std::endl;
            return false;
        }
    }

    if (algorithm == "radius" && (argStatisticalMeanK->set() || argStatisticalMultiplier->set()))
    {
        std::cerr << "statistical- arguments are not supported with radius algorithm" << std::endl;
        return false;
    }

    if (algorithm == "statistical" && (argRadiusMinK->set() || argRadiusRadius->set()))
    {
        std::cerr << "radius- arguments are not supported with statistical algorithm" << std::endl;
        return false;
    }

    return true;
}


static std::unique_ptr<PipelineManager> pipeline(ParallelJobInfo *tile, pdal::Options &noiseFilterOptions)
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

    last = &manager->makeFilter( "filters.outlier", *last, noiseFilterOptions);

    pdal::Options writer_opts;
    // let's use the same offset & scale & header & vlrs as the input
    writer_opts.add(pdal::Option("forward", "all"));
       
    (void)manager->makeWriter( tile->outputFilename, "", *last, writer_opts);
        
    return manager;
}

void FilterNoise::preparePipelines(std::vector<std::unique_ptr<PipelineManager>>& pipelines)
{   
    pdal::Options noiseFilterOptions;
    noiseFilterOptions.add(pdal::Option("method", algorithm));

    if (algorithm == "radius")
    {
        noiseFilterOptions.add(pdal::Option("min_k", radiusMinK));
        noiseFilterOptions.add(pdal::Option("radius", radiusRadius));
    }
    else if (algorithm == "statistical")
    {
        noiseFilterOptions.add(pdal::Option("mean_k", statisticalMeanK));
        noiseFilterOptions.add(pdal::Option("multiplier", statisticalMultiplier));
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

            pipelines.push_back(pipeline(&tile, noiseFilterOptions));
        }
    }
    else
    {
        ParallelJobInfo tile(ParallelJobInfo::Single, BOX2D(), filterExpression, filterBounds);
        tile.inputFilenames.push_back(inputFile);
        tile.outputFilename = outputFile;

        pipelines.push_back(pipeline(&tile, noiseFilterOptions));
    }
}

void FilterNoise::finalize(std::vector<std::unique_ptr<PipelineManager>>&)
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