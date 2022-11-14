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
#include <pdal/io/BufferReader.hpp>

#include "CommonX.hpp"
#include "GridX.hpp"
#include "FileDimInfoX.hpp"
#include "EpfTypesX.hpp"
#include "WriterX.hpp"
#include "FileProcessorX.hpp"
#include "LasX.hpp"

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
    std::vector<FileInfoX>& fileInfos, BaseInfo &m_b, TileGrid &m_grid, FileInfoX &m_srsFileInfo)
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




static void fillMetadata(const pdal::PointLayoutPtr layout, BaseInfo &m_b, const TileGrid &m_grid, FileInfoX &m_srsFileInfo)
{
    using namespace pdal;

    // Info to be passed to sampler.
    m_b.bounds = m_grid.processingBounds();
    m_b.trueBounds = m_grid.conformingBounds();
    if (m_srsFileInfo.valid())
        m_b.srs = m_srsFileInfo.srs;
    m_b.pointSize = 0;

    // Set the pointFormatId based on whether or not colors exist in the file
    if (layout->hasDim(Dimension::Id::Infrared))
        m_b.pointFormatId = 8;
    else if (layout->hasDim(Dimension::Id::Red) ||
             layout->hasDim(Dimension::Id::Green) ||
             layout->hasDim(Dimension::Id::Blue))
        m_b.pointFormatId = 7;
    else
        m_b.pointFormatId = 6;

    const Dimension::IdList& lasDims = untwine::pdrfDims(m_b.pointFormatId);
    for (Dimension::Id id : layout->dims())
    {
        untwine::FileDimInfoX di;
        di.name = layout->dimName(id);
        di.type = layout->dimType(id);
        di.offset = layout->dimOffset(id);
        di.dim = id;
        di.extraDim = !Utils::contains(lasDims, id);
        m_b.pointSize += pdal::Dimension::size(di.type);
        m_b.dimInfo.push_back(di);
    }
    auto calcScale = [](double scale, double low, double high)
    {
        if (scale > 0)
            return scale;

        // 2 billion is a little less than the int limit.  We center the data around 0 with the
        // offset, so we're applying the scale to half the range of the data.
        double val = high / 2 - low / 2;
        double power = std::ceil(std::log10(val / 2000000000.0));

        // Set an arbitrary limit on scale of 1e10-4.
        return std::pow(10, (std::max)(power, -4.0));
    };

    m_b.scale[0] = calcScale(m_b.scale[0], m_b.trueBounds.minx, m_b.trueBounds.maxx);
    m_b.scale[1] = calcScale(m_b.scale[1], m_b.trueBounds.miny, m_b.trueBounds.maxy);
    m_b.scale[2] = calcScale(m_b.scale[2], m_b.trueBounds.minz, m_b.trueBounds.maxz);

    // Find an offset such that (offset - min) / scale is close to an integer. This helps
    // to eliminate warning messages in lasinfo that complain because of being unable
    // to write nominal double values precisely using a 32-bit integer.
    // The hope is also that raw input values are written as the same raw values
    // on output. This may not be possible if the input files have different scaling or
    // incompatible offsets.
    auto calcOffset = [](double minval, double maxval, double scale)
    {
        double interval = maxval - minval;
        double spacings = interval / scale;  // Number of quantized values in our range.
        double halfspacings = spacings / 2;  // Half of that number.
        double offset = (int32_t)halfspacings * scale; // Round to an int value and scale down.
        return minval + offset;              // Add the base (min) value.
    };

    m_b.offset[0] = calcOffset(m_b.trueBounds.minx, m_b.trueBounds.maxx, m_b.scale[0]);
    m_b.offset[1] = calcOffset(m_b.trueBounds.miny, m_b.trueBounds.maxy, m_b.scale[1]);
    m_b.offset[2] = calcOffset(m_b.trueBounds.minz, m_b.trueBounds.maxz, m_b.scale[2]);
    std::cout << "fill metadata: " << m_b.scale[0] << " " << m_b.scale[1] << " " << m_b.scale[2]
              << m_b.offset[0] << " " << m_b.offset[1] << " " << m_b.offset[2] << std::endl;
}




