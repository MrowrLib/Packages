package("specs_cpp")
    set_homepage("https://github.com/mrowrpurr/Specs.cpp")
    set_description("Async BDD C++ Test Framework.")
    add_urls("https://github.com/mrowrpurr/Specs.cpp.git")
    add_deps(
        "function_pointer",
        "global_macro_functions",
        "collections",
        "underscore_log",
        "string_format",
        "cxxopts"
    )
    on_install(function (package)
        -- The C++ interfaces
        os.cp("Specs.API/include/*", package:installdir())

        -- Support for shared DLLs
        os.cp("Specs.DLL/include/*", package:installdir())
        os.cp("Specs.DllLoader/include/*", package:installdir())

        -- Core implementation classes for main interfaces
        os.cp("Specs.Implementations/include/*", package:installdir())

        -- Available Runners and Reporters
        os.cp("Specs.Runners/include/*", package:installdir())
        os.cp("Specs.Reporters/include/*", package:installdir())

        -- main() entrypoint
        os.cp("Specs.Main/include/*", package:installdir())

        -- DSLs for defining specs
        os.cp("Specs.DSLs/include/*", package:installdir())

        -- Provides <Specs.h> helper header
        os.cp("Specs/include/*", package:installdir())
    end)
