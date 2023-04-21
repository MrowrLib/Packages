vcpkg_from_git(
    OUT_SOURCE_PATH SOURCE_PATH
    URL https://github.com/MrowrLib/string_format.cpp.git
    REF 45e8db50ba8a68b6fda60a31b41c37411aa156ad
)

message("What is PORT? ${PORT}")
message("What is SOURCE PATH? ${SOURCE_PATH}")
message("What is CURRENT_PACKAGES_DIR? ${CURRENT_PACKAGES_DIR}")

configure_file("${SOURCE_PATH}/LICENSE" "${CURRENT_PACKAGES_DIR}/share/${PORT}/copyright" COPYONLY)

vcpkg_cmake_configure(SOURCE_PATH ${SOURCE_PATH})

vcpkg_cmake_install()

file(COPY ${CURRENT_PACKAGES_DIR}/share/${PORT}/ DESTINATION ${CURRENT_PACKAGES_DIR}/share/string_format)

file(REMOVE_RECURSE
    "${CURRENT_PACKAGES_DIR}/share/${PORT}"
    "${CURRENT_PACKAGES_DIR}/debug"
    "${CURRENT_PACKAGES_DIR}/lib"
)
