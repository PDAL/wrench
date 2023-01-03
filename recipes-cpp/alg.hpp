
#pragma once

#include <pdal/PipelineManager.hpp>
#include <pdal/util/ProgramArgs.hpp>

using namespace pdal;

struct ParallelTileInfo;


struct StreamingAlg
{
    // parallel runs (generic)
    int max_threads = -1;
    double tile_size = 1000;

    // all algs should have some input...
    std::string inputFile;

    pdal::ProgramArgs programArgs;

    StreamingAlg() = default;

    // no copying
    StreamingAlg(const StreamingAlg &other) = delete;
    StreamingAlg& operator=(const StreamingAlg &other) = delete;

    bool parseArgs(std::vector<std::string> args);

    // interface
    virtual void addArgs() = 0;
    virtual bool checkArgs() = 0;
    virtual void preparePipelines(std::vector<std::unique_ptr<PipelineManager>>& pipelines, const BOX3D &bounds) = 0;
    virtual void finalize(std::vector<std::unique_ptr<PipelineManager>>& pipelines) {};
};

bool runStreamingAlg(std::vector<std::string> args, StreamingAlg &alg);


//////////////


struct Density : public StreamingAlg
{
    // parameters from the user
    std::string outputFile;
    double resolution = 0;

    // args - initialized in addArgs()
    pdal::Arg* argOutput = nullptr;
    pdal::Arg* argRes = nullptr;

    std::vector<std::string> tileOutputFiles;

    // impl
    virtual void addArgs() override;
    virtual bool checkArgs() override;
    virtual void preparePipelines(std::vector<std::unique_ptr<PipelineManager>>& pipelines, const BOX3D &bounds) override;
    virtual void finalize(std::vector<std::unique_ptr<PipelineManager>>& pipelines) override;

    // new
    std::unique_ptr<PipelineManager> pipeline(ParallelTileInfo *tile = nullptr) const;
};


struct Boundary : public StreamingAlg
{
    // parameters from the user
    std::string outputFile;

    // args - initialized in addArgs()
    pdal::Arg* argOutput = nullptr;

    // impl
    virtual void addArgs() override;
    virtual bool checkArgs() override;
    virtual void preparePipelines(std::vector<std::unique_ptr<PipelineManager>>& pipelines, const BOX3D &bounds) override;
    virtual void finalize(std::vector<std::unique_ptr<PipelineManager>>& pipelines) override;

};


struct Clip : public StreamingAlg
{
    // parameters from the user
    std::string outputFile;
    std::string polygonFile;

    // args - initialized in addArgs()
    pdal::Arg* argOutput = nullptr;
    pdal::Arg* argPolygon = nullptr;

    // impl
    virtual void addArgs() override;
    virtual bool checkArgs() override;
    virtual void preparePipelines(std::vector<std::unique_ptr<PipelineManager>>& pipelines, const BOX3D &bounds) override;
    //virtual void finalize(std::vector<std::unique_ptr<PipelineManager>>& pipelines) override;

};
