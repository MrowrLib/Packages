vcpkg_from_git(
    OUT_SOURCE_PATH SOURCE_PATH
    URL https://github.com/MrowrLib/memory_util.cpp.git
    REF 6f11d4bae1ebc526a60ff6b0979780f3b2930066
)

vcpkg_cmake_configure(
    SOURCE_PATH {SOURCE_PATH}
)

vcpkg_cmake_install()

vcpkg_cmake_config_fixup(CONFIG_PATH lib/cmake/memory_util.cpp)
