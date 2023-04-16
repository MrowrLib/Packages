vcpkg_from_git(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO https://github.com/MrowrLib/string_format.cpp.git
    REF f50ff588425b562e5965a7170ca1dbb19b2a93ce
)

vcpkg_cmake_configure(
    SOURCE_PATH {SOURCE_PATH}
)

vcpkg_cmake_install()

vcpkg_cmake_config_fixup(CONFIG_PATH lib/cmake/string_format)
