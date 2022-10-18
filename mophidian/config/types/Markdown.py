from .Base import BaseType
from .util import color, Color, Style, RESET

_defualts = {
    "defaults": True,
    "extensions": [
        "abbr",
        "admonition",
        "attr_list",
        "def_list",
        "footnotes",
        "md_in_html",
        "tables",
        "wikilinks",
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
    "extension_configs": {
        "footnotes": {
            "BACKLINK_TEXT": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 384 512\" class=\"fn-backlink\"><!--! Font Awesome Pro 6.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2022 Fonticons, Inc. --><path d=\"M32 448c-17.7 0-32 14.3-32 32s14.3 32 32 32l96 0c53 0 96-43 96-96l0-306.7 73.4 73.4c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3l-128-128c-12.5-12.5-32.8-12.5-45.3 0l-128 128c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L160 109.3 160 416c0 17.7-14.3 32-32 32l-96 0z\"/></svg>"
        }
    },
}


class Markdown(BaseType):
    """All variables are type checked and validated. The config options are exluded from this."""

    extensions: list[str]
    """List of strings representing what extensions to load"""

    extension_configs: dict[str, dict]
    """List of config options for a given extenstion"""

    def __init__(self, **kwargs) -> None:
        self.extensions = []
        self.extension_configs = {}
        self.defaults = _defualts["defaults"]

        self.errors = {
            "ec_error": "",
            "ec_errors": [],
            "e_error": "",
            "e_errors": [],
            "general": [],
        }

        if "defaults" in kwargs:
            defaults = kwargs["defaults"]
            if isinstance(defaults, bool):
                self.defaults = defaults
            else:
                self.errors["general"].append(
                    '  "append": was of type <'
                    + color(type(defaults).__name__, prefix=[Color.RED])
                    + "> but was expecting <"
                    + color("bool", prefix=[Color.YELLOW])
                    + ">"
                )

        if "extensions" in kwargs:
            extensions: list[str] = kwargs["extensions"]
            if isinstance(extensions, list):
                if self.defaults:
                    self.extensions.extend(_defualts["extensions"])
                for i, extension in enumerate(extensions):
                    if isinstance(extension, str):
                        if extension not in self.extensions:
                            self.extensions.append(extension)
                    else:
                        self.errors["e_errors"].append(
                            color(f'    {extensions[i]}', prefix=[Color.RED])
                            + ":  was of type <"
                            + color(type(extension).__name__, prefix=[Color.RED])
                            + "> but was expecting <"
                            + color("str", prefix=[Color.YELLOW])
                            + ">"
                        )
            else:
                self.errors["e_error"] = (
                    "was of type <"
                    + color(type(extensions).__name__, prefix=[Color.RED])
                    + "> but was expecting <"
                    + color("list", prefix=[Color.YELLOW])
                    + ">"
                )

        if "extension_configs" in kwargs:
            extension_configs: dict[str, dict] = kwargs["extension_configs"]
            if isinstance(extension_configs, dict):
                if self.defaults:
                    self.extension_configs.update(_defualts["extension_configs"])
                for key in extension_configs:
                    if key in self.extensions:
                        if isinstance(extension_configs[key], dict):
                            self.extension_configs.update({key: extension_configs[key]})
                        else:
                            self.errors["ec_errors"].append(
                                f'    "{key}": '
                                + color("value ", prefix=[Color.RED])
                                + "was of type <"
                                + color(
                                    type(extension_configs[key]).__name__,
                                    prefix=[Color.RED],
                                    suffix=[Color.RESET],
                                )
                                + "> but was expecting <"
                                + color("dict", prefix=[Color.YELLOW])
                                + ">"
                            )
                    else:
                        self.errors["ec_errors"].append(
                            f'    "{color(key, prefix=[Color.RED])}": '
                            + "is not a know plugin. Make sure it is installed and declared in "
                            + color("markdown", prefix=[Color.YELLOW])
                            + " > "
                            + color("extensions", prefix=[Color.YELLOW])
                        )
            else:
                self.errors["ec_error"] = (
                    "was of type <"
                    + color(type(kwargs["extension_configs"]).__name__, prefix=[Color.RED])
                    + "> but was expecting <"
                    + color("dict", prefix=[Color.YELLOW])
                    + ">"
                )

    def has_ext_errors(self) -> bool:
        """Determine if there are extension errors.

        Returns:
            bool: True if any
        """
        return self.errors['e_error'] != "" or len(self.errors['e_errors']) > 0

    def has_ext_config_errors(self) -> bool:
        """Determine if there are any extension config errors

        Returns:
            bool: True if any
        """
        return self.errors['ec_error'] != "" or len(self.errors['ec_errors']) > 0

    def has_errors(self) -> bool:
        """Determines if there were errors while parsing the markdown parameters

        Returns:
            bool: True if there are any erros. False if there are none.
        """
        return self.has_ext_errors() or self.has_ext_config_errors()

    def ext_errors(self) -> str:
        if self.has_ext_errors():
            if self.errors['e_error']:
                return (
                    '  "extensions": '
                    + color('value ', prefix=[Color.RED])
                    + self.errors['e_error']
                )
            elif len(self.errors['e_errors']) > 0:
                output = ['  "extensions": [']
                output.append(color("    ...", prefix=[Color.BLUE]))
                output.extend(self.errors["e_errors"])
                return "\n".join(output) + color("\n    ...", prefix=[Color.BLUE]) + "\n  ]"
        return ""

    def ext_config_errors(self) -> str:
        if self.has_ext_config_errors():
            output = ['  "extension_config": {']
            if self.errors['ec_error']:
                output.append(self.errors['ec_error'])
            elif len(self.errors['ec_errors']) > 0:
                output.extend(self.errors["ec_errors"])
            return "\n".join(output) + "\n  }"
        return ""

    def format_errors(self) -> str:
        return color(
            '"markdown": {\n',
            self.ext_errors(),
            ",\n" if self.has_ext_errors() else "",
            self.ext_config_errors(),
            "\n}",
            prefix=[Style.BOLD],
            suffix=[Style.NOBOLD, Color.RESET],
        )