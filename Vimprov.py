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


class StarkCommand(sublime_plugin.WindowCommand):
    def run(self):
        print('running stark')
        _set_color_scheme('Stark')


class UnstarkCommand(sublime_plugin.WindowCommand):
    def run(self):
        _set_color_scheme('Monokai')



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


# class ToggleVimprovCommand(sublime_plugin.WindowCommand):
#     def run(self):
#         for w in sublime.windows():
#                 for v in w.views():
#                     do_toggle_vimprov(v)
# import time

# class InputStateTracker(sublime_plugin.ViewEventListener):
#     @classmethod
#     def is_applicable(cls, settings):
#         return True
#         # return settings.get('vimprov', False)

#     def on_query_context(self, key, operator, operand, match_all):
#         print('wwoop', key)
#         return True
VIMPROV_BUFFER = []
class ProcessVimprovArg(sublime_plugin.TextCommand):
    def run(self, edit, key):
        view = self.view
        for region in view.sel():
            if not region.empty():
                # Get the selected text
                s = view.substr(region)
                print(s)

        settings = view.settings()
        print('maybe process', key)
        if settings.get('vimprov', False):
            VIMPROV_BUFFER.append(key)
        else:
            view.run_command("insert", {"characters": key})
        if key == 'i':
            do_toggle_vimprov(view)
        if key == 'h':
            view.run_command('move', {'by': 'characters', 'forward': False, 'extend': False})
        if key == 'j':
            view.run_command('move', {'by': 'lines', 'forward': True, 'extend': False})
        if key == 'k':
            view.run_command('move', {'by': 'lines', 'forward': False, 'extend': False})
        if key == 'l':
            view.run_command('move', {'by': 'characters', 'forward': True, 'extend': False})

class VimprovCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        print(view.settings().get('command_mode'))
        do_toggle_vimprov(self.view)
        return
        # print(view)
        # print('ere')
        # return
        settings = view.settings()
        prev_theme = settings.get('color_scheme')
        print('theme', prev_theme)
        if 'Stark' in prev_theme:
            _set_color_scheme('Monokai', settings)
        else:
            _set_color_scheme('Stark', settings)
        # return
        # _set_color_scheme('Stark')
        # print('wakka', settings.get('color_scheme'))
        # def reset_color_scheme():`
        # _do_set_color_scheme_tmp(prev_theme, settings)
        def set_all_windows(window, theme):
            print('this should work', theme)
            for v in window.views():
                _set_color_scheme(theme, v.settings())

        w = self.view.window()
        def back_to_monokai(thing):
            print("Done I guess")
            set_all_windows(w, 'Monokai')


        v = w.show_input_panel(
            ':', '',
            # On Change
            None,
            # On Done
            lambda x: back_to_monokai(x),
            # On Cancel
            None # lambda: back_to_monokai()
        )
        set_all_windows(w, 'Stark')

        # set_all_windows(w, 'Monokai')

        # print('bazinga', v, view)
        # _set_color_scheme('Stark', v.settings())

        # print('ding', v.)
        # v.run_command("stark")

    def on_done(self, x, prev_theme, settings):
        _set_color_scheme('Monokai', settings)

    # def _set_color_scheme(self, color_scheme):

        # print('ere')
        # time.sleep(3)


