# Vimprov

## Overview
An unreasonably opinionated attempt to merge the expressiveness of vim with the multi-cursor paradigm of sublime.

This aims to ease a few personal qualms that another vim newbie could presumably run into:
* Makes it very obvious that you are not in insert mode (changes the entire color palette)
* Insert mode behaves *exactly* like vanilla sublime
* No visual mode to confuse things
* Inversion of commands is easy (usually the caps version)

## Commands
### Special Command
* alt+space - toggle vimprov
* i - Enter insert mode
* . - Repeat last valid command

### Actions
* g - go, cursor movement
* d - delete, delete text
* s - select, extend selection

### Regions
#### Basic movement
* h - move left
* j - move down
* k - move up
* l - move right

#### Regions with a defined scope
* p - partial word - next partial word
* w - word  - next white space
* e - end   - end of line
* f - file  - end of file

#### Regions defined by a character
* t - 'til   - go to next <character> inclusive
* u - until - next <character> 
* c - contained - bounded by <character> - handles brackets (){}<>[]
* C - Contained - bounded by <character> inclusive - handles brackets (){}<>[]

## Next Steps
* Get undo/redo working
* Add commands for dealing with current selection, e.g. cut
* Improve robustness (especially redo command and contained)
