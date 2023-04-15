vcpkg_from_git(
    OUT_SOURCE_PATH SOURCE_PATH
    URL https://github.com/MrowrLib/string_format.cpp.git
    REF main
)

vcpkg_cmake_configure(
    SOURCE_PATH {SOURCE_PATH}
)

vcpkg_cmake_install()

vcpkg_cmake_config_fixup(CONFIG_PATH lib/cmake/string_format.cpp)
