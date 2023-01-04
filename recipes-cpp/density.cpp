
#include <iostream>
#include <filesystem>
#include <thread>

#include <pdal/PipelineManager.hpp>
#include <pdal/Stage.hpp>
#include <pdal/util/ProgramArgs.hpp>

#include <gdal/gdal_utils.h>

#include "utils.hpp"
#include "alg.hpp"
#include "vpc.hpp"

using namespace pdal;

namespace fs = std::filesystem;

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


std::unique_ptr<PipelineManager> Density::pipeline(ParallelJobInfo *tile) const
{
    std::unique_ptr<PipelineManager> manager( new PipelineManager );

    // TODO: extend to handle multiple readers
    assert(tile->inputFilenames.size() == 1);

    Stage& r = manager->makeReader(tile->inputFilenames[0], "");

    if (tile->mode == ParallelJobInfo::Spatial)
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

    if (tile->box.valid())
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

    pdal::StageCreationOptions opts{ tile->outputFilename, "", &r, writer_opts };
    Stage& w = manager->makeWriter( opts );
    return manager;
}


void Density::preparePipelines(std::vector<std::unique_ptr<PipelineManager>>& pipelines, const BOX3D &bounds)
{
    if (ends_with(inputFile, ".vpc"))
    {
        // using per-file processing

        // TODO: this assumes non-overlapping files - for overlapping we would need extra input files

        // VPC handling
        VirtualPointCloud vpc;
        if (!vpc.read(inputFile))
            return;

        // for /tmp/hello.tif we will use /tmp/hello dir for all results
        fs::path outputParentDir = fs::path(outputFile).parent_path();
        fs::path outputSubdir = outputParentDir / fs::path(outputFile).stem();
        fs::create_directories(outputSubdir);

        int i = 0;
        for ( auto& f : vpc.files )
        {
            ParallelJobInfo tile;
            tile.mode = ParallelJobInfo::FileBased;
            tile.box = f.bbox.to2d();
            tile.inputFilenames.push_back(f.filename);

            // create temp output file names

            // for input file /x/y/z.las that goes to /tmp/hello.vpc,
            // individual output file will be called /tmp/hello/z.las
            fs::path inputBasename = fs::path(f.filename).stem();
            tile.outputFilename = (outputSubdir / inputBasename).string() + ".tif";

            tileOutputFiles.push_back(tile.outputFilename);

            pipelines.push_back(pipeline(&tile));
        }
    }
    else if (ends_with(inputFile, ".copc.laz"))
    {
        // using square tiles for single COPC

        // for /tmp/hello.tif we will use /tmp/hello dir for all results
        fs::path outputParentDir = fs::path(outputFile).parent_path();
        fs::path outputSubdir = outputParentDir / fs::path(outputFile).stem();
        fs::create_directories(outputSubdir);

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
                ParallelJobInfo tile;
                tile.mode = ParallelJobInfo::Spatial;
                tile.box = BOX2D(xmin+tile_size*ix,
                                ymin+tile_size*iy,
                                xmin+tile_size*(ix+1),
                                ymin+tile_size*(iy+1));
                tile.inputFilenames.push_back(inputFile);

                // create temp output file names
                // for tile (x=2,y=3) that goes to /tmp/hello.tif,
                // individual output file will be called /tmp/hello/2_3.tif
                fs::path inputBasename = std::to_string(ix) + "_" + std::to_string(iy);
                tile.outputFilename = (outputSubdir / inputBasename).string() + ".tif";

                tileOutputFiles.push_back(tile.outputFilename);

                pipelines.push_back(pipeline(&tile));
            }
        }
    }
    else
    {
        // single input LAS/LAZ - no parallelism

        ParallelJobInfo tile;
        tile.mode = ParallelJobInfo::Single;
        tile.inputFilenames.push_back(inputFile);
        tile.outputFilename = outputFile;
        pipelines.push_back(pipeline(&tile));
    }

}


void Density::finalize(std::vector<std::unique_ptr<PipelineManager>>& pipelines)
{
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

        // export to COG
        // TODO: make this optional?
        const char* args[] = { "-of", "COG", "-co", "COMPRESS=DEFLATE", NULL };
        GDALTranslateOptions* psOptions = GDALTranslateOptionsNew((char**)args, NULL);
        
        GDALDatasetH dsFinal = GDALTranslate(outputFile.c_str(), ds, psOptions, nullptr);
        assert(dsFinal);
        GDALTranslateOptionsFree(psOptions);
        GDALClose(ds);
        GDALClose(dsFinal);

        // TODO: remove VRT + partial tifs after gdal_translate?
     }

}
