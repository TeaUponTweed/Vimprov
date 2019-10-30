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


# class StarkCommand(sublime_plugin.WindowCommand):
#     def run(self):
#         print('running stark')
#         _set_color_scheme('Stark')


# class UnstarkCommand(sublime_plugin.WindowCommand):
#     def run(self):
#         _set_color_scheme('Monokai')

NUM_KEYS = '0123456789'
MOVE_KEYS = 'hjklwWpPeEfF'
## elemental movement
# h - move left
# j - move down
# k - move up
# l - move right

## regions
# p - partial word  - next non [a-zA-Z0-9]
# w - word  - next white space
# e - end   - end of line
# f - file  - end of file

## less defined regions
# t - til   - next <character>
# u - until - next <character> inclusive
# h - here  - select word under cursor
# H - here  - select sub word under cursor
# c - contained - bounded by <character> - handles brackets (){}<>
# C - Contained - bounded by <character> inclusive

# Note: caps invert unless otherwise specifed

class VimpovAction(object):
    current_action = None
    last_action = None
    def __init__(self, repeat=None, verb=None, noun=None):
        self.repeat = repeat
        self.verb = verb
        self.noun = noun
        self.record = []

    def process_key(self, key):
        self.record.append(key)
        if not self.has_repeat() and not self.has_repeat():
            if not self.maybe_process_repeat(key):
                self.process_verb(key)
        elif self.has_repeat() and not self.has_verb():
            if not self.maybe_process_repeat(key):
                self.process_verb(key)
        elif self.has_verb():
            self.process_adjective(key)
        elif self.has_adjective():
            self.process_noun(key)
        else:
            raise ValueError('We should not be here')
        return self.fully_formed()

    def maybe_process_repeat(self, key):
        if key not in NUM_KEYS:
            return False
        if self.repeat is None:
            self.repeat = [key]
        else:
            self.repeat += [key]
        return True

    def process_verb(self, key):
        # g - go
        # d - delete
        # s - select
        # i - insert
        if key in 'gds':
            self.verb = key
        elif key in MOVE_KEYS:
            self.verb = 'g'
            self.noun = key
            self.adjective = key
        else:
            raise ValueError('{} is not a valid verb'.format(key))

    def process_adjective(self, key):
        # TODO maybe steal from https://github.com/philippotto/Sublime-MultiEditUtils/blob/master/MultiEditUtils.py
        if key in 'sSwWlLfFhH':
            self.adjective = key
            self.noun = key
        elif key in 'tTuUiI':
            self.adjective = key
        else:
            raise ValueError('Cannot use {} as an adjective'.format(key))

    def process_noun(self, key):
        self.noun = key

    def has_repeat(self):
        return self.repeat is not None

    def has_verb(self):
        return self.verb is not None

    def has_adjective(self):
        return self.adjective is not None

    def has_noun(self):
        return self.noun is not None

    def fully_formed(self):
        return self.has_verb() and self.has_noun() and self.has_adjective()


def do_toggle_vimprov(view):
    settings = view.settings()
    vimprov = not settings.get('vimprov', False)
    settings.set('vimprov', vimprov)
    settings.set('command_mode', vimprov)
    # global current_action
    # global last_action
    VimpovAction.current_action = VimpovAction()
    VimpovAction.last_action = None
    view.set_status('_vimprov', '')

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

def do_move(key, view, extend):
    assert key in MOVE_KEYS
    # elemental
    if key == 'h':
        view.run_command('move', {'by': 'characters', 'forward': False, 'extend': False})
    elif key == 'j':
        view.run_command('move', {'by': 'lines', 'forward': True, 'extend': False})
    elif key == 'k':
        view.run_command('move', {'by': 'lines', 'forward': False, 'extend': False})
    elif key == 'l':
        view.run_command('move', {'by': 'characters', 'forward': True, 'extend': False})
    # regions
    elif key == 'w':
        view.run_command('move', {'by': 'words', 'forward': True, 'extend': False})
    elif key == 'W':
        view.run_command('move', {'by': 'words', 'forward': False, 'extend': False})
    elif key == 'p':
        view.run_command('move', {'by': 'subwords', 'forward': True, 'extend': False})
    elif key == 'P':
        view.run_command('move', {'by': 'subwords', 'forward': False, 'extend': False})
    elif key == 'e':
        view.run_command('move_to', {"to": "eol", "extend": False})
    elif key == 'E':
        view.run_command('move_to', {"to": "bol", "extend": False})
    elif key == 'f':
        view.run_command('move_to', {"to": "eof", "extend": False})
    elif key == 'F':
        view.run_command('move_to', {"to": "bof", "extend": False})
    else:
        return False
    return True


def transform_action(action, view):
    print('transform_action', action.verb, action.adjective, action.noun)
    if action.verb == 'i':
        do_toggle_vimprov(view)

    def doit():
        if action.verb == 'g':
            do_move(action.adjective, view, extend=False)
        elif action.verb == 's':
            if action.adjective in MOVE_KEYS:
                do_move(action.adjective, view, extend=True)
            else:
                pass # TODO
        else:
            pass # TODO

    if action.repeat is None:
        repeat = 1
    else:
        repeat = int(''.join(action.repeat))

    for _ in range(repeat):
        doit()



class ProcessVimprovArg(sublime_plugin.TextCommand):
    def run(self, edit, key):
        view = self.view
        # for sel in view.sel():
        #     for line in view.lines(sel):
        #         row = view.rowcol(line.begin())[0]
        #         print(row)

            # if not region.empty():
            #     # Get the selected text
            #     s = view.substr(region)
            # print(region)
        if key == 'i':
            do_toggle_vimprov(view)

        settings = view.settings()
        print('maybe process', key)
        view.set_status('_vimprov', '--- Vimprov: ' + ''.join(VimpovAction.current_action.record) + ' ---' )
        try:
            VimpovAction.current_action.process_key(key)
        except ValueError as e:
            print('Vimprov error:', e)
            VimpovAction.current_action = VimpovAction()
        else:
            print(VimpovAction.current_action.fully_formed())
            if VimpovAction.current_action.fully_formed():
                transform_action(VimpovAction.current_action, view)
                VimpovAction.last_action = current_action
                VimpovAction.current_action = VimpovAction()

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


