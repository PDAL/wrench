#ifndef COMMONX_HPP
#define COMMONX_HPP

#include <stdexcept>

using PointCount = uint64_t;

class  FatalError : public std::runtime_error
{
public:
    inline FatalError(std::string const& msg) : std::runtime_error(msg)
        {}
};

namespace untwine
{
  // TODO: windows needs special treatment
inline std::string toNative(const std::string& in)
{
    return in;
}

inline std::string fromNative(const std::string& in)
{
    return in;
}
}

#endif // COMMONX_HPP
