import sublime
import sublime_plugin


def _set_color_scheme(scheme, settings=None):
    color_schemes = sublime.find_resources("*.sublime-color-scheme")
    for color_scheme in color_schemes:
        if scheme in color_scheme:
            print(color_scheme)
            _do_set_color_scheme_tmp(color_scheme, settings=settings)
            break
    else:
        raise ValueError('No scheme matching {} found'.format(scheme))


def _do_set_color_scheme_tmp(color_scheme_path, settings):
    if settings is None:
        settings = _load_settings()
    settings.set('color_scheme', color_scheme_path)


def _load_settings():
    return sublime.load_settings('Preferences.sublime-settings')


class EnterVimprovCommand(sublime_plugin.WindowCommand):
    def run(self):
        _set_color_scheme('Stark')


class ExitVimprovCommand(sublime_plugin.WindowCommand):
    def run(self):
        _set_color_scheme('Monokai')


def do_toggle_vimprov(view):
    settings = view.settings()
    vimprov = not settings.get('vimprov', False)
    settings.set('vimprov', vimprov)
    print(sublime.find_resources("*.sublime-color-scheme"))
    if vimprov:
        _set_color_scheme('Stark', settings)
    else:
        _set_color_scheme('Monokai', settings)


class ToggleVimprovCommand(sublime_plugin.WindowCommand):
    def run(self):
        for w in sublime.windows():
                for v in w.views():
                    do_toggle_vimprov(v)
