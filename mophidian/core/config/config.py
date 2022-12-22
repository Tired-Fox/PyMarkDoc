from __future__ import annotations

from teddecor.decorators import config, TypesDefault


@config
class Markdown:
    """Mophidian.markdown configuration."""

    extensions = TypesDefault(
        list,
        nested_types=[str],
        default=[
            "abbr",
            "admonition",
            "attr_list",
            "def_list",
            "footnotes",
            "md_in_html",
            "tables",
            "toc",
            "wikilinks",
            "codehilite",
            "pymdownx.betterem",
            "pymdownx.caret",
            "pymdownx.details",
            "pymdownx.mark",
            "pymdownx.smartsymbols",
            "pymdownx.superfences",
            "pymdownx.tabbed",
            "pymdownx.tasklist",
            "pymdownx.tilde",
        ],
    )
    """The markdown extensions that are to be used for every markdown file."""

    extension_configs = {
        "footnotes": {
            "BACKLINK_TEXT": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 384 512\" \
class=\"fn-backlink\" style=\"width: .75rem; height: .75rem;\" fill=\"currentColor\"><!--! \
Font Awesome Pro 6.2.0 by @fontawesome - https://fontawesome.com License - \
https://fontawesome.com/license (Commercial License) Copyright 2022 Fonticons, Inc. -->\
<path d=\"M32 448c-17.7 0-32 14.3-32 32s14.3 32 32 32l96 0c53 0 96-43 96-96l0-306.7 73.4 73.4c12.5 \
12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3l-128-128c-12.5-12.5-32.8-12.5-45.3 0l-128 128c-12.5 \
12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L160 109.3 160 416c0 17.7-14.3 32-32 32l-96 0z\"/></svg>"
        },
        "codehilite": {"css_class": "highlight"},
    }
    """The configurations for each markdown extension."""


@config
class Site:
    """Mophidian.site configuration."""

    name = "Mophidian"
    """The name of the site. Defaults to `Mophidian`"""

    version = "1.0"
    """The version of the site `ex`: 0.1 or 1. Defaults to `1.0`"""

    source = "pages/"
    """The directory to use for the source files. This equals the location of the main
    pages. Defaults to `pages/`
    """

    dest = "site/"
    """The directory to put the built files into. Defaults to `site/`"""

    content = "content/"
    """The directory where content files are located. These files are markdown and they are used in
    dynamic routes. Defaults to `content/`
    """

    root = ""
    """Root directory of the website. Used for links. Ex: `https://user.github.io/project/` where
    `project/` is the directory of the website. Defaults to ``
    """


@config
class Build:
    """Mohpidian.build configuration."""

    version_format = "v{}"
    """How the generator should format the version. Defaults to `v{}`"""

    default_layout = "moph_base"
    """The name of the default template to use for markdown files. Defaults to `moph_base`"""

    refresh_delay = 2.0
    """The delay until the live server reloads the browser after a file change is detected.
    Defaults to `2.0`.
    """

    use_root = False
    """Temporary"""


@config
class Integrations:
    tailwind = False
    """Auto use and setup tailwind css with node. Defaults to `False`"""

    sass = False
    """Auto use and setup sass with node. Defaults to `False`"""

    package_manager = "npm"
    """The users prefered package manager. Defaults to `npm`"""


@config
class Nav:
    """Mophidian.nav configuration."""

    directory_url = True
    """Whether to use directory urls. If true then files like `foo.md` will translate to
    `foo/index.html`.
    """


@config(load="./moph.json", save="./moph.json")
class Config:
    """Mophidian configuration."""

    markdown = Markdown
    """Markdown configuration."""

    site = Site
    """Site configuration."""

    build = Build
    """Build configuration."""

    integrations = Integrations
    """Integrations configuration."""

    nav = Nav
    """Navigation configuration."""
