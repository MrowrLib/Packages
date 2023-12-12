package("specs_cpp_snowhouse")
    set_homepage("https://github.com/mrowrpurr/Specs.cpp")
    set_description("Snowhouse assertion support for Specs.cpp")
    add_urls("https://github.com/mrowrpurr/Specs.cpp.git")
    on_install(function (package)
        local include_dir = path.join(package:installdir(), "include")

        if not os.isdir(include_dir) then
            os.mkdir(include_dir)
        end

        -- Snowhouse integration for Specs.cpp
        os.cp("Specs.Snowhouse/include/*", include_dir)
    end)
