from conans.model import Generator
from conans import ConanFile


class Waf(Generator):

    def _remove_lib_extension(self, libs):
        return [lib[0:-4] if lib.endswith(".lib") else lib for lib in libs]

    @property
    def filename(self):
        return "waf_conan_libs_info.py"

    @property
    def content(self):
        template = ('    "{dep}" : {{\n'
                    '        "CPPPATH"     : {info.include_paths},\n'
                    '        "LIBPATH"     : {info.lib_paths},\n'
                    '        "BINPATH"     : {info.bin_paths},\n'
                    '        "LIBS"        : {info.libs},\n'
                    '        "CPPDEFINES"  : {info.defines},\n'
                    '        "CXXFLAGS"    : {info.cxxflags},\n'
                    '        "CCFLAGS"     : {info.cflags},\n'
                    '        "SHLINKFLAGS" : {info.sharedlinkflags},\n'
                    '        "LINKFLAGS"   : {info.exelinkflags},\n'
                    '    }},\n'
                    '    "{dep}_version" : "{info.version}",\n')

        sections = []

        sections.append("conan = {\n")
        self.deps_build_info.libs = self._remove_lib_extension(
            self.deps_build_info.libs)

        all_flags = template.format(dep="conan", info=self.deps_build_info)
        sections.append(all_flags)

        for config, cpp_info in self.deps_build_info.configs.items():
            all_flags = template.format(dep="conan:" + config, info=cpp_info)
            sections.append(all_flags)

        for dep_name, info in self.deps_build_info.dependencies:
            dep_name = dep_name.replace("-", "_")
            info.libs = self._remove_lib_extension(info.libs)
            dep_flags = template.format(dep=dep_name, info=info)
            sections.append(dep_flags)

            for config, cpp_info in info.configs.items():
                all_flags = template.format(
                    dep=dep_name + ":" + config, info=cpp_info)
                sections.append(all_flags)

        sections.append("}\n")

        template = ('def configure(ctx):\n'
                    '    ctx.env.CONAN_LIBS = []\n'
                    '    ctx.env.INCLUDES.extend(conan[\'conan\'][\'CPPPATH\'])\n'
                    '    ctx.env.LIBPATH.extend(conan[\'conan\'][\'LIBPATH\'])\n'
                    '    for libname, settings in conan.items():\n'
                    '        if \'CPPPATH\' in settings:\n'
                    '            ctx.env["INCLUDES_{}".format(libname)] = settings[\'CPPPATH\']\n'
                    '        if \'LIBPATH\' in settings:\n'
                    '            ctx.env["LIBPATH_{}".format(libname)] = settings[\'LIBPATH\']\n'
                    '        if \'LIBS\' in settings:\n'
                    '            ctx.env["LIB_{}".format(libname)] = settings[\'LIBS\']\n'
                    '            ctx.env.CONAN_LIBS.append(libname)\n'
                    '    if ctx.env.DEST_OS == \'win32\' and ctx.env.CC_NAME == \'msvc\':\n'
                    '        ctx.check_cc(lib=\'user32\', mandatory=True)\n'
                    '        ctx.check_cc(lib=\'comctl32\', mandatory=True)\n'
                    '        ctx.check_cc(lib=\'kernel32\', mandatory=True)\n'
                    '        ctx.check_cc(lib=\'ws2_32\', mandatory=True)\n'
                    '        ctx.check_cc(lib=\'gdi32\', mandatory=True)\n'
                    '        ctx.check_cc(lib=\'Advapi32\', mandatory=True)\n'
                    '        ctx.check_cc(lib=\'Comdlg32\', mandatory=True)\n'
                    '        ctx.env.CONAN_LIBS.extend([\'USER32\', \'COMCTL32\', \'KERNEL32\', \
\'WS2_32\', \'GDI32\', \'ADVAPI32\', \'COMDLG32\'])\n')

        sections.append(template)
        return "\n".join(sections)


class WafGeneratorPackage(ConanFile):
    name = "WafGen"
    version = "0.1"
    url = "https://github.com/czoido/conan-waf-generator"
    license = "MIT"
