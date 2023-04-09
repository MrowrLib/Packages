package("StringFormatting")
    set_kind("library") -- Change this to library
    set_homepage("https://github.com/MrowrLib/StringFormatting.h")
    set_description("A header-only library for string formatting.")
    add_urls("https://github.com/MrowrLib/StringFormatting.h.git")
    on_install(function (package)
        os.cp("include", package:installdir())
    end)
    on_test(function (package) -- Add this on_test function
        local configs = {}
        if package:config("use_fmt") then
            configs.use_fmt = true
        end
        assert(package:check_cxxsnippets({configs = configs, test = [=[#include <StringFormatting/StringFormatting.h>
#include <iostream>
int main() {
    std::cout << string_format("Hello {}!", "World") << std::endl;
}
]=]}))
    end)