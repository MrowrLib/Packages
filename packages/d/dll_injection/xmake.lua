package("dll_injection")
    set_homepage("https://github.com/MrowrLib/dll_injection.cpp")
    set_description("A header-only library for easily injecting .dll's into running Windows processes.")
    add_urls("https://github.com/MrowrLib/dll_injection.cpp.git")
    add_deps("_Log_")
    on_install(function (package)
        os.cp("include", package:installdir())
    end)
