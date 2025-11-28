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


void HeightAboveGround::addArgs()
{
    argOutput = &programArgs.add("output,o", "Output point cloud file", outputFile);
    argOutputFormat = &programArgs.add("output-format", "Output format (las/laz/copc)", outputFormat);

    argCount = &programArgs.add("count", "The number of ground neighbors to consider when determining the height above ground for a non-ground point", count);
    argMaxDistance = &programArgs.add("max-distance", "Use only ground points within max_distance of non-ground point when performing neighbor interpolation.", maxDistance);
    argReplaceZWithHeightAboveGround = &programArgs.add("replace-z", "Replace Z dimension with height above ground (true/false).", replaceZWithHeightAboveGround);
}

bool HeightAboveGround::checkArgs()
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

    if (!argCount->set())
    {
        count = 1; // default
    }

    if (!argMaxDistance->set())
    {
        maxDistance = 0; // default
    }

    if (!argReplaceZWithHeightAboveGround->set())
    {
        replaceZWithHeightAboveGround = false; // default
    }
    
    return true;
}


static std::unique_ptr<PipelineManager> pipeline(ParallelJobInfo *tile, int count, double maxDistance, bool replaceZWithHeightAboveGround)
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

    Options hag_nn_opts;

    if (count > 1)
    {
        hag_nn_opts.add(pdal::Option("count", count));
    }

    if (maxDistance > 0)
    {
        hag_nn_opts.add(pdal::Option("max_distance", maxDistance));
    }

    last = &manager->makeFilter( "filters.hag_nn", *last, hag_nn_opts);
    
    pdal::Options writer_opts;
    // let's use the same offset & scale & header & vlrs as the input
    writer_opts.add(pdal::Option("forward", "all"));
    
    if (replaceZWithHeightAboveGround)
    {
        pdal::Options ferry_opts;
        ferry_opts.add(pdal::Option("dimensions", "HeightAboveGround=>Z"));

        last = &manager->makeFilter( "filters.ferry", *last, ferry_opts);
    }
    else
    {
        writer_opts.add(pdal::Option("extra_dims","HeightAboveGround=float32"));
    }
   
    (void)manager->makeWriter( tile->outputFilename, "", *last, writer_opts);
        
    return manager;
}


void HeightAboveGround::preparePipelines(std::vector<std::unique_ptr<PipelineManager>>& pipelines)
{   
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

            pipelines.push_back(pipeline(&tile, count, maxDistance, replaceZWithHeightAboveGround));
        }
    }
    else
    {
        ParallelJobInfo tile(ParallelJobInfo::Single, BOX2D(), filterExpression, filterBounds);
        tile.inputFilenames.push_back(inputFile);
        tile.outputFilename = outputFile;
        pipelines.push_back(pipeline(&tile, count, maxDistance, replaceZWithHeightAboveGround));
    }
}

void HeightAboveGround::finalize(std::vector<std::unique_ptr<PipelineManager>>&)
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
