# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

import configparser

import pytest

from vimiv.config import styles
from vimiv.utils import customtypes


@pytest.fixture(params=(True, False))
def new_style(request):
    """Fixture to create a clean default and clean default-dark style."""
    new_style = styles.create_default(dark=request.param, save_to_file=False)
    yield new_style


@pytest.fixture
def style_file(tmp_path):
    """Fixture to create a style file with different properties."""

    def create_style_file(color="#FFF", font=None, n_colors=16, header=True, **options):
        """Helper function returned to create the styles file.

        Args:
            color: Color written for the 16 base colors.
            font: Font written.
            n_colors: Number of base colors to write.
            header. If False, omit the STYLE section header.
            options: Further style options passed.
        """
        filename = str(tmp_path / "style")
        if not header:
            return filename
        parser = configparser.ConfigParser()
        parser.add_section("STYLE")
        for i in range(n_colors):
            parser["STYLE"][f"base{i:02x}"] = color
        if font is not None:
            parser["STYLE"]["font"] = font
        for key, value in options.items():
            parser["STYLE"][key] = value
        with open(filename, "w", encoding="utf-8") as f:
            parser.write(f)
        return filename

    return create_style_file


def test_add_style_option(new_style):
    new_style["red"] = "#ff0000"
    assert new_style["{red}"] == "#ff0000"


def test_fail_add_non_string_style_option(new_style):
    with pytest.raises(AssertionError, match="must be string"):
        new_style[True] = "#ff0000"


def test_fail_add_non_string_style_value(new_style):
    with pytest.raises(AssertionError, match="must be string"):
        new_style["red"] = 12


def test_replace_referenced_variables(new_style):
    new_style["red"] = "#ff0000"
    new_style["error.fg"] = "{red}"
    assert new_style["{error.fg}"] == "#ff0000"


def test_fail_get_nonexisting_style_option(new_style):
    styles._style = new_style
    assert styles.get("anything") == ""
    styles._style = None


def test_is_color_option():
    assert styles.Style.is_color_option("test.bg")
    assert styles.Style.is_color_option("test.fg")
    assert not styles.Style.is_color_option("test.fga")
    assert not styles.Style.is_color_option("test.f")


def test_check_valid_color():
    # If a check fails, ValueError is raised, so we need no assert statement
    styles.Style.check_valid_color("#ffffff")  # 6 digit hex
    styles.Style.check_valid_color("#FFFFFF")  # 6 digit hex capital
    styles.Style.check_valid_color("#FFfFfF")  # 6 digit hex mixed case
    styles.Style.check_valid_color("#00fFfF")  # 6 digit hex mixed case and number


@pytest.mark.parametrize(
    "color",
    (
        "ffffff",  # Missing leading #
        "#fffffff",  # 7 digits
        "#fffff",  # 5 digits
        "#ffff",  # 4 digits
        "#fff",  # 3 digits
        "#ff",  # 2 digits
        "#f",  # 1 digit
        "#",  # 0 digits
        "#agfjkl",  # invalid content
    ),
)
def test_fail_check_valid_color(color):
    with pytest.raises(ValueError):
        styles.Style.check_valid_color(color)


@pytest.mark.parametrize(
    "expected_color, expected_font, options",
    [
        ("#ffffff", "my new font", {}),
        ("#ffffff", None, {}),
        ("#ffffff", None, {"image.bg": "#FF00FF", "library.font": "other"}),
        ("#ffffff", None, {"image.bg": "invalid", "library.font": "other"}),
    ],
)
def test_read_style(style_file, expected_color, expected_font, options):
    """Check reading a style file retrieves the correct results."""
    path = style_file(color=expected_color, font=expected_font, **options)
    read_style = styles.read(path)
    # Correct 16 base colors
    for i in range(16):
        assert read_style[f"{{base{i:02x}}}"].lower() == expected_color.lower()
    if expected_font is not None:  # Font from styles file if passed
        assert read_style["{font}"].lower() == expected_font.lower()
    else:  # Default font otherwise
        assert read_style["{font}"].lower() == styles.DEFAULT_FONT.lower()
    # Any additional options in the styles file
    default = styles.create_default(save_to_file=False)
    for name, expected_value in options.items():
        key = "{" + name + "}"
        if styles.Style.is_color_option(name):
            try:
                styles.Style.check_valid_color(expected_value)
            except ValueError:
                expected_value = default[key]
        assert read_style[key] == expected_value


def test_read_style_missing_section(style_file):
    """Check reading a style file missing the section header leads to error handling."""
    check_critical_error_handling(style_file(header=False))


@pytest.mark.parametrize("n_colors", range(15))
def test_read_style_missing_color(style_file, n_colors):
    """Check reading a style file missing any base color leads to error handling."""
    check_critical_error_handling(style_file(n_colors=n_colors))


def test_read_style_invalid_base_color(style_file):
    """Check reading a style file with an invalid base color leads to error handling."""
    check_critical_error_handling(style_file(color="invalid"))


def check_critical_error_handling(path):
    """Helper function to check for correct handling of critical errors."""
    with pytest.raises(SystemExit, match=str(customtypes.Exit.err_config)):
        styles.read(path)


@pytest.mark.parametrize("name", ("name", "{name}"))
def test_style_key(name):
    assert styles.Style.key(name) == "{name}"
