cmake_minimum_required(VERSION 3.5)

project(tile-writer LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(PDAL REQUIRED)

add_executable(tile-writer
    main.cpp

    BufferCache.cpp
    Cell.cpp
    FileProcessor.cpp
    Las.cpp
    TileGrid.cpp
    ThreadPool.cpp
    Writer.cpp

    BufferCache.hpp
    Cell.hpp
    Common.hpp
    EpfTypes.hpp
    FileDimInfo.hpp
    FileProcessor.hpp
    Las.hpp
    Point.hpp
    TileGrid.hpp
    TileKey.hpp
    ThreadPool.hpp
    Writer.hpp
)

target_include_directories(tile-writer
    PRIVATE
        #${CMAKE_CURRENT_BINARY_DIR}/include
        ${PDAL_INCLUDE_DIRS}
        #${PROJECT_SOURCE_DIR}
)
target_link_libraries(tile-writer
    PRIVATE
        #${CMAKE_THREAD_LIBS_INIT}
        ${PDAL_LIBRARIES}
)

install(TARGETS tile-writer
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR})
