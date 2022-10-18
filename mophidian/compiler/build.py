import os
import shutil
from typing import Any
import markdown
from pathlib import Path

from .setup import init_static, find_pages, find_content, get_components, get_layouts
from .pages import Page
from config import Config
from jinja2 import Environment, Template


class Build:
    def __init__(self):
        self.config = Config()
        self.pages = find_pages()
        self.content = find_content()
        self.components = get_components()
        self.layouts = get_layouts()
        self.slugs = []

        self.params = {
            "site": self.config.site,
            "components": self.components,
            "layouts": self.layouts,
        }

    # TODO: Handle updating the information and rebuilding when [slug] or [...slug] is added or moved
    def remove_page(self, path: Path):
        if path.name.replace(path.suffix, "") not in ['[slug]', "[...slug]"]:
            del self.pages[Page.build_uri(path)]
        else:
            removed_page = Page(path.parent.as_posix(), path.name, path.suffix)
            if removed_page.name == "[slug]":
                for file in Path('site/' + removed_page.parent).glob("./*.html"):
                    os.remove(file)
            else:
                shutil.rmtree('site/' + removed_page.parent, ignore_errors=True)

    def add_page(self, path: Path):
        new_page = Page(path.parent.as_posix(), path.name, path.suffix)
        self.pages.append(new_page)
        if path.name.replace(path.suffix, "") not in ['[slug]', "[...slug]"]:
            self.generate_page(new_page)
        else:
            self.generate_content(new_page)

    def remove_content(self, path: Path):
        del self.content[Page.build_uri(path)]

    def add_content(self, path: Path):
        new_content = Page(path.parent.as_posix(), path.name, path.suffix)
        self.content.append(new_content)

        best_match_slug = None
        for slug in self.slugs:
            if slug.parent in new_content.parent:
                if best_match_slug is None or len(slug.parent) > len(best_match_slug.parent):
                    best_match_slug = slug

        if best_match_slug is not None:
            self.generate_markdown(new_content, best_match_slug.template)

    def generate_markdown(self, page: Page, template: Template = None):
        extensions = self.config.markdown.extensions if self.config.markdown else []
        extension_configs: Any = (
            self.config.markdown.extension_configs if self.config.markdown else []
        )

        md = markdown.Markdown(extensions=extensions, extension_configs=extension_configs)
        content = md.reset().convert(page.content)

        if template is None:
            if page.meta != {} and "layout" in page.meta and page.meta["layout"].strip() != "":
                layout = self.layouts[page.meta["layout"]]
            else:
                layout = self.layouts["moph_base"]
        else:
            layout = template

        path = "site/" + page.uri
        Path(path).mkdir(parents=True, exist_ok=True)
        with open(path + "/index.html", "+w", encoding="utf-8") as page_file:
            page_file.write(layout.render(**self.params, meta=page.meta, content=content))

    def generate_html(self, page: Page):
        path = "site/" + page.uri
        Path(path).mkdir(parents=True, exist_ok=True)
        with open(path + "/index.html", "+w", encoding="utf-8") as page_file:
            page_file.write(page.template.render(**self.params, meta=page.meta))

    def generate_page(self, page: Page):
        if page.ext == ".md":
            self.generate_markdown(page)
        else:
            self.generate_html(page)

    def generate_content(self, page: Page):
        environment = Environment()
        with open(page.full_path, "r", encoding="utf-8") as slug_file:
            slug = environment.from_string(slug_file.read())

        if slug is not None:
            if page.name == "[slug]":
                for cpage in self.content:
                    if cpage.parent == page.parent and cpage.ext == ".md":
                        cpage.template = page.template
                        print(cpage.template)
                        self.generate_markdown(cpage, page.template)
            else:
                slugs = [content.uri for content in self.content]
                for cpage in slugs:
                    if page.parent in cpage:
                        self.content[cpage].template = page.template
                        self.generate_markdown(self.content[cpage], page.template)

    def create_pages(self):
        for page in self.pages:
            if page.name not in ["[slug]", "[...slug]"]:
                self.generate_page(page)
            elif page.name in ["[slug]", "[...slug]"] and page.ext == ".html":
                self.slugs.append(page)
                self.generate_content(page)
            else:
                continue

    def full(self):
        init_static()
        self.create_pages()