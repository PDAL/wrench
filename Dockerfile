# Author: Daniel Rode


# https://docs.docker.com/reference/dockerfile/


FROM alpine:latest

RUN ash <<'EOF'
    set -e  # Exit on error

    # Install Alpine Linux packages for building PDAL Wrench
    apk update
    apk add \
        cmake \
        g++ \
        git \
        make \
        pdal-dev \
    ;

    # Build and install PDAL Wrench from source
    git clone "https://github.com/PDAL/wrench"
    mkdir wrench/build
    cd wrench/build
    cmake ..
    make

    mv pdal_wrench /usr/local/bin/pdal_wrench
    cd ../../
    rm -r wrench/
EOF
