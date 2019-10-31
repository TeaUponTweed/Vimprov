import sublime
import sublime_plugin

# helpers for chaning the theme
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
    def __init__(self, repeat=None, verb=None, adjective=None, noun=None):
        self.repeat = repeat
        self.verb = verb
        self.adjective = adjective
        self.noun = noun
        self.record = []

    def process_key(self, key):
        self.record.append(key)
        if not self.has_repeat() and not self.has_verb():
            if not self.maybe_process_repeat(key):
                self.process_verb(key)
        elif self.has_repeat() and not self.has_verb():
            if not self.maybe_process_repeat(key):
                self.process_verb(key)
        elif self.has_verb() and not self.has_adjective():
            self.process_adjective(key)
        elif self.has_adjective():
            self.process_noun(key)
        else:
            raise ValueError('We should not be here')
        return self.fully_formed()

    def maybe_process_repeat(self, key):
        print('maybe_process_repeat', key)
        if key not in NUM_KEYS:
            return False
        if self.repeat is None:
            self.repeat = [key]
        else:
            self.repeat += [key]
        return True

    def process_verb(self, key):
        print('process_verb', key)
        # g - go
        # d - delete
        # s - select
        if key in 'gds':
            self.verb = key
        elif key in MOVE_KEYS:
            self.verb = 'g'
            self.noun = key
            self.adjective = key
        else:
            raise ValueError('{} is not a valid verb'.format(key))

    def process_adjective(self, key):
        print('process_adjective', key)
        # TODO maybe steal from https://github.com/philippotto/Sublime-MultiEditUtils/blob/master/MultiEditUtils.py
        if key in MOVE_KEYS:#'sSwWlLfFhH':
            self.adjective = key
            self.noun = key
        elif key in 'tTuUhHcC':
            self.adjective = key
        else:
            raise ValueError('Cannot use {} as an adjective'.format(key))

    def process_noun(self, key):
        print('process_noun', key)
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

    def __repr__(self):
        return '{} {} {}'.  format(self.verb if self.verb else '', self.adjective if self.adjective else '', self.noun if self.noun else '')

    def __str__(self):
        return self.__repr__()


def do_toggle_vimprov(view):
    settings = view.settings()
    vimprov = not settings.get('vimprov', False)
    settings.set('vimprov', vimprov)
    settings.set('command_mode', vimprov)
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
        view.run_command('move', {'by': 'characters', 'forward': False, 'extend': extend})
    elif key == 'j':
        view.run_command('move', {'by': 'lines', 'forward': True, 'extend': extend})
    elif key == 'k':
        view.run_command('move', {'by': 'lines', 'forward': False, 'extend': extend})
    elif key == 'l':
        view.run_command('move', {'by': 'characters', 'forward': True, 'extend': extend})
    # regions
    elif key == 'w':
        view.run_command('move', {'by': 'words', 'forward': True, 'extend': extend})
    elif key == 'W':
        view.run_command('move', {'by': 'words', 'forward': False, 'extend': extend})
    elif key == 'p':
        view.run_command('move', {'by': 'subwords', 'forward': True, 'extend': extend})
    elif key == 'P':
        view.run_command('move', {'by': 'subwords', 'forward': False, 'extend': extend})
    elif key == 'e':
        view.run_command('move_to', {'to': 'eol', 'extend': extend})
    elif key == 'E':
        view.run_command('move_to', {'to': 'bol', 'extend': extend})
    elif key == 'f':
        view.run_command('move_to', {'to': 'eof', 'extend': extend})
    elif key == 'F':
        view.run_command('move_to', {'to': 'bof', 'extend': extend})


