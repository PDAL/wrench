/*****************************************************************************
 *   Copyright (c) 2020, Hobu, Inc. (info@hobu.co)                           *
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

#include <unordered_set>

#include <pdal/pdal_features.hpp>
#include <pdal/SpatialReference.hpp>
#include <pdal/util/Algorithm.hpp>
#include <pdal/util/FileUtils.hpp>
#include <pdal/StageFactory.hpp>

#include "CommonX.hpp"
#include "GridX.hpp"
#include "FileDimInfoX.hpp"
#include "EpfTypesX.hpp"
#include "WriterX.hpp"
#include "FileProcessorX.hpp"

using namespace std;

const std::string MetadataFilename {"info2.txt"};

using StringList = std::vector<std::string>;

struct OptionsX
{
    std::string outputName;
    bool singleFile;
    StringList inputFiles;
    std::string tempDir;
    bool preserveTempDir;
    bool doCube;
    size_t fileLimit;
    int level;
    int progressFd;
    bool progressDebug;
    StringList dimNames;
    bool stats;
    std::string a_srs;
    bool metadata;
};

struct BaseInfo
{
public:
    BaseInfo()
    {};

    OptionsX opts;
    pdal::BOX3D bounds;
    pdal::BOX3D trueBounds;
    size_t pointSize;
    std::string outputFile;
    untwine::DimInfoListX dimInfo;
    pdal::SpatialReference srs;
    int pointFormatId;

    using d3 = std::array<double, 3>;
    d3 scale { -1.0, -1.0, -1.0 };
    d3 offset {};
};

#include <filesystem>


// TODO: mac needs special variant
std::vector<std::string> directoryList(const std::string& dir)
{
    namespace fs = std::filesystem;

    std::vector<std::string> files;

    try
    {
        fs::directory_iterator it(untwine::toNative(dir));
        fs::directory_iterator end;
        while (it != end)
        {
            files.push_back(untwine::fromNative(it->path()));
            it++;
        }
    }
    catch (fs::filesystem_error&)
    {
        files.clear();
    }
    return files;
}

using namespace untwine::epf;
using namespace pdal;



static PointCount createFileInfo(const StringList& input, StringList dimNames,
    std::vector<FileInfoX>& fileInfos, BaseInfo &m_b, GridX &m_grid, FileInfoX &m_srsFileInfo)
{
    using namespace pdal;

    std::vector<FileInfoX> tempFileInfos;
    std::vector<std::string> filenames;
    PointCount totalPoints = 0;

    // If there are some dim names specified, make sure they contain X, Y and Z and that
    // they're all uppercase.
    if (!dimNames.empty())
    {
        for (std::string& d : dimNames)
            d = Utils::toupper(d);
        for (const std::string xyz : { "X", "Y", "Z" })
            if (!Utils::contains(dimNames, xyz))
                dimNames.push_back(xyz);
    }

    // If any of the specified input files is a directory, get the names of the files
    // in the directory and add them.
    for (const std::string& filename : input)
    {
        if (FileUtils::isDirectory(filename))
        {
            std::vector<std::string> dirfiles = directoryList(filename);
            filenames.insert(filenames.end(), dirfiles.begin(), dirfiles.end());
        }
        else
            filenames.push_back(filename);
    }

    std::vector<double> xOffsets;
    std::vector<double> yOffsets;
    std::vector<double> zOffsets;

    // Determine a driver for each file and get a preview of the file.  If we couldn't
    // Create a FileInfo object containing the file bounds, dimensions, filename and
    // associated driver.  Expand our grid by the bounds and file point count.
    for (std::string& filename : filenames)
    {
        StageFactory factory;
        std::string driver = factory.inferReaderDriver(filename);
        if (driver.empty())
            throw FatalErrorX("Can't infer reader for '" + filename + "'.");
        Stage *s = factory.createStage(driver);
        pdal::Options opts;
        opts.add("filename", filename);
        s->setOptions(opts);

        QuickInfo qi = s->preview();

        if (!qi.valid())
            throw FatalErrorX("Couldn't get quick info for '" + filename + "'.");

        // Get scale values from the reader if they exist.
        pdal::MetadataNode root = s->getMetadata();
        pdal::MetadataNode m = root.findChild("scale_x");
        if (m.valid())
            m_b.scale[0] = (std::max)(m_b.scale[0], m.value<double>());
        m = root.findChild("scale_y");
        if (m.valid())
            m_b.scale[1] = (std::max)(m_b.scale[1], m.value<double>());
        m = root.findChild("scale_z");
        if (m.valid())
            m_b.scale[2] = (std::max)(m_b.scale[2], m.value<double>());
        m = root.findChild("offset_x");
        if (m.valid())
            xOffsets.push_back(m.value<double>());
        m = root.findChild("offset_y");
        if (m.valid())
            yOffsets.push_back(m.value<double>());
        m = root.findChild("offset_z");
        if (m.valid())
            zOffsets.push_back(m.value<double>());

        FileInfoX fi;
        fi.bounds = qi.m_bounds;
        fi.numPoints = qi.m_pointCount;
        fi.filename = filename;
        fi.driver = driver;

        // Accept dimension names if there are no limits or this name is in the list
        // of desired dimensions.
        for (const std::string& name : qi.m_dimNames)
            if (dimNames.empty() || Utils::contains(dimNames, Utils::toupper(name)))
                fi.dimInfo.push_back(untwine::FileDimInfoX(name));

        if (m_srsFileInfo.valid() && m_srsFileInfo.srs != qi.m_srs)
            std::cerr << "Files have mismatched SRS values. Using SRS from '" <<
                m_srsFileInfo.filename << "'.\n";
        fi.srs = qi.m_srs;
        tempFileInfos.push_back(fi);
        if (!m_srsFileInfo.valid() && qi.m_srs.valid())
            m_srsFileInfo = fi;

        m_grid.expand(qi.m_bounds, qi.m_pointCount);
        totalPoints += fi.numPoints;
    }

    // If we had an offset from the input, choose one in the middle of the list of offsets.
    if (xOffsets.size())
    {
        std::sort(xOffsets.begin(), xOffsets.end());
        m_b.offset[0] = xOffsets[xOffsets.size() / 2];
    }
    if (yOffsets.size())
    {
        std::sort(yOffsets.begin(), yOffsets.end());
        m_b.offset[1] = yOffsets[yOffsets.size() / 2];
    }
    if (zOffsets.size())
    {
        std::sort(zOffsets.begin(), zOffsets.end());
        m_b.offset[2] = zOffsets[zOffsets.size() / 2];
    }

    // If we have LAS start capability, break apart file infos into chunks of size 5 million.
#ifdef PDAL_LAS_START
    PointCount ChunkSize = 5'000'000;
    for (const FileInfoX& fi : tempFileInfos)
    {
        if (fi.driver != "readers.las" || fi.numPoints < ChunkSize)
        {
            fileInfos.push_back(fi);
            continue;
        }
        PointCount remaining = fi.numPoints;
        pdal::PointId start = 0;
        while (remaining)
        {
            FileInfoX lasFi(fi);
            lasFi.numPoints = (std::min)(ChunkSize, remaining);
            lasFi.start = start;
            fileInfos.push_back(lasFi);

            start += ChunkSize;
            remaining -= lasFi.numPoints;
        }
    }
#else
    fileInfos = std::move(tempFileInfos);
#endif

    return totalPoints;
}



int main()
{

  // originally member vars
  untwine::epf::GridX m_grid;
  BaseInfo m_b;
  FileInfoX m_srsFileInfo;
  std::unique_ptr<WriterX> m_writer;
  untwine::ThreadPoolX m_pool(8);

  m_b.opts.fileLimit = 10000000;
  m_b.opts.tempDir = "/tmp/epf";
  m_b.opts.inputFiles.push_back("/home/martin/qgis/point-cloud-sandbox/data/trencin.laz");

  BOX3D totalBounds;

  if (pdal::FileUtils::fileExists(m_b.opts.tempDir + "/" + MetadataFilename))
    throw FatalErrorX("Output directory already contains EPT data.");

  m_grid.setCubic(m_b.opts.doCube);

  // Create the file infos. As each info is created, the N x N x N grid is expanded to
  // hold all the points. If the number of points seems too large, N is expanded to N + 1.
  // The correct N is often wrong, especially for some areas where things are more dense.
  std::vector<untwine::epf::FileInfoX> fileInfos;
  point_count_t totalPoints = createFileInfo(m_b.opts.inputFiles, m_b.opts.dimNames, fileInfos, m_b, m_grid, m_srsFileInfo);

  if (m_b.opts.level != -1)
      m_grid.resetLevel(m_b.opts.level);

  // This is just a debug thing that will allow the number of input files to be limited.
  if (fileInfos.size() > m_b.opts.fileLimit)
      fileInfos.resize(m_b.opts.fileLimit);

  // Stick all the dimension names from each input file in a set.
  std::unordered_set<std::string> allDimNames;
  for (const FileInfoX& fi : fileInfos)
      for (const untwine::FileDimInfoX& fdi : fi.dimInfo)
          allDimNames.insert(fdi.name);

  // Register the dimensions, either as the default type or double if we don't know
  // what it is.
  PointLayoutPtr layout(new PointLayout());
  for (const std::string& dimName : allDimNames)
  {
      Dimension::Type type;
      try
      {
          type = Dimension::defaultType(Dimension::id(dimName));
      }
      catch (pdal::pdal_error&)
      {
          type = Dimension::Type::Double;
      }
      layout->registerOrAssignDim(dimName, type);
  }
  layout->finalize();

  // Fill in dim info now that the layout is finalized.
  for (FileInfoX& fi : fileInfos)
  {
      for (untwine::FileDimInfoX& di : fi.dimInfo)
      {
          di.dim = layout->findDim(di.name);
          di.type = layout->dimType(di.dim);
          di.offset = layout->dimOffset(di.dim);
      }
  }

  // Make a writer with NumWriters threads.
  m_writer.reset(new WriterX(m_b.opts.tempDir, NumWriters, layout->pointSize()));

  // Sort file infos so the largest files come first. This helps to make sure we don't delay
  // processing big files that take the longest (use threads more efficiently).
  std::sort(fileInfos.begin(), fileInfos.end(), [](const FileInfoX& f1, const FileInfoX& f2)
      { return f1.numPoints > f2.numPoints; });

  //progress.setPointIncrementer(totalPoints, 40);

  // Add the files to the processing pool
  m_pool.trap(true, "Unknown error in FileProcessor");
  for (const FileInfoX& fi : fileInfos)
  {
      int pointSize = layout->pointSize();
      m_pool.add([&fi, /*&progress,*/ pointSize, &m_grid, &m_writer]()
      {
          untwine::epf::FileProcessorX fp(fi, pointSize, m_grid, m_writer.get() /*, progress*/);
          fp.run();
      });
  }

  // Wait for  all the processors to finish and restart.
  m_pool.join();
  // Tell the writer that it can exit. stop() will block until the writer threads
  // are finished.  stop() will throw if an error occurred during writing.
  m_writer->stop();

  // If the FileProcessors had an error, throw.
  std::vector<std::string> errors = m_pool.clearErrors();
  if (errors.size())
      throw FatalErrorX(errors.front());


  cout << "Hello World!  " << totalPoints << " " << fileInfos.size() << endl;
  return 0;
}
