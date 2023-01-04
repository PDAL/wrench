
#include <iostream>
#include <filesystem>
namespace fs = std::filesystem;

#include "vpc.hpp"
#include "utils.hpp"

#include <pdal/util/ProgramArgs.hpp>

#include "nlohmann/json.hpp"


using json = nlohmann::json;

using namespace pdal;


void VirtualPointCloud::clear()
{
    files.clear();
}

void VirtualPointCloud::dump()
{
    std::cout << "----- VPC" << std::endl;
    for (auto& f : files)
    {
        std::cout << " - " << f.filename << "  " << f.count << "  "
                    << f.bbox.minx << " " << f.bbox.miny << " " << f.bbox.maxx << " " << f.bbox.maxy << std::endl;
    }
}

bool VirtualPointCloud::read(std::string filename)
{
    clear();

    std::ifstream inputJson(filename);
    if (!inputJson.good())
    {
        std::cout << "failed to read file " << filename << std::endl;
        return false;
    }

    json data;
    try
    {
        data = json::parse(inputJson);
    }
    catch (std::exception &e)
    {
        std::cout << "json parsing error: " << e.what() << std::endl;
        return false;
    }
    if (!data.contains("vpc"))
    {
        std::cout << "not a VPC file " << filename << std::endl;
        return false;
    }
    if (data["vpc"] != "1.0.0")
    {
        std::cout << "unsupported VPC file version " << data["vpc"] << std::endl;
        return false;
    }

    for (auto& f : data["files"])
    {
        File vpcf;
        vpcf.filename = f["filename"];
        vpcf.count = f["count"];
        json jb = f["bbox"];
        vpcf.bbox = BOX3D(
            jb[0].get<double>(), jb[1].get<double>(), jb[2].get<double>(),
            jb[3].get<double>(),jb[4].get<double>(), jb[5].get<double>() );
        files.push_back(vpcf);
    }

    return true;
}

bool VirtualPointCloud::write(std::string filename)
{
    std::ofstream outputJson(filename);
    if (!outputJson.good())
    {
        std::cout << "failed to create file" << std::endl;
        return false;
    }

    std::vector<nlohmann::ordered_json> jFiles;
    for ( const File &f : files )
    {
        jFiles.push_back({
            { "filename", f.filename },
            { "count", f.count },
            { "bbox", { f.bbox.minx, f.bbox.miny, f.bbox.minz, f.bbox.maxx, f.bbox.maxy, f.bbox.maxz } },
        });
    }

    nlohmann::ordered_json jMeta = {};  // TODO

    nlohmann::ordered_json j = { { "vpc", "1.0.0" }, { "metadata", jMeta }, { "files", jFiles } };

    outputJson << std::setw(2) << j << std::endl;
    outputJson.close();
    return true;
}


void buildVpc(std::vector<std::string> args)
{
    std::string outputFile;
    std::vector<std::string> inputFiles;

    ProgramArgs programArgs;
    programArgs.add("output,o", "Output virtual point cloud file", outputFile);
    programArgs.add("files,f", "input files", inputFiles).setPositional();

    try
    {
        programArgs.parseSimple(args);
    }
    catch(pdal::arg_error err)
    {
        // TODO
        std::cerr << "uh oh" << std::endl;
        return;
    }

    std::cout << "input " << inputFiles.size() << std::endl;
    std::cout << "output " << outputFile << std::endl;

    VirtualPointCloud vpc;

    for (const std::string &inputFile : inputFiles)
    {
        MetadataNode n = getReaderMetadata(inputFile);
        point_count_t cnt = n.findChild("count").value<point_count_t>();
        BOX3D bbox(
                n.findChild("minx").value<double>(),
                n.findChild("miny").value<double>(),
                n.findChild("minz").value<double>(),
                n.findChild("maxx").value<double>(),
                n.findChild("maxy").value<double>(),
                n.findChild("maxz").value<double>()
        );

        VirtualPointCloud::File f;
        f.filename = inputFile;
        f.count = cnt;
        f.bbox = bbox;
        vpc.files.push_back(f);
    }

    vpc.dump();

    vpc.write(outputFile);

    vpc.read(outputFile);

    // TODO: for now hoping that all files have the same file type + CRS + point format + scaling
    // "dataformat_id"
    // "spatialreference"
    // "scale_x" ...


    //Utils::toJSON(n, std::cout);

}
