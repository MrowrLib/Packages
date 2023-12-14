vcpkg_from_git(
    OUT_SOURCE_PATH SOURCE_PATH
    URL https://github.com/mrowrpurr/Specs.cpp.git
    REF 515e85098ee38e9b7bf8bac4931b57d9e0444361
)

vcpkg_cmake_configure(
    SOURCE_PATH ${SOURCE_PATH}
    OPTIONS
        -DBUILD_SPECS=ON
        -DBUILD_SNOWHOUSE_ADAPTER=OFF
        -DBUILD_LIBASSERT_ADAPTER=OFF
)

vcpkg_cmake_install()

if(VCPKG_BUILD_TYPE STREQUAL "debug")
    # Delete all the release lib files
    file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/lib/*.lib")

    # Copy everything from debug/lib into lib
    file(GLOB DEBUG_LIBS "${CURRENT_PACKAGES_DIR}/debug/lib/*.lib")
    file(COPY ${DEBUG_LIBS} DESTINATION "${CURRENT_PACKAGES_DIR}/lib")
endif()


file(REMOVE_RECURSE
    "${CURRENT_PACKAGES_DIR}/debug/include"
    "${CURRENT_PACKAGES_DIR}/debug/share"
)

file(MAKE_DIRECTORY "${CURRENT_PACKAGES_DIR}/share/${PORT}")
file(INSTALL "${SOURCE_PATH}/LICENSE" DESTINATION "${CURRENT_PACKAGES_DIR}/share/${PORT}" RENAME copyright)
