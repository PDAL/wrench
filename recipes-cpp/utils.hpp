
#pragma once

#include <pdal/PipelineManager.hpp>

using namespace pdal;

// tiling scheme containing tileCountX x tileCountY square tiles of tileSize x tileSize,
// with lower-left corner of the tiling being at [tileStartX,tileStartY]
struct Tiling
{
    int tileCountX;
    int tileCountY;
    double tileStartX;
    double tileStartY;
    double tileSize;

    BOX2D fullBox() const
    {
        return BOX2D(tileStartX,
                     tileStartY,
                     tileStartX + tileSize * tileCountX,
                     tileStartY + tileSize * tileCountY);
    }

    BOX2D boxAt(int ix, int iy) const
    {
        return BOX2D(tileStartX + tileSize*ix,
                     tileStartY + tileSize*iy,
                     tileStartX + tileSize*(ix+1),
                     tileStartY + tileSize*(iy+1));
    }
};

// specification that square tiles of tileSize x tileSize should be aligned:
// so that all corners have coordinates [originX + N*tileSize, originY + M*tileSize]
// where N,M are some integer values
struct TileAlignment
{
    double originX;
    double originY;
    double tileSize;

    // returns tiling that fully covers given bounding box, using this tile alignment
    Tiling coverBounds(const BOX2D &box) const
    {
        Tiling t;
        t.tileSize = tileSize;
        double offsetX = fmod(originX, tileSize);
        double offsetY = fmod(originY, tileSize);
        t.tileStartX = floor((box.minx - offsetX)/tileSize)*tileSize + offsetX;
        t.tileStartY = floor((box.miny - offsetY)/tileSize)*tileSize + offsetY;
        t.tileCountX = ceil((box.maxx - t.tileStartX)/tileSize);
        t.tileCountY = ceil((box.maxy - t.tileStartY)/tileSize);
        return t;
    }
};

struct ParallelJobInfo
{
    enum ParallelMode {
        Single,      //!< no parallelism
        FileBased,   //!< each input file processed separately
        Spatial,     //!< using tiles - "box" should be used
    } mode;

    ParallelJobInfo(ParallelMode m = Single): mode(m) {}
    ParallelJobInfo(ParallelMode m, const BOX2D &b, const std::string fe): mode(m), box(b), filterExpression(fe) {}

    // what input point cloud files to read for a job
    std::vector<std::string> inputFilenames;

    // what is the output file name of this job
    std::string outputFilename;

    // bounding box for this job (for input/output)
    BOX2D box;

    // bounding box for the job with extra collar that some algs may use
    // in case they need access to neighboring points at the edges of tiles
    BOX2D boxWithCollar;

    // PDAL filter expression to apply on all pipelines
    std::string filterExpression;

    // modes of operation:
    // A. multi input without box  (LAS/LAZ)    -- per file strategy
    //    - all input files are processed, no filtering on bounding box
    // B. multi input with box     (anything)   -- tile strategy
    //    - all input files are processed, but with filtering applied
    //    - COPC: filtering inside readers.copc with "bounds" argument
    //    - LAS/LAZ: filter either using CropFilter after reader -or- "where" 

    // streaming algs:
    // - multi-las: if not overlapping:  mode A
    //              if overlapping:      mode A - with a warning it is inefficient?
    // - multi-copc:  mode B
    // - single-copc: mode B or just single pipeline
};


QuickInfo getQuickInfo(std::string inputFile);

MetadataNode getReaderMetadata(std::string inputFile);

void runPipelineParallel(point_count_t totalPoints, bool isStreaming, std::vector<std::unique_ptr<PipelineManager>>& pipelines, int max_threads);

std::string box_to_pdal_bounds(const BOX2D &box);


inline bool ends_with(std::string const & value, std::string const & ending)
{
    if (ending.size() > value.size()) return false;
    return std::equal(ending.rbegin(), ending.rend(), value.rbegin());
}


inline std::string join_strings(const std::vector<std::string>& list, char delimiter)
{
    std::string output;
    for (std::vector<std::string>::const_iterator it = list.begin(); it != list.end(); ++it)
    {
        output += *it;
        if (it != list.end() - 1)
            output += delimiter;
    }
    return output;
}


bool rasterTilesToCog(const std::vector<std::string> &inputFiles, const std::string &outputFile);
