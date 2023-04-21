vcpkg_from_git(
    OUT_SOURCE_PATH SOURCE_PATH
    URL https://github.com/MrowrLib/_Log_.cpp.git
    REF 16841a3d6c005959af7de7366c7469200280d608
)

vcpkg_cmake_configure(
    SOURCE_PATH ${SOURCE_PATH}
    OPTIONS -DBUILD_EXAMPLE=OFF
)

vcpkg_cmake_install()

file(INSTALL ${SOURCE_PATH}/LICENSE DESTINATION ${CURRENT_PACKAGES_DIR}/share/${PORT}/copyright)
file(INSTALL ${CURRENT_PACKAGES_DIR}/share/${PORT}/ DESTINATION ${CURRENT_PACKAGES_DIR}/share/_Log_)

file(REMOVE_RECURSE
    "${CURRENT_PACKAGES_DIR}/share/${PORT}"
    "${CURRENT_PACKAGES_DIR}/debug"
    "${CURRENT_PACKAGES_DIR}/lib"
)
