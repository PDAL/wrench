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


#include "EpfTypesX.hpp"
#include "GridX.hpp"
#include "CellX.hpp"

namespace untwine
{

class ProgressWriter;

namespace epf
{

class WriterX;

// Processes a single input file (FileInfo) and writes data to the Writer.
class FileProcessorX
{
public:
    FileProcessorX(const FileInfoX& fi, size_t pointSize, const GridX& grid, WriterX *writer/*,
        ProgressWriter& progress*/);

    Cell *getCell(const VoxelKeyX& key);
    void run();

private:
    FileInfoX m_fi;
    CellMgr m_cellMgr;
    GridX m_grid;
    //ProgressWriter& m_progress;
};

} // namespace epf
} // namespace untwine
