package("StringFormatting")
    set_kind("library") -- Change this to library
    set_homepage("https://github.com/MrowrLib/StringFormatting.h")
    set_description("A header-only library for string formatting.")
    add_urls("https://github.com/MrowrLib/StringFormatting.h.git")
    on_install(function (package)
        os.cp("include", package:installdir())
    end)
