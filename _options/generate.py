from optutil import Config
import os
import re

un_whitespace = re.compile(r"[\s_]+")
first_word_re = re.compile("^(\w+)", re.I)

PRELUDE = """
.. This page has been automatically generated by `_options/generate.py`!

%(title)s Options
------------------------------------------------------------------------

""".strip()



def render_rst(config):
    output = [PRELUDE % vars(config)]
    write = output.append

    for section in config.sections:
        write("")
        write("%s" % section.name)
        write("^" * len(section.name))
        write("")
        if section.docs:
            write(u".. seealso::")
            write(u"")
            for doc in section.docs:
                write(u"   :doc:`%s`" % doc)
            write("")

        write(".. list-table::")
        write("   :header-rows: 1")
        write("   ")
        write("   * - Option")
        write("     - Argument")
        write("     - Description")
        write("     - Docs")
        
        for opt in section.options:
            write("   * - %s" % ", ".join("``%s``" % name for name in opt.names))
            write("     - %s" % opt.get_argument())
            write("     - %s" % opt.get_description())
            if opt.docs:
                write("     - %s" % ", ".join(u":doc:`%s`" % topic for topic in opt.docs))
            else:
                write("     - \\")

    return output

def write_output(output, filename):
    target_file = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", filename))
    with file(target_file, "wb") as out_file:
        out_file.write("\n".join(output).encode("UTF-8"))

def main():
    import optdefs
    funcs = [(c, f) for (c, f) in [(c, getattr(optdefs, c)) for c in dir(optdefs) if c.endswith("_options")] if callable(f)]
    funcs.sort(key = lambda (c, f): ((-9000, None) if c.startswith("core_") else (0, c))) # Shunt core options up top, use alpha otherwise

    filenames = []
    for funcname, func in funcs:
        print "Calling %r..." % funcname,
        config = func()
        filename = "Options%s.rst" % un_whitespace.sub("", first_word_re.search(config.title).group(1)).title()
        rst_lines = render_rst(config)
        print "Writing %s..." % filename
        write_output(rst_lines, filename)
        filenames.append(filename)



    print "Writing meta-options..."

    meta_content = ["""
.. This page has been automatically generated by `_options/generate.py`!

Configuration Options
=====================

uWSGI and the various plugins it consists of is almost infinitely configurable.

You can peruse the options page for each plugin, or scroll a little further down for an exhaustive and exhausting list of all options.


.. toctree::
   :maxdepth: 1

""",

"\n".join("   %s" % filename.split(".")[0] for filename in filenames),

"""

Take a deep breath and don't panic -- the list below is long.

"""] + [".. include:: %s" % filename for filename in filenames]
    write_output(meta_content, "Options.rst")


if __name__ == '__main__':
    main()