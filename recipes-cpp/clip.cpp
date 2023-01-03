
#include <iostream>
#include <thread>

#include <pdal/PipelineManager.hpp>
#include <pdal/Stage.hpp>
#include <pdal/util/ProgramArgs.hpp>
#include <pdal/pdal_types.hpp>
#include <pdal/Polygon.hpp>

#include <gdal/gdal_utils.h>

#include "utils.hpp"
#include "alg.hpp"

using namespace pdal;


void Clip::addArgs()
{
    argOutput = &programArgs.add("output,o", "Output raster file", outputFile);
    argPolygon = &programArgs.add("polygon,p", "Input polygon vector file", polygonFile);
}

bool Clip::checkArgs()
{
    if (!argOutput->set())
    {
        std::cerr << "missing output" << std::endl;
        return false;
    }
    if (!argPolygon->set())
    {
        std::cerr << "missing polygon" << std::endl;
        return false;
    }

    return true;
}


// populate polygons into filters.crop options
bool loadPolygons(const std::string &polygonFile, pdal::Options& crop_opts)
{
    GDALAllRegister();

    GDALDatasetH hDS = GDALOpenEx( polygonFile.c_str(), GDAL_OF_VECTOR, NULL, NULL, NULL );
    if( hDS == NULL )
    {
        std::cout << "cannot open polygon " << polygonFile << std::endl;
        return false;
    }

    OGRLayerH hLayer = GDALDatasetGetLayer(hDS, 0);
    //hLayer = GDALDatasetGetLayerByName( hDS, "point" );

    OGR_L_ResetReading(hLayer);
    OGRFeatureH hFeature;
    while( (hFeature = OGR_L_GetNextFeature(hLayer)) != NULL )
    {
        OGRGeometryH hGeometry = OGR_F_GetGeometryRef(hFeature);
        if ( hGeometry != NULL )
        {
            crop_opts.add(pdal::Option("polygon", Polygon(hGeometry)));
        }
        OGR_F_Destroy( hFeature );
    }
    GDALClose( hDS );
    return true;
}


void Clip::preparePipelines(std::vector<std::unique_ptr<PipelineManager>>& pipelines, const BOX3D &bounds)
{
    // TODO: parallel runs

    std::unique_ptr<PipelineManager> manager( new PipelineManager );
    Stage& r = manager->makeReader(inputFile, "");

    pdal::Options crop_opts;
    if (!loadPolygons(polygonFile, crop_opts))
        return;

    Stage& f = manager->makeFilter( "filters.crop", r, crop_opts );

    pdal::Options writer_opts;
    writer_opts.add(pdal::Option("forward", "all"));

    Stage& w = manager->makeWriter(outputFile, "", f, writer_opts);

    pipelines.push_back(std::move(manager));
}
