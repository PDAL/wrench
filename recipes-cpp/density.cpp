
#include <iostream>
#include <thread>

#include <pdal/PipelineManager.hpp>
#include <pdal/Stage.hpp>
#include <pdal/util/ProgramArgs.hpp>

#include <gdal/gdal_utils.h>

#include "utils.hpp"
#include "alg.hpp"

using namespace pdal;


void Density::addArgs()
{
    argOutput = &programArgs.add("output,o", "Output raster file", outputFile);
    argRes = &programArgs.add("resolution,r", "Resolution of the density grid", resolution);
}

bool Density::checkArgs()
{
    if (!argOutput->set())
    {
        std::cerr << "missing output" << std::endl;
        return false;
    }
    if (!argRes->set())
    {
        std::cerr << "missing resolution" << std::endl;
        return false;
    }

    return true;
}


std::unique_ptr<PipelineManager> Density::pipeline(ParallelTileInfo *tile) const
{
    std::unique_ptr<PipelineManager> manager( new PipelineManager );
    Stage& r = manager->makeReader(inputFile, "");

    if (tile)
    {
        // for parallel runs
        assert(r.getName() == "readers.copc");

        pdal::Options copc_opts;
        copc_opts.add(pdal::Option("threads", 1));
        copc_opts.add(pdal::Option("bounds", box_to_pdal_bounds(tile->box)));
        r.addOptions(copc_opts);
    }

    pdal::Options writer_opts;
    writer_opts.add(pdal::Option("binmode", true));
    writer_opts.add(pdal::Option("output_type", "count"));
    writer_opts.add(pdal::Option("resolution", resolution));

    writer_opts.add(pdal::Option("data_type", "int16"));  // 16k points in a cell should be enough? :)
    writer_opts.add(pdal::Option("gdalopts", "TILED=YES"));
    writer_opts.add(pdal::Option("gdalopts", "COMPRESS=DEFLATE"));

    if (tile)
    {
        // TODO: for tiles that are smaller than full box - only use intersection
        // to avoid empty areas in resulting rasters

        BOX2D box2 = tile->box;
        // fix tile size - TODO: not sure if this is the right thing to do
        box2.maxx -= resolution;
        box2.maxy -= resolution;
        writer_opts.add(pdal::Option("bounds", box_to_pdal_bounds(box2)));
    }

    // TODO: "writers.gdal: Requested driver 'COG' does not support file creation.""
    //   writer_opts.add(pdal::Option("gdaldriver", "COG"));

    std::string output = tile ? tile->outputFilename : outputFile;

    pdal::StageCreationOptions opts{ output, "", &r, writer_opts };
    Stage& w = manager->makeWriter( opts );
    return manager;
}


void Density::preparePipelines(std::vector<std::unique_ptr<PipelineManager>>& pipelines, const BOX3D &bounds)
{
    bool parallel_run = ends_with(inputFile, ".copc.laz");

    if (parallel_run)
    {
        // TODO: optionally adjust xmin/ymin to have nice numbers?

        double xmin = bounds.minx, ymin = bounds.miny;
        double xmax = bounds.maxx, ymax = bounds.maxy;

        int n_tiles_x = int(ceil((xmax-xmin)/tile_size));
        int n_tiles_y = int(ceil((ymax-ymin)/tile_size));
        std::cout << "tiles " << n_tiles_x << " " << n_tiles_y << std::endl;
        std::vector<BOX2D> tile_bounds;

        // TODO: fix tile bounds calculation - created 501 pixel tile instead of 500
        // (probably writers.gdal needs precise bounds too)

        for (int iy = 0; iy < n_tiles_y; ++iy)
        {
            for (int ix = 0; ix < n_tiles_x; ++ix)
            {
                ParallelTileInfo tile;
                tile.tileX = ix;
                tile.tileY = iy;
                tile.box = BOX2D(xmin+tile_size*ix,
                                ymin+tile_size*iy,
                                xmin+tile_size*(ix+1),
                                ymin+tile_size*(iy+1));

                // create temp output file names
                std::string output = outputFile;
                assert(ends_with(output, ".tif"));
                output.erase(output.rfind(".tif"), 4);
                output += "-" + std::to_string(tile.tileX) + "-" + std::to_string(tile.tileY) + ".tif";
                tile.outputFilename = output;

                tileOutputFiles.push_back(output);

                pipelines.push_back(pipeline(&tile));
            }
        }
    }
    else
    {
        pipelines.push_back(pipeline());
    }

}


void Density::finalize(std::vector<std::unique_ptr<PipelineManager>>& pipelines)
{
    (pipelines);

    if (pipelines.size() > 1)
    {
        // build a VRT so that all tiles can be handled as a single data source

        std::string output = outputFile;
        assert(ends_with(output, ".tif"));
        output.erase(output.rfind(".tif"), 4);
        output += ".vrt";

        std::vector<const char*> dsNames;
        for ( const std::string &t : tileOutputFiles )
        {
            dsNames.push_back(t.c_str());
        }

        // https://gdal.org/api/gdal_utils.html
        GDALDatasetH ds = GDALBuildVRT(output.c_str(), (int)dsNames.size(), nullptr, dsNames.data(), nullptr, nullptr);
        assert(ds);
        GDALClose(ds);

        // TODO: optionally export to COG (?)
    }

}
