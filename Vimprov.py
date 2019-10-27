import sublime
import sublime_plugin

class EnterVimproveCommand(sublime_plugin.WindowCommand):
    def run(self):
        sublime.view().run_command("stark")

class ExitVimproveCommand(sublime_plugin.WindowCommand):
    def run(self):
        sublime.view().run_command("unstark")
