import sublime
import sublime_plugin


def _get_path_to_scheme(scheme):
    color_schemes = sublime.find_resources("*.sublime-color-scheme")
    for color_scheme in color_schemes:
        if scheme in color_scheme:
            return color_scheme
    else:
        raise ValueError('No scheme matching {} found'.format(scheme))

def _set_color_scheme(scheme, settings=None):
    scheme = _get_path_to_scheme(scheme)
    _do_set_color_scheme_tmp(scheme, settings=settings)

def _do_set_color_scheme_tmp(color_scheme_path, settings):
    if settings is None:
        settings = _load_settings()
    settings.set('color_scheme', color_scheme_path)


def _load_settings():
    return sublime.load_settings('Preferences.sublime-settings')


class EnterVimprovCommand(sublime_plugin.WindowCommand):
    def run(self):
        pass
        # _set_color_scheme('Stark')


class ExitVimprovCommand(sublime_plugin.WindowCommand):
    def run(self):
        pass
        # _set_color_scheme('Monokai')



def do_toggle_vimprov(view):
    settings = view.settings()
    vimprov = not settings.get('vimprov', False)
    settings.set('vimprov', vimprov)
    if vimprov:
        stark_color_theme_loc = settings.get('vimprov_stark_them')
        if stark_color_theme_loc is None:
            stark_color_theme_loc = _get_path_to_scheme('Stark')
            settings.set('vimprov_stark_them', stark_color_theme_loc)

        prev_theme = settings.get('color_scheme')

        print(prev_theme, '~>', stark_color_theme_loc)

        settings.set('vimprov_prev_theme', prev_theme)

        _do_set_color_scheme_tmp(stark_color_theme_loc, settings)

    else:
        stark_color_theme_loc = settings.get('vimprov_stark_them')
        assert stark_color_theme_loc is not None

        prev_theme = settings.get('vimprov_prev_theme')
        assert prev_theme is not None

        print(stark_color_theme_loc, '~>', prev_theme)

        _do_set_color_scheme_tmp(prev_theme, settings)


class ToggleVimprovCommand(sublime_plugin.WindowCommand):
    def run(self):
        for w in sublime.windows():
                for v in w.views():
                    do_toggle_vimprov(v)
