vcpkg_from_git(
    OUT_SOURCE_PATH SOURCE_PATH
    URL https://github.com/MrowrLib/string_format.cpp.git
    REF 762d4582492d5c60892e2c38f6fe30b3a9733149
)

vcpkg_cmake_configure(
    SOURCE_PATH ${SOURCE_PATH}
)

vcpkg_cmake_install()

file(INSTALL ${SOURCE_PATH}/LICENSE DESTINATION ${CURRENT_PACKAGES_DIR}/share/${PORT} RENAME copyright)

vcpkg_cmake_config_fixup(CONFIG_PATH lib/cmake/string_format)
file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/lib" "${CURRENT_PACKAGES_DIR}/lib")
