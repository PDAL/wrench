
#pragma once

#include <vector>
#include <string>

#include <pdal/pdal_types.hpp>
#include <pdal/util/Bounds.hpp>

using namespace pdal;


void buildVpc(std::vector<std::string> args);


struct VirtualPointCloud
{
    struct File
    {
        std::string filename;
        point_count_t count;
        BOX3D bbox;
    };

    std::vector<File> files;

    void clear();
    void dump();
    bool read(std::string filename);
    bool write(std::string filename);

    point_count_t totalPoints() const;
    BOX3D box3d() const;

    //! returns files that have bounding box overlapping the given bounding box
    std::vector<File> overlappingBox2D(const BOX2D &box);
};
