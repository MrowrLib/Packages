file(DOWNLOAD "https://api.github.com/repos/MrowrLib/string_format.cpp/tarball/main" ${DOWNLOADS}/archive.tar.gz
    SHOW_PROGRESS
)

vcpkg_extract_source_archive(
    SOURCE_PATH
    ARCHIVE ${DOWNLOADS}/archive.tar.gz
)

vcpkg_cmake_configure(
    SOURCE_PATH ${SOURCE_PATH}
)

vcpkg_cmake_install()

file(INSTALL ${SOURCE_PATH}/LICENSE DESTINATION ${CURRENT_PACKAGES_DIR}/share/${PORT} RENAME copyright)

vcpkg_cmake_config_fixup(CONFIG_PATH lib/cmake/string_format)
