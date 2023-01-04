
#pragma once

#include <pdal/PipelineManager.hpp>

using namespace pdal;

struct ParallelTileInfo
{
    int tileX, tileY;
    BOX2D box;

    std::string outputFilename;
};


QuickInfo getQuickInfo(std::string inputFile);

MetadataNode getReaderMetadata(std::string inputFile);

void runPipelineParallel(point_count_t totalPoints, std::vector<std::unique_ptr<PipelineManager>>& pipelines, int max_threads);

std::string box_to_pdal_bounds(const BOX2D &box);


inline bool ends_with(std::string const & value, std::string const & ending)
{
    if (ending.size() > value.size()) return false;
    return std::equal(ending.rbegin(), ending.rend(), value.rbegin());
}
