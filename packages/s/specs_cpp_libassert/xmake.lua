package("specs_cpp_libassert")
    set_homepage("https://github.com/mrowrpurr/Specs.cpp")
    set_description("libassert assertion support for Specs.cpp")
    add_urls("https://github.com/mrowrpurr/Specs.cpp.git")
    on_install(function (package)
        -- libassert integration for Specs.cpp
        os.cp("Specs.LibAssert/include/*", package:installdir())
    end)
