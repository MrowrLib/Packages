vcpkg_from_git(
    OUT_SOURCE_PATH SOURCE_PATH
    URL https://github.com/mrowrpurr/Specs.cpp.git
    REF dab4f3c40a55b34dd8e45aa79d0d2760617ffc7e
)

vcpkg_cmake_configure(
    SOURCE_PATH ${SOURCE_PATH}
    OPTIONS
        -DBUILD_SPECS=ON
        -DBUILD_SNOWHOUSE_ADAPTER=OFF
        -DBUILD_LIBASSERT_ADAPTER=OFF
)

vcpkg_cmake_install()

file(REMOVE_RECURSE
    "${CURRENT_PACKAGES_DIR}/debug"
)

file(MAKE_DIRECTORY "${CURRENT_PACKAGES_DIR}/share/${PORT}")
file(INSTALL "${SOURCE_PATH}/LICENSE" DESTINATION "${CURRENT_PACKAGES_DIR}/share/${PORT}" RENAME copyright)
