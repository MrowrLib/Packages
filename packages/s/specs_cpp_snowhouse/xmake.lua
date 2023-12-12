package("specs_cpp_snowhouse")
    set_homepage("https://github.com/mrowrpurr/Specs.cpp")
    set_description("Snowhouse assertion support for Specs.cpp")
    add_urls("https://github.com/mrowrpurr/Specs.cpp.git")
    on_install(function (package)
        -- Snowhouse integration for Specs.cpp
        os.cp("Specs.Snowhouse/include/*", package:installdir())
    end)
