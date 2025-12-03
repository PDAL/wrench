cmake_minimum_required(VERSION 3.5)

project(pdal_wrench LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Compile flag. Make it possible to turn it off.
set (PEDANTIC TRUE CACHE BOOL "Determines if we should compile in pedantic mode.")

find_package(PDAL REQUIRED)
find_package(GDAL REQUIRED)
find_package(Threads REQUIRED)

add_executable(pdal_wrench
    src/main.cpp
    src/alg.cpp
    src/boundary.cpp
    src/clip.cpp
    src/density.cpp
    src/filter_noise.cpp
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
        ${CMAKE_THREAD_LIBS_INIT}
)

install(TARGETS pdal_wrench DESTINATION bin)

#############################################################
# enable warnings

if (PEDANTIC)
  message (STATUS "Pedantic compiler settings enabled")

  if(WIN32)
    add_definitions(-DWIN32_LEAN_AND_MEAN)
  endif()

  if(MSVC)
    set(_warnings "")
    if (NOT USING_NMAKE AND NOT USING_NINJA)
      set(_warnings "${_warnings} /W4" )
    endif()

    # disable warnings
    set(_warnings "${_warnings} /wd4091 ")  # 'typedef': ignored on left of '' when no variable is declared (occurs in MS DbgHelp.h header)
    set(_warnings "${_warnings} /wd4100 ")  # unused formal parameters
    set(_warnings "${_warnings} /wd4127 ")  # constant conditional expressions (used in Qt template classes)
    set(_warnings "${_warnings} /wd4190 ")  # 'identifier' has C-linkage specified, but returns UDT 'identifier2' which is incompatible with C
    set(_warnings "${_warnings} /wd4231 ")  # nonstandard extension used : 'identifier' before template explicit instantiation (used in Qt template classes)
    set(_warnings "${_warnings} /wd4244 ")  # conversion from '...' to '...' possible loss of data
    set(_warnings "${_warnings} /wd4251 ")  # needs to have dll-interface to be used by clients of class (occurs in Qt template classes)
    set(_warnings "${_warnings} /wd4267 ")  # 'argument': conversion from 'size_t' to 'int', possible loss of data
    set(_warnings "${_warnings} /wd4275 ")  # non dll-interface class '...' used as base for dll-interface class '...'
    set(_warnings "${_warnings} /wd4290 ")  # c++ exception specification ignored except to indicate a function is not __declspec(nothrow) (occurs in sip generated bindings)
    set(_warnings "${_warnings} /wd4456 ")  # declaration of '...' hides previous local declaration
    set(_warnings "${_warnings} /wd4457 ")  # declaration of '...' hides a function parameter
    set(_warnings "${_warnings} /wd4458 ")  # declaration of '...' hides class member
    set(_warnings "${_warnings} /wd4505 ")  # unreferenced local function has been removed (QgsRasterDataProvider::extent)
    set(_warnings "${_warnings} /wd4510 ")  # default constructor could not be generated (sqlite3_index_info, QMap)
    set(_warnings "${_warnings} /wd4512 ")  # assignment operator could not be generated (sqlite3_index_info)
    set(_warnings "${_warnings} /wd4610 ")  # user defined constructor required (sqlite3_index_info)
    set(_warnings "${_warnings} /wd4706 ")  # assignment within conditional expression (pal)
    set(_warnings "${_warnings} /wd4714 ")  # function '...' marked as __forceinline not inlined (QString::toLower/toUpper/trimmed)
    set(_warnings "${_warnings} /wd4800 ")  # 'int' : forcing value to bool 'true' or 'false' (performance warning)
    set(_warnings "${_warnings} /wd4996 ")  # '...': was declared deprecated (unfortunately triggered when implementing deprecated interfaces even when it is deprecated too)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${_warnings}")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${_warnings}")
  else()
    # add warnings via flags (not as definitions as on Mac -Wall can not be overridden per language )
    set(_warnings "-Wall -Wextra -Wno-long-long -Wformat-security -Wno-strict-aliasing")

    set(WERROR FALSE CACHE BOOL "Treat build warnings as errors.")
    if (WERROR)
      set(_warnings "${_warnings} -Werror")
    endif()
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${_warnings}")

    # c++ only warnings
    set(_warnings "${_warnings} -Wnon-virtual-dtor")

    # unavoidable - we can't avoid these, as older, supported compilers do not support removing the redundant move
    set(_warnings "${_warnings} -Wno-redundant-move")

    # disable misleading-indentation warning -- it's slow to parse the sip files and not needed since we have the automated code styling rules
    set(_warnings "${_warnings} -Wno-misleading-indentation")

    if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" AND CMAKE_CXX_COMPILER_VERSION VERSION_GREATER 7.9.999)
      # heaps of these thrown by Qt headers at the moment (sep 2019)
      set(_warnings "${_warnings} -Wno-deprecated-copy")
    endif()

    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${_warnings}")

    if ("${CMAKE_CXX_COMPILER_ID}" MATCHES "Clang")
       set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wreturn-type-c-linkage -Woverloaded-virtual -Wimplicit-fallthrough")
    endif()

    # add any extra CXXFLAGS flags set by user. can be -D CXX_EXTRA_FLAGS or environment variable
    # command line -D option overrides environment variable
    # e.g. useful for suppressing transient upstream warnings in dependencies, like Qt
    set(CXX_EXTRA_FLAGS "" CACHE STRING "Additional appended CXXFLAGS")
    if ("${CXX_EXTRA_FLAGS}" STREQUAL "" AND DEFINED $ENV{CXX_EXTRA_FLAGS})
      set(CXX_EXTRA_FLAGS "$ENV{CXX_EXTRA_FLAGS}")
    endif()
    if (NOT "${CXX_EXTRA_FLAGS}" STREQUAL "")
      message (STATUS "Appending CXX_EXTRA_FLAGS")
      set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${CXX_EXTRA_FLAGS}")
    endif()
  endif()
endif()

if (CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Qunused-arguments")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Qunused-arguments")
  set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Qunused-arguments")
  set(CMAKE_MODULE_LINKER_FLAGS "${CMAKE_MODULE_LINKER_FLAGS} -Qunused-arguments")
  set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Qunused-arguments")
endif()

if(CMAKE_SYSTEM_PROCESSOR MATCHES "^(powerpc|ppc)")
  # spatialite crashes on ppc - see bugs.debian.org/603986
  add_definitions( -fno-strict-aliasing )
endif()
