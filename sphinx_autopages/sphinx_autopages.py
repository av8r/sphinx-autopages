import importlib.util
import os
import re
from ast import literal_eval
from pathlib import Path
from typing import ClassVar

from docutils.frontend import OptionParser
from docutils.nodes import Node
from docutils.parsers.rst import directives
from docutils.utils import new_document
from sphinx.application import Sphinx
from sphinx.directives.other import int_or_nothing
from sphinx.environment import BuildEnvironment
from sphinx.parsers import RSTParser
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective
from sphinx.util.typing import OptionSpec

logger = logging.getLogger(__name__)
# logger.setLevel(logging.LEVEL_NAMES["DEBUG"])

_IDX_MAP = {}

class AutoPages:
    def __init__(self, app: Sphinx) -> None:
        self.app: Sphinx = app
        self.env: BuildEnvironment = app.builder.env

    def autopages(self) -> list[str] | None:
        def get_genfiles(
                from_docs: list[str],
                suffixes: list[str] | None = None,
                all_genfiles: list[str] | None = None
        ) -> list[str] | None:
            if not all_genfiles:
                all_genfiles = []
            for doc in from_docs:
                # XXX - hack
                if doc.startswith("apidocs/"):
                    continue
                if suffixes:
                    # lookup for doc name with suffix in list of suffixes
                    all_docs: list[Path] = list(self.env.srcdir.resolve().glob(f"{doc}.*"))
                    full_docs = [_doc for _doc in all_docs if _doc.suffix in suffixes]
                    assert len(full_docs), f"Can't find {doc} suffix in {suffixes}"
                    if len(full_docs) > 1:
                        logger.warning(f"{doc} > 1 suffix--> {full_docs}, use {full_docs[0]}")
                    full_doc = full_docs[0]
                else:
                    full_doc = doc
                # find our directive and pase it in doc file
                # parse directive ars and split it in fct_helper, *args and **kwargs
                with (open(full_doc) as f):
                    fct_kwargs = {}
                    content = f.read()
                    directive_regex = {
                        ".rst": r"..\s+(?P<directive>autopages)(?P<sep>\s*::\s*)(?P<args>.*)",
                        # TODO fix  REGEX - should not accept end with ```$
                        ".md": r"```{(?P<directive>autopages)(?P<sep>\s*}\s*)(?P<args>.*)",
                    }.get(full_doc.suffix.lower(), ".rst")
                    # match = re.search(directive_regex, content)
                    # https://stackoverflow.com/questions/67387814/multiline-regex-match-retrieving-line-numbers-and-matches/67416775#67416775

                    for match in re.finditer(directive_regex, content):
                        line_num = content[:match.start()].count("\n") + 1

                        fct_args_kwargs = match.group(
                            "args").replace(",", " ").replace("```", "").split()

                        fct_name = fct_args_kwargs.pop(0)
                        fct = getattr(module, fct_name, None)
                        assert fct and callable(fct), f"Error {fct_name} not found or not callable!"
                        # Build generated on their own subdir
                        work_dir = Path(full_doc.parent / f"_{full_doc.stem}_{line_num}")
                        work_dir.mkdir(parents=True, exist_ok=True)
                        # see: https://stackoverflow.com/questions/9305387/string-of-kwargs-to-kwargs
                        fct_args = []
                        fct_kwargs["from_doc"] = doc
                        _have_kwargs = ""
                        for arg in fct_args_kwargs:
                            if "=" not in arg:
                                if not _have_kwargs:
                                    fct_args.append(literal_eval(arg))
                                else:
                                    raise ValueError(f"arg: {arg} after kwargs!")
                            else:
                                _have_kwargs += f"{arg} "
                        # see: https://stackoverflow.com/questions/9305387/string-of-kwargs-to-kwargs
                        fct_kwargs |= {
                            k: literal_eval(v)
                            for k, v in (pair.split("=")
                                         for pair in _have_kwargs.split())
                        }
                        logger.info(f"Running {fct.__name__}({fct_args}, {fct_kwargs})")

                        # push generated files in _IDX
                        if not doc in _IDX_MAP:
                            _IDX_MAP[doc] = {}
                        # _IDX_MAP[doc].append(work_dir.relative_to(self.env.srcdir))
                        _IDX_MAP[doc][work_dir.relative_to(self.env.srcdir)] = []

                        # Run fct_helper from working_directory
                        os.chdir(work_dir)
                        local_genfiles = fct(self.app, *fct_args, **fct_kwargs)
                        if local_genfiles:
                            relative_to_srcdir = work_dir.relative_to(self.env.srcdir)
                            local_genfiles = [str(relative_to_srcdir / f) for f in local_genfiles]
                            all_genfiles.extend(local_genfiles)
                            get_genfiles(
                                from_docs=local_genfiles,
                                suffixes=suffixes,
                                all_genfiles=all_genfiles
                            )
                            _IDX_MAP[doc][work_dir.relative_to(self.env.srcdir)] = local_genfiles
                        else:
                            logger.warning(f"{doc}, {fct.__name__}:{line_num} "
                                           f"does not return a list of created files.")
            return all_genfiles if all_genfiles else None

        # import conf.py
        module_name = "write_page_conf"
        file_path = Path(self.app.confdir / "conf.py")
        assert file_path.is_file()
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # self.env.found_docs : list of docs WITHOUT suffix
        # we'll have to find the suffix and append it
        return get_genfiles(
            from_docs=list(self.env.found_docs),
            suffixes = list(self.app.config.source_suffix),
            all_genfiles=None
        )


