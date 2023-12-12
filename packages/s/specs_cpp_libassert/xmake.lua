package("specs_cpp_libassert")
    set_homepage("https://github.com/mrowrpurr/Specs.cpp")
    set_description("libassert assertion support for Specs.cpp")
    add_urls("https://github.com/mrowrpurr/Specs.cpp.git")
    on_install(function (package)
        local include_dir = path.join(package:includedir(), "include")

        if not os.isdir(include_dir) then
            os.mkdir(include_dir)
        end

        -- libassert integration for Specs.cpp
        os.cp("Specs.LibAssert/include/*", include_dir)
    end)
