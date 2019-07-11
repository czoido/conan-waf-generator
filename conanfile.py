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

        for dep_name, info in self.deps_build_info.dependencies:
            if dep_name not in self.conanfile.build_requires:
                dep_name = dep_name.replace("-", "_")
                info.libs = self._remove_lib_extension(info.libs)
                dep_flags = template.format(dep=dep_name, info=info)
                sections.append(dep_flags)

        sections.append("}\n")
        sections.append("def configure(ctx):")
        sections.append("    ctx.env.CONAN_LIBS = []")
        sections.append("    for libname, settings in conan.items():")
        sections.append("        if 'CPPPATH' in settings:")
        sections.append("            ctx.env['INCLUDES_{}'.format(libname)] = settings['CPPPATH']")
        sections.append("        if 'LIBPATH' in settings:")
        sections.append("            ctx.env['LIBPATH_{}'.format(libname)] = settings['LIBPATH']")
        sections.append("        if 'LIBS' in settings:")
        sections.append("            ctx.env['LIB_{}'.format(libname)] = settings['LIBS']")
        sections.append("            ctx.env.CONAN_LIBS.append(libname)")
        return "\n".join(sections)


class WafGeneratorPackage(ConanFile):
    name = "WafGen"
    version = "0.1"
    url = "https://github.com/czoido/conan-waf-generator"
    license = "MIT"