# https://www.sphinx-doc.org/en/master/extdev/utils.html#sphinx.util.docutils.SphinxDirective
class AutoPagesDirective(SphinxDirective):
    has_content = True
    required_arguments = 1
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec: ClassVar[OptionSpec] = {
        "maxdepth": int_or_nothing,     # int,
        "name": directives.unchanged,
        "class": directives.class_option,
        "caption": directives.unchanged_required,
        "glob": directives.flag,
        "hidden": directives.flag,
        "includehidden": directives.flag,
        "numbered": int_or_nothing,
        "titlesonly": directives.flag,
        "reversed": directives.flag,
    }

    def run(self) -> list[Node]:
        # logger.warning(f"XXX arguments: {pformat(self.arguments, indent=4)}")
        doc = Path(self.env.docname)
        work_dir = Path(doc.parent / f"_{doc.stem}_{self.lineno}")
        # logger.warning(f"DEBUG: make TOC {self.env.docname} in dir {work_dir}")

        rst = ".. toctree::\n"
        rst += "\n".join([ f"   :{k}: {v}"
            for k, v in {
                "maxdepth": self.options.get("maxdepth", 2),
                "name": self.options.get("name"),
                "class": self.options.get("class"),
                "caption": self.options.get("caption"),
                "glob": "glob" in self.options,
                "hidden": "hidden" in self.options,
                "includehidden": "includehidden" in self.options,
                "numbered": self.options.get("numbered", 0),
                "titlesonly": "titlesonly" in self.options,
                "reversed": "reversed" in self.options,
            }.items() if v
        ])
        rst += "\n\n"
        len_rst = len(rst)

        for file_name in sorted(_IDX_MAP.get(self.env.docname).get(work_dir)):
            f_name = Path(file_name).relative_to(Path(self.env.docname).parent)
            rst += f"   {f_name!s}\n"

        if len(rst) == len_rst:
            logger.warning(f"Something Wrong: index without file: {self.env.docname}")
        # else:
        #     logger.warning(f"DEBUG\n{rst}")
        return self.parse_rst(rst)

    def parse_rst(self, text: str) -> list[Node]:
        parser = RSTParser()
        parser.set_application(self.env.app)

        settings = OptionParser(
            defaults=self.env.settings,
            components=(RSTParser,),
            read_config_files=True,
        ).get_default_values()
        document = new_document("<rst-doc>", settings=settings)
        parser.parse(text, document)
        return document.children


def on_builder_inited(app: Sphinx) -> None:
    # fct = app.config.write_files_callable
    # fct_kwargs = app.config.write_files_callable_kwargs

    # logger.warning("on_builfer_inited")

    w = AutoPages(app=app)
    genfiles = w.autopages()
    if not genfiles:
        return
