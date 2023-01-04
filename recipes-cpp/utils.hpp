
#pragma once

#include <pdal/PipelineManager.hpp>

using namespace pdal;

struct ParallelJobInfo
{
    enum ParallelMode {
        Single,      //!< no parallelism
        FileBased,   //!< each input file processed separately
        Spatial,     //!< using tiles - "box" should be used
    } mode;

    // what input point cloud files to read for a job
    std::vector<std::string> inputFilenames;

    // what is the output file name of this job
    std::string outputFilename;

    // bounding box for this job (for input/output)
    BOX2D box;

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

void runPipelineParallel(point_count_t totalPoints, std::vector<std::unique_ptr<PipelineManager>>& pipelines, int max_threads);

std::string box_to_pdal_bounds(const BOX2D &box);


inline bool ends_with(std::string const & value, std::string const & ending)
{
    if (ending.size() > value.size()) return false;
    return std::equal(ending.rbegin(), ending.rend(), value.rbegin());
}
