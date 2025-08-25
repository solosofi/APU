cmake_minimum_required(VERSION 3.10)
project(core)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(core SHARED core.cpp)

# In the future, we will add PAPI or other performance counter libraries here
# target_link_libraries(core PRIVATE PAPI)
