import importlib.util
import os
import re
import shelve
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


class AutoPages:
    def __init__(self, app: Sphinx) -> None:
        self.module = None
        self.app: Sphinx = app
        self.env: BuildEnvironment = app.builder.env
        self._excludes : list = []

        self.autopages_map_docs = shelve.open(  # noqa: SIM115
            self.app.env.config.autopages_map_docs,
            flag="c",
            writeback=True
        )


    def _get_genfiles(
            self,
            from_docs: list[str],
            suffixes: list[str] | None = None,
    ) -> list[str] | None:
        for doc in from_docs:
            # skip exclude
            for _exclude in self._excludes:
                if doc.startswith(_exclude):
                    continue
            if suffixes:
                # lookup for doc name with suffix in list of suffixes
                full_docs: list[Path] =[
                    Path(self.env.srcdir.resolve() / f"{doc}{suffix}")
                    for suffix in suffixes
                    if Path(self.env.srcdir.resolve() / f"{doc}{suffix}").is_file()
                ]
                assert full_docs, f"Can't find {doc} suffix in {suffixes}"
                assert len(full_docs) == 1, f"{doc} has more then on suffix [{full_docs}]"
            else:
                ###  OK XXX ### full_doc = doc XXX no suffix ???
                full_docs = [Path(doc)]
            # find our directive and pase it in doc file
            # parse directive ars and split it in fct_helper, *args and **kwargs
            ###  OK XXX ### with (open(full_doc) as f):
            for full_doc in full_docs:
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

                        # XXX KO my_args="a, b"
                        # fct_args_kwargs = match.group(
                        #     "args").replace(",", " ").replace("```", "").split()
                        fct_args_kwargs = match.group(
                            "args").replace("```", "").split()

                        fct_name = fct_args_kwargs.pop(0)
                        fct = getattr(self.module, fct_name, None)
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

                        # push generated files in shelve: autopages_map_docs
                        if doc not in self.autopages_map_docs:
                            self.autopages_map_docs[doc] = {}
                        self.autopages_map_docs[doc][work_dir.relative_to(self.env.srcdir)] = []

                        # Run fct_helper from working_directory
                        os.chdir(work_dir)
                        local_genfiles = fct(self.app, *fct_args, **fct_kwargs)
                        if local_genfiles:
                            relative_to_srcdir = work_dir.relative_to(self.env.srcdir)
                            local_genfiles = [str(relative_to_srcdir / f) for f in local_genfiles]
                            self._get_genfiles(
                                from_docs=local_genfiles,
                                suffixes=suffixes,
                            )
                            self.autopages_map_docs[doc][work_dir.relative_to(self.env.srcdir)] = local_genfiles  # noqa: E501
                        else:
                            logger.warning(f"{doc}, {fct.__name__}:{line_num} "
                                           f"does not return a list of created files.")
                        self.autopages_map_docs.sync()



    def autopages(self) -> list[str] | None:
        # import conf.py
        module_name = "write_page_conf"
        file_path = Path(self.app.confdir / "conf.py")
        assert file_path.is_file()
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

        # self.env.found_docs : list of docs WITHOUT suffix
        if self.app.env.config.autopages_excludes:
            self._excludes = [self.app.env.config.autopages_excludes] \
                if isinstance(self.app.env.config.autopages_excludes, str) \
                else self.app.env.config.autopages_excludes
        # we'll have to find the suffix and append it
        return self._get_genfiles(
            from_docs=list(self.env.found_docs),
            suffixes = list(self.app.config.source_suffix),
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
        autopages_map_docs = shelve.open(  # noqa: SIM115
            self.env.app.env.config.autopages_map_docs,
            flag="r"
        )

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

        for file_name in sorted(
                autopages_map_docs.get(self.env.docname).get(work_dir)
                or []
        ):
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

    app.add_config_value(
        name="autopages_map_docs",
        default=app.doctreedir / "autopages_map_docs.db",
        rebuild="env",
        types=frozenset({Path})
    )

    # cleanup
    on_builder_finished(app=app)

    w = AutoPages(app=app)
    genfiles = w.autopages()
    if not genfiles:
        return


def on_builder_finished(app: Sphinx, exception: Exception | None = None) -> None:
    if app.env.config.autopages_cleanup:
        logger.info("Cleanup..........")
        # logger.warning(app.config.source_suffix)
        with shelve.open(
            app.env.config.autopages_map_docs,
            flag="c",
            # writeback=True
        ) as db:
            if len(db):
                for directive_file in sorted(
                        db,
                        key=lambda i: len(Path(i).parents),
                        reverse=True
                ):
                    for directive_dir in db[directive_file]:
                        for file_to_delete in db[directive_file][directive_dir]:
                            for suffix in app.config.source_suffix:
                                f_to_del = Path(app.srcdir / f"{file_to_delete!s}{suffix}")
                                if f_to_del.is_file():
                                    logger.info(f"removing file: {f_to_del}")
                                    f_to_del.unlink()
                        # logger.warning("===================")
                        # # is_empty = not any(Path('some/path/here').iterdir())
                        # d_to_del = Path(app.srcdir / directive_dir)
                        # if d_to_del.is_dir() and not any(d_to_del.iterdir()):
                        #     logger.info(f"removing dir: {d_to_del}")
                        #     try:
                        #         d_to_del.rmdir()
                        #     except Exception as exc:
                        #         logger.warning(exc, stack_info=True, exc_info=True)

                        # logger.warning(directive_dir)
                        # logger.warning(db[directive_file])
                        # logger.warning(db[directive_file][directive_dir])
                        del db[directive_file][directive_dir]
