vcpkg_from_git(
    OUT_SOURCE_PATH SOURCE_PATH
    URL https://github.com/MrowrLib/MiniSpecs.cpp.git
    REF ddf3abc7a15b7fc47d890e001f782b35a8815941
)

vcpkg_cmake_configure(
    SOURCE_PATH ${SOURCE_PATH}
)

vcpkg_cmake_install()

file(REMOVE_RECURSE
    "${CURRENT_PACKAGES_DIR}/debug"
    "${CURRENT_PACKAGES_DIR}/lib"
)

file(MAKE_DIRECTORY "${CURRENT_PACKAGES_DIR}/share/${PORT}")
file(INSTALL "${SOURCE_PATH}/LICENSE" DESTINATION "${CURRENT_PACKAGES_DIR}/share/${PORT}" RENAME copyright)
