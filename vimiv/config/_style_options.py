# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Style dictionary storing default options."""

DEFAULT_OPTIONS = {
    # Image
    "image.bg": "{base00}",
    "image.scrollbar.width": "8px",
    "image.scrollbar.bg": "{image.bg}",
    "image.scrollbar.fg": "{base03}",
    "image.scrollbar.padding": "2px",
    # Library
    "library.font": "{font}",
    "library.fg": "{base06}",
    "library.padding": "2px",
    "library.directory.fg": "{base07}",
    "library.even.bg": "{base01}",
    "library.odd.bg": "{base01}",
    "library.selected.bg": "{base0d}",
    "library.selected.fg": "{base07}",
    "library.search.highlighted.fg": "{base01}",
    "library.search.highlighted.bg": "{base04}",
    "library.scrollbar.width": "{image.scrollbar.width}",
    "library.scrollbar.bg": "{image.bg}",
    "library.scrollbar.fg": "{image.scrollbar.fg}",
    "library.scrollbar.padding": "{image.scrollbar.padding}",
    "library.border": "0px solid",
    # Statusbar
    "statusbar.font": "{font}",
    "statusbar.bg": "{base02}",
    "statusbar.fg": "{base06}",
    "statusbar.error": "{base08}",
    "statusbar.warning": "{base09}",
    "statusbar.info": "{base0c}",
    "statusbar.message_border": "2px solid",
    "statusbar.padding": "4",
    # Thumbnail
    "thumbnail.font": "{font}",
    "thumbnail.fg": "{library.fg}",
    "thumbnail.bg": "{image.bg}",
    "thumbnail.padding": "20",
    "thumbnail.selected.bg": "{library.selected.bg}",
    "thumbnail.search.highlighted.bg": "{library.search.highlighted.bg}",
    "thumbnail.default.bg": "{statusbar.info}",
    "thumbnail.error.bg": "{statusbar.error}",
    "thumbnail.frame.fg": "{thumbnail.fg}",
    # Completion
    "completion.height": "16em",
    "completion.fg": "{statusbar.fg}",
    "completion.even.bg": "{statusbar.bg}",
    "completion.odd.bg": "{statusbar.bg}",
    "completion.selected.fg": "{library.selected.fg}",
    "completion.selected.bg": "{library.selected.bg}",
    # Keyhint
    "keyhint.padding": "2px",
    "keyhint.border_radius": "10px",
    "keyhint.suffix_color": "{base0c}",
    # Manipulate
    "manipulate.fg": "{statusbar.fg}",
    "manipulate.focused.fg": "{base0c}",
    "manipulate.bg": "{image.bg}",
    "manipulate.slider.left": "{library.selected.bg}",
    "manipulate.slider.handle": "{base04}",
    "manipulate.slider.right": "{statusbar.bg}",
    # Manipulate image overlay
    "manipulate.image.border": "2px solid",
    "manipulate.image.border.color": "{base0c}",
    # Mark
    "mark.color": "{base0e}",
    # Keybindings popup
    "keybindings.bindings.color": "{keyhint.suffix_color}",
    "keybindings.highlight.color": "{mark.color}",
    # Metadata overlay
    "metadata.padding": "{keyhint.padding}",
    "metadata.border_radius": "{keyhint.border_radius}",
}
