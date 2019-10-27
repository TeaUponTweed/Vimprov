import sublime
import sublime_plugin

def _set_color_scheme(scheme):
    color_schemes = sublime.find_resources("*.sublime-color-scheme")
    for color_scheme in color_schemes:
        if scheme in color_scheme:
            _do_set_color_scheme(color_scheme)
            break
    else:
        raise ValueError('No scheme matching {} found'.format(scheme))

def _do_set_color_scheme(color_scheme_path):
    _load_settings().set('color_scheme', color_scheme_path)
    sublime.save_settings('Preferences.sublime-settings')
    sublime.status_message('SelectColorScheme: ' + color_scheme_path)

def _load_settings():
    return sublime.load_settings('Preferences.sublime-settings')



class EnterVimprovCommand(sublime_plugin.WindowCommand):
    def run(self):
        _set_color_scheme('Stark')
class ExitVimprovCommand(sublime_plugin.WindowCommand):
    def run(self):
        _set_color_scheme('Monokai')
