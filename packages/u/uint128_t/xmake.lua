package("uint128_t")
    set_homepage("https://github.com/calccrypto/uint128_t")
    set_description("A header-only, constexpr implementation of a 128-bit unsigned integer type for C++")
    add_urls("https://github.com/MrowrLib/uint128_t.git")

    on_install(function (package)
        os.cp("*.h", package:installdir("include"))
        os.cp("*.include", package:installdir("include"))
        os.cp("*.build", package:installdir("include"))
    end)
