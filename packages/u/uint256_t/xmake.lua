package("uint256_t")
    set_homepage("https://github.com/calccrypto/uint256_t")
    set_description("A header-only, constexpr implementation of a 256-bit unsigned integer type for C++")
    add_urls("https://github.com/MrowrLib/uint256_t.git")

    add_deps("uint128_t")

    on_install(function (package)
        os.cp("*.h", package:installdir("include"))
        os.cp("*.include", package:installdir("include"))
        os.cp("*.build", package:installdir("include"))
    end)
