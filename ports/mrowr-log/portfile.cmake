vcpkg_from_git(
    OUT_SOURCE_PATH SOURCE_PATH
    URL https://github.com/MrowrLib/_Log_.cpp.git
    REF 16841a3d6c005959af7de7366c7469200280d608
)

# set(LIBRARY_NAME _Log_)
message(STATUS "PORT: ${PORT}")
message(STATUS "SOURCE_PATH: ${SOURCE_PATH}")
message(STATUS "CURRENT_PACKAGES_DIR: ${CURRENT_PACKAGES_DIR}")

# Print out whether CURRENT_PACKAGES_DIRECTORY/share/${PORT} exists
if(EXISTS "${CURRENT_PACKAGES_DIR}/share/${PORT}")
    message(STATUS "CURRENT_PACKAGES_DIR/share/${PORT} exists")
else()
    message(STATUS "CURRENT_PACKAGES_DIR/share/${PORT} does not exist")
endif()

message("Configuring...")

vcpkg_cmake_configure(
    SOURCE_PATH ${SOURCE_PATH}
    OPTIONS -DBUILD_EXAMPLE=OFF
)

message("Installing...")

vcpkg_cmake_install()

message("Installed.")

message(STATUS "PORT: ${PORT}")
message(STATUS "SOURCE_PATH: ${SOURCE_PATH}")
message(STATUS "CURRENT_PACKAGES_DIR: ${CURRENT_PACKAGES_DIR}")

# Print out whether CURRENT_PACKAGES_DIRECTORY/share/${PORT} exists
if(EXISTS "${CURRENT_PACKAGES_DIR}/share/${PORT}")
    message(STATUS "CURRENT_PACKAGES_DIR/share/${PORT} exists")
else()
    message(STATUS "CURRENT_PACKAGES_DIR/share/${PORT} does not exist")
endif()

file(COPY "${CURRENT_PACKAGES_DIR}/share/${PORT}/" DESTINATION "${CURRENT_PACKAGES_DIR}/share/_Log_")

# file(COPY "${CURRENT_PACKAGES_DIR}/share/${PORT}/" DESTINATION "${CURRENT_PACKAGES_DIR}/share/${LIBRARY_NAME}")

# "${CURRENT_PACKAGES_DIR}/share/${PORT}/*/**"
file(REMOVE_RECURSE
    "${CURRENT_PACKAGES_DIR}/debug"
    "${CURRENT_PACKAGES_DIR}/lib"
)

file(MAKE_DIRECTORY "${CURRENT_PACKAGES_DIR}/share/${PORT}")
file(COPY "${SOURCE_PATH}/LICENSE" DESTINATION "${CURRENT_PACKAGES_DIR}/share/${PORT}")
