cmake_minimum_required(VERSION 3.5)

project(pdal_wrench LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(PDAL REQUIRED)
find_package(GDAL REQUIRED)

add_executable(pdal_wrench
    main.cpp
    alg.cpp
    boundary.cpp
    clip.cpp
    density.cpp
    info.cpp
    merge.cpp
    thin.cpp
    to_raster.cpp
    to_raster_tin.cpp
    to_vector.cpp
    translate.cpp
    utils.cpp
    vpc.cpp
    #MyThreadPool.cpp

    tile/tile.cpp
    tile/BufferCache.cpp
    tile/Cell.cpp
    tile/FileProcessor.cpp
    tile/Las.cpp
    tile/TileGrid.cpp
    tile/ThreadPool.cpp
    tile/Writer.cpp
)

target_include_directories(pdal_wrench
    PRIVATE
        #${CMAKE_CURRENT_BINARY_DIR}/include
        ${PDAL_INCLUDE_DIRS}
        ${GDAL_INCLUDE_DIR}
        #${PROJECT_SOURCE_DIR}
)
target_link_libraries(pdal_wrench
    PRIVATE
        #${CMAKE_THREAD_LIBS_INIT}
        ${PDAL_LIBRARIES}
        ${GDAL_LIBRARY}
)
