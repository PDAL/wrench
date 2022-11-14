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


#pragma once

#include <pdal/util/Bounds.hpp>

#include "VoxelKeyX.hpp"


namespace untwine
{
namespace epf
{

class TileGrid
{
public:
    TileGrid() : m_millionPoints(0), m_cubic(true)
    {}

    void expand(const pdal::BOX3D& bounds, size_t points);
    TileKey key(double x, double y, double z) const;
    pdal::BOX3D processingBounds() const
        { return m_cubic ? m_cubicBounds : m_bounds; }
    pdal::BOX3D cubicBounds() const
        { return m_cubicBounds; }
    pdal::BOX3D conformingBounds() const
        { return m_bounds; }

    void setCubic(bool cubic)
        { m_cubic = cubic; }

private:
    double m_tileLength = 100;
    int m_gridSizeX = 0, m_gridSizeY = 0;

    pdal::BOX3D m_bounds;
    pdal::BOX3D m_cubicBounds;
    size_t m_millionPoints;
    bool m_cubic;
    double m_xsize;
    double m_ysize;
    double m_zsize;
};

} // namespace epf
} // namespace untwine
