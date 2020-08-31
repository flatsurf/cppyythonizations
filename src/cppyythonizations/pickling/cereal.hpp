/**********************************************************************
 *  This file is part of cppyythonizations.
 *
 *        Copyright (C) 2019-2020 Julian Rüth
 *
 *  Permission is hereby granted, free of charge, to any person obtaining a copy
 *  of this software and associated documentation files (the "Software"), to deal
 *  in the Software without restriction, including without limitation the rights
 *  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 *  copies of the Software, and to permit persons to whom the Software is
 *  furnished to do so, subject to the following conditions:
 *  
 *  The above copyright notice and this permission notice shall be included in all
 *  copies or substantial portions of the Software.
 *  
 *  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 *  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 *  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 *  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 *  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 *  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 *  SOFTWARE.
 **********************************************************************/

#ifndef CPPYYTHONIZATIONS_PICKLE_CEREAL_HPP
#define CPPYYTHONIZATIONS_PICKLE_CEREAL_HPP

#include <cereal/archives/json.hpp>
#include <cereal/cereal.hpp>
#include <cereal/types/memory.hpp>
#include <iosfwd>
#include <memory>
#include <sstream>
#include <string>

namespace cppyythonizations {
namespace pickling {
namespace cereal {

// A helper to get RAII that cereal needs to make sure that its output has been flushed.
template <typename T>
std::string serialize(const T &value) {
  std::stringstream serialized;
  {
    ::cereal::JSONOutputArchive archive(serialized, ::cereal::JSONOutputArchive::Options::NoIndent());
    archive(::cereal::make_nvp("cereal", value));
  }
  return serialized.str();
}

// For the sake of symmetry, the same for deserialization.
template <typename T>
T deserialize(const std::string &serialized) {
  std::stringstream stream(serialized);
  T value;
  {
    ::cereal::JSONInputArchive archive(stream);
    archive(::cereal::make_nvp("cereal", value));
  }
  return value;
}

}  // namespace cereal
}  // namespace pickling
}  // namespace cppyythonizations

#endif
