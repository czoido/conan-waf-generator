from conans.model import Generator
from conans import ConanFile


class Waf(Generator):

    @property
    def filename(self):
        return "wafconan.py"

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
        sections.extend(
            ['conan_arch = "{0}"'.format(str(self.settings.get_safe("arch"))),
             'conan_arch_build = "{0}"'.format(str(self.settings.get_safe("arch_build"))),
             'conan_build_type = "{0}"'.format(str(self.settings.get_safe("build_type"))),
             'conan_compiler = "{0}"'.format(str(self.settings.get_safe("compiler"))),
             'conan_compiler_runtime = "{0}"'.format(str(self.settings.get_safe("compiler.runtime"))),
             'conan_compiler_version = "{0}"'.format(str(self.settings.get_safe("compiler.version"))),
             'conan_os = "{0}"'.format(str(self.settings.get_safe("os"))),
             'conan_os_build = "{0}"'.format(str(self.settings.get_safe("os_build")))
             ]
        )
        sections.append("conan = {\n")
        self.deps_build_info.libs = \
            [lib[0:-4] if lib.endswith(".lib") else lib for lib in self.deps_build_info.libs]

        all_flags = template.format(dep="conan", info=self.deps_build_info)
        sections.append(all_flags)

        for config, cpp_info in self.deps_build_info.configs.items():
            all_flags = template.format(dep="conan:" + config, info=cpp_info)
            sections.append(all_flags)

        for dep_name, info in self.deps_build_info.dependencies:
            dep_name = dep_name.replace("-", "_")
            info.libs = [lib[0:-4] if lib.endswith(".lib") else lib for lib in info.libs]
            dep_flags = template.format(dep=dep_name, info=info)
            sections.append(dep_flags)

            for config, cpp_info in info.configs.items():
                all_flags = template.format(
                    dep=dep_name + ":" + config, info=cpp_info)
                sections.append(all_flags)

        sections.append("}\n")
        sections.append("""def conan_configure_libs(ctx):""")
        sections.append("""    ctx.env.CONAN_LIBS = []""")
        #should not inject build info, leave it there until the build helper is ready
        sections.append("""    ctx.env.MSVC_VERSION = conan_compiler_version""")
        sections.append("""    ctx.env.INCLUDES.extend(conan['conan']['CPPPATH'])""")
        sections.append("""    ctx.env.LIBPATH.extend(conan['conan']['LIBPATH'])""")
        sections.append("""    ctx.env.CXXFLAGS.append("/{}".format(conan_compiler_runtime))""")
        sections.append("""    for libname, settings in conan.items():""")
        sections.append("""        if 'CPPPATH' in settings:""")
        sections.append("""            ctx.env["INCLUDES_{}".format(libname)] = settings['CPPPATH']""")
        sections.append("""        if 'LIBPATH' in settings:""")
        sections.append("""            ctx.env["LIBPATH_{}".format(libname)] = settings['LIBPATH']""")
        sections.append("""        if 'LIBS' in settings:""")
        sections.append("""            ctx.env["LIB_{}".format(libname)] = settings['LIBS']""")
        sections.append("""            ctx.env.CONAN_LIBS.append(libname)""")

        return "\n".join(sections)


class WafGeneratorPackage(ConanFile):
    name = "WafGen"
    version = "0.1"
    url = "https://github.com/czoido/conan-waf-generator"
    license = "MIT"
