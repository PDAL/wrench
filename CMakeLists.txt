cmake_minimum_required(VERSION 3.5)

project(pdal_wrench LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(PDAL REQUIRED)
find_package(GDAL REQUIRED)

add_executable(pdal_wrench
    src/main.cpp
    src/alg.cpp
    src/boundary.cpp
    src/clip.cpp
    src/density.cpp
    src/info.cpp
    src/merge.cpp
    src/thin.cpp
    src/to_raster.cpp
    src/to_raster_tin.cpp
    src/to_vector.cpp
    src/translate.cpp
    src/utils.cpp
    src/vpc.cpp

    src/tile/tile.cpp
    src/tile/BufferCache.cpp
    src/tile/Cell.cpp
    src/tile/FileProcessor.cpp
    src/tile/Las.cpp
    src/tile/TileGrid.cpp
    src/tile/ThreadPool.cpp
    src/tile/Writer.cpp
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