static void writeOutputFile(const std::string& filename, pdal::PointViewPtr view, const BaseInfo &m_b)
{
    using namespace pdal;

    StageFactory factory;

    BufferReader r;
    r.addView(view);

    Stage *prev = &r;

    if (view->layout()->hasDim(Dimension::Id::GpsTime))
    {
        Stage *f = factory.createStage("filters.sort");
        pdal::Options fopts;
        fopts.add("dimension", "gpstime");
        f->setOptions(fopts);
        f->setInput(*prev);
        prev = f;
    }

    Stage *w = factory.createStage("writers.las");
    pdal::Options wopts;
    wopts.add("extra_dims", "all");
    wopts.add("software_id", "Entwine 1.0");
    wopts.add("compression", "laszip");
    wopts.add("filename", filename);
    wopts.add("offset_x", m_b.offset[0]);
    wopts.add("offset_y", m_b.offset[1]);
    wopts.add("offset_z", m_b.offset[2]);
    wopts.add("scale_x", m_b.scale[0]);
    wopts.add("scale_y", m_b.scale[1]);
    wopts.add("scale_z", m_b.scale[2]);
    wopts.add("minor_version", 4);
    wopts.add("dataformat_id", m_b.pointFormatId);

    wopts.add("a_srs", "EPSG:5514");

//    if (m_b.opts.a_srs.size())
//        wopts.add("a_srs", m_b.opts.a_srs);
    if (m_b.opts.metadata)
        wopts.add("pdal_metadata", m_b.opts.metadata);
    w->setOptions(wopts);
    w->setInput(*prev);

    w->prepare(view->table());
    w->execute(view->table());
}




int main()
{

  // originally member vars
  untwine::epf::TileGrid m_grid;
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

  //if (m_b.opts.level != -1)
  //    m_grid.resetLevel(m_b.opts.level);

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
#if 1   // TODO: only temporarily disabled to test writing of output
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
#endif
  // If the FileProcessors had an error, throw.
  std::vector<std::string> errors = m_pool.clearErrors();
  if (errors.size())
      throw FatalErrorX(errors.front());


  //cout << "Hello World!  " << totalPoints << " " << fileInfos.size() << endl;

  //---------

  fillMetadata( layout, m_b, m_grid, m_srsFileInfo );

  //---------

  untwine::ThreadPoolX m_pool2(8);

  std::vector<std::string> lstBinFiles = directoryList("/tmp/epf");
  std::string finalDir = "/tmp/epf-tiles";

  int outFileIdx = 0;
  for ( std::string binFile : lstBinFiles )
  {
      std::string outFilename = finalDir + "/" + std::to_string(outFileIdx) + ".laz";    // TODO: use tile coords!
      outFileIdx++;

      m_pool2.add([binFile, outFilename, &m_b]()
      {
          std::cout << "output: " << binFile << std::endl;

          PointTable table;

          //ABELL - fixme
          // For now we copy the dimension list so we're sure that it matches the layout, though
          // there's no reason why it should change. We should modify things to use a single
          // layout.

          Dimension::IdList lasDims = untwine::pdrfDims(m_b.pointFormatId);
          untwine::DimInfoListX dims = m_b.dimInfo;
          // TODO m_extraDims.clear();
          for (untwine::FileDimInfoX& fdi : dims)
          {
              fdi.dim = table.layout()->registerOrAssignDim(fdi.name, fdi.type);
              // TODO
              //if (!Utils::contains(lasDims, fdi.dim))
              //    m_extraDims.push_back(DimType(fdi.dim, fdi.type));
          }
          table.finalize();

          PointViewPtr view(new pdal::PointView(table));

          // TODO: use file mapping?
          int ptCnt = 0;
          std::ifstream fileReader(binFile,std::ios::binary|std::ios::ate);
          assert(fileReader); // TODO
          auto fileSize = fileReader.tellg();
          fileReader.seekg(std::ios::beg);
          std::string content(fileSize,0);
          fileReader.read(&content[0],fileSize);
          char *contentPtr = content.data();

          std::cout << "pt cnt " << (double) fileSize / m_b.pointSize << std::endl;
          ptCnt = fileSize / m_b.pointSize;

          pdal::PointId pointId = view->size();
          for ( int i = 0; i < ptCnt; ++i )
          {
              char *base = contentPtr + i * m_b.pointSize;
              for (const untwine::FileDimInfoX& fdi : dims)
                  view->setField(fdi.dim, fdi.type, pointId,
                      reinterpret_cast<void *>(base + fdi.offset));
              pointId++;
          }

          writeOutputFile( outFilename, view, m_b);
      });
  }

  m_pool2.join();

  return 0;
}