def do_move_in_the_weeds(view, til, forward, extend, include_char, erase=False, edit=None):
    new_regions = []
    for sel in view.sel():
        row, col = view.rowcol(sel.a)
        line = view.substr(view.line(view.text_point(row, 0)))
        left = line[:col]
        right = line[col:]
        if forward:
            delta = right.find(til)
        else:
            delta = left.rfind(til)
            delta = len(left) - delta


        delta = max(delta, 0)
        print('------')
        print(left)
        print(right)
        print(row, col, delta)
        print('------')
        if delta == -1 or delta == 0:
            if extend:
                region = sublime.Region(sel.a, sel.a)
            else:
                region = sublime.Region(sel.a, sel.a)
        else:
            if include_char and forward:
                delta += 1
            if not include_char and not forward:
                delta -= 1

            if extend:
                if forward:
                    region = sublime.Region(sel.a, sel.b+delta)
                else:
                    region = sublime.Region(sel.a-delta, sel.b)
            else:
                if forward:
                    region = sublime.Region(sel.a+delta, sel.a+delta)
                else:
                    region = sublime.Region(sel.a-delta, sel.a-delta)
        new_regions.append(region)

    view.sel().clear()
    for region in new_regions:
        view.sel().add(region)
    if erase:
        assert edit is not None
        for sel in view.sel():
            if not sel.empty():
                view.erase(edit, sublime.Region(sel.a, sel.b))

def transform_action(action, view, edit):
    print('transform_action', action.verb, action.adjective, action.noun)
    if action.verb == 'i':
        do_toggle_vimprov(view)

    def doit():
        assert action.verb in 'gsd'
        extend = action.verb in 'sd'
        forward = action.adjective in 'tu'
        include_char = action.adjective in 'tC'
        erase = action.verb == 'd'

        if action.adjective in MOVE_KEYS:
            do_move(action.adjective, view, extend=extend)
        elif action.adjective in 'tT':
            do_move_in_the_weeds(view=view, til=action.noun, forward=forward, extend=extend, include_char=include_char, edit=edit, erase=erase)
        elif action.adjective in 'uU':
            do_move_in_the_weeds(view=view, til=action.noun, forward=forward, extend=extend, include_char=include_char, edit=edit, erase=erase)
        elif action.adjective in 'cC':
            if not extend:
                print('contained implies extend')
            if action.noun in '()':
                left_char = '('
                right_char = ')'
            elif action.noun in '<>':
                left_char = '<'
                right_char = '>'
            elif action.noun in '[]':
                left_char = '['
                right_char = ']'
            elif action.noun in '{}':
                left_char = '{'
                right_char = '}'
            else:
                left_char = right_char = action.noun

            do_move_in_the_weeds(view=view, til=right_char, forward=True, extend=True, include_char=include_char, edit=edit, erase=erase)
            do_move_in_the_weeds(view=view, til=left_char, forward=False, extend=True, include_char=include_char, edit=edit, erase=erase)
        else:
            print('{} is not a valid adjective'.format(action.adjective))

    if action.repeat is None:
        repeat = 1
    else:
        repeat = int(''.join(action.repeat))

    for _ in range(repeat):
        doit()



class ProcessVimprovArg(sublime_plugin.TextCommand):
    def run(self, edit, key):
        view = self.view
        print('handle key', key)

        # special handling for insert
        if key == 'i':
            do_toggle_vimprov(view)
            return
        # special handling for repeat
        if key == '.':
            if VimpovAction.last_action is not None:
                transform_action(VimpovAction.last_action, view, edit)
            return

        # TODO
        # * clear selection for verb x
        # * dd to delete selection
        # * why doesn't undo work?

        # # special handling for undo
        # if key == 'u':
        #     view.run_command('undo')
        #     return
        # # special handling for redo
        # if key == 'U':
        #     view.run_command('redo')
        #     return

        # process regular keys
        settings = view.settings()
        view.set_status('_vimprov', '--- Vimprov: ' + ''.join(VimpovAction.current_action.record) + ' ---' )
        try:
            VimpovAction.current_action.process_key(key)
        except ValueError as e:
            print('Vimprov error:', e)
            VimpovAction.current_action = VimpovAction()
        else:
            print(VimpovAction.current_action.fully_formed())
            if VimpovAction.current_action.fully_formed():
                transform_action(VimpovAction.current_action, view, edit)
                VimpovAction.last_action = VimpovAction(
                    repeat=VimpovAction.current_action.repeat,
                    noun=VimpovAction.current_action.noun,
                    adjective=VimpovAction.current_action.adjective,
                    verb=VimpovAction.current_action.verb,
                )
                VimpovAction.current_action = VimpovAction()


class ToggleVimprovCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        do_toggle_vimprov(self.view)
