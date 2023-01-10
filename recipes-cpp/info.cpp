
#include <iostream>
#include <filesystem>
#include <thread>

#include <pdal/PipelineManager.hpp>
#include <pdal/Stage.hpp>
#include <pdal/util/ProgramArgs.hpp>
#include <pdal/pdal_types.hpp>
#include <pdal/Polygon.hpp>

#include <gdal/gdal_utils.h>

#include "utils.hpp"
#include "alg.hpp"
#include "vpc.hpp"

using namespace pdal;

namespace fs = std::filesystem;


void Info::addArgs()
{
}

bool Info::checkArgs()
{
    return true;
}

void Info::preparePipelines(std::vector<std::unique_ptr<PipelineManager>>& pipelines, const BOX3D &bounds, point_count_t &totalPoints)
{
    if (ends_with(inputFile, ".vpc"))
    {
        VirtualPointCloud vpc;
        if (!vpc.read(inputFile))
            return;

        // TODO: crs + other global metadata

        point_count_t total = 0;
        BOX3D box = !vpc.files.empty() ? vpc.files[0].bbox : BOX3D();
        for (const VirtualPointCloud::File& f : vpc.files)
        {
            total += f.count;
            box.grow(f.bbox);
        }

        std::cout << "VPC           " << vpc.files.size() << " files" << std::endl;
        std::cout << "count         " << total << std::endl;
        std::cout << "extent        " << box.minx << " " << box.miny << " " << box.minz << std::endl;
        std::cout << "              " << box.maxx << " " << box.maxy << " " << box.maxz << std::endl;

        // list individual files
        std::cout << std::endl << "Files:" << std::endl;
        for (const VirtualPointCloud::File& f : vpc.files)
        {
            // TODO: maybe add more info?
            std::cout << f.filename << std::endl;
        }

        // TODO: optionally run stats on the whole VPC
    }
    else
    {
        MetadataNode layout;
        MetadataNode meta = getReaderMetadata(inputFile, &layout);

        std::string crs = meta.findChild("srs").findChild("wkt").value(); // TODO: nicer printing (e.g. only CRS name + EPSG ID)
        if (crs.empty())
            crs = "(unknown)";

        std::cout << "LAS           " << meta.findChild("major_version").value() << "." << meta.findChild("minor_version").value() << std::endl;
        std::cout << "point format  " << meta.findChild("dataformat_id").value() << std::endl;
        std::cout << "count         " << meta.findChild("count").value() << std::endl;
        std::cout << "scale         " << meta.findChild("scale_x").value() << " " << meta.findChild("scale_y").value() << " " << meta.findChild("scale_z").value() << std::endl;
        std::cout << "offset        " << meta.findChild("offset_x").value() << " " << meta.findChild("offset_y").value() << " " << meta.findChild("offset_z").value() << std::endl;
        std::cout << "extent        " << meta.findChild("minx").value() << " " << meta.findChild("miny").value() << " " << meta.findChild("minz").value() << std::endl;
        std::cout << "              " << meta.findChild("maxx").value() << " " << meta.findChild("maxy").value() << " " << meta.findChild("maxz").value() << std::endl;
        std::cout << "crs           " << crs << std::endl;
        // TODO: file size in MB ?

        // TODO: possibly show extra metadata: (probably --verbose mode)
        // - creation date + software ID + system ID
        // - filesource ID
        // - VLR info

        std::cout << std::endl << "Attributes:" << std::endl;
        MetadataNodeList dims = layout.children("dimensions");
        for (auto &dim : dims)
        {
            std::string name = dim.findChild("name").value();
            std::string type = dim.findChild("type").value();
            int size = dim.findChild("size").value<int>();
            std::cout << " - " << name << " " << type << " " << size << std::endl;
        }

        // TODO: optionally run filters.stats to get basic stats + counts of classes, returns, ...
    }
}

void Info::finalize(std::vector<std::unique_ptr<PipelineManager>>& pipelines)
{
}
