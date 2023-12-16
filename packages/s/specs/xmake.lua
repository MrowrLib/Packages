package("specs")
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
        local include_dir = path.join(package:installdir(), "include")

        if not os.isdir(include_dir) then
            os.mkdir(include_dir)
        end

        -- The C++ interfaces
        os.cp("Specs.API/include/*", include_dir)

        -- Support for shared DLLs
        os.cp("Specs.DLL/include/*", include_dir)
        os.cp("Specs.LibraryLoader/include/*", include_dir)

        -- Core implementation classes for main interfaces
        os.cp("Specs.Implementations/include/*", include_dir)

        -- Available Runners and Reporters
        os.cp("Specs.Runners/include/*", include_dir)
        os.cp("Specs.Reporters/include/*", include_dir)

        -- main() entrypoint
        os.cp("Specs.Main/include/*", include_dir)

        -- DSLs for defining specs
        os.cp("Specs.Globals/include/*", include_dir)
        os.cp("Specs.DSLs/include/*", include_dir)

        -- Provides <Specs.h> helper header
        os.cp("Specs/include/*", include_dir)
    end)
