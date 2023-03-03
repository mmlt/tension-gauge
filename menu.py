# def example_menu():
#     t = 0
#
#     def temp():
#         nonlocal t
#         t += 1
#         return t
#
#     sub_menu = Menu(["c", "return"],[show(), leave()])
#     main_menu = Menu(["temp", show(temp), "b", enter(sub_menu)])

#menu, content_fn = func(self, menu_manager)


"""
Menu initially displays item[0] text.

On LEFT/RIGHT_KEY it shows the prev/next item text.

On ENTER_KEY it performs the item action;
  enter a sub menu
  leave the current menu
  show content

When ENTER_KEY is not pressed within N sec it switches back to the last content.
"""


def show(fn):
    def func(menu, menu_manager):
        return menu, fn

    return func


def enter(next_menu):
    def func(menu, menu_manager):
        menu_manager.push(menu)
        return next_menu, None

    return func


def leave():
    def func(menu, menu_manager):
        m = menu_manager.pop()
        return m, None

    return func


LEFT_KEY = 0
RIGHT_KEY = 2
ENTER_KEY = 1


class MenuManager:
    def __init__(self, on_display, menu):
        self._menu = menu
        self._stack = []
        self._on_display = on_display
        menu.enter(self)

    def pop(self):
        return self._stack.pop()

    def push(self, menu):
        self._stack.append(menu)

    def poll10hz(self, event):
        m = self._menu.do(event, self)
        if m != self._menu:
            # menu has changed
            print("Menu changed to:", m)
            m.enter(self)
        self._menu = m

    def display(self, string):
        if self._on_display is not None:
            self._on_display(string)


class BaseMenu:
    def do(self, event, menu_manager: MenuManager) -> 'BaseMenu':  # pep-0484
        """
        Do is called 10 times per second to handle events and update display.
        :param event: key events
        :param menu_manager: manager to display values and push/pop menus
        :return: the current or next menu
        """
        return self

    def enter(self, menu_manager: MenuManager) -> None:
        """
        Enter is called when the menu is entered or re-entered.
        :param menu_manager: manager to display values
        """
        return


class Menu(BaseMenu):
    """
    Menu is a list of text/action items.
    Items are selected with LEFT/RIGHT_KEY and activated with ENTER_KEY.
    """
    def __init__(self, items, actions):
        # list of menu texts to display.
        self._items = items
        # list of actions to perform when a menu item is selected.
        self._actions = actions
        # default menu item
        self._index = 0
        # menu timeout timer
        self._time = 0
        # function that returns current value to display.
        self._content_fn = None

    def do(self, event, menu_manager: MenuManager) -> 'BaseMenu':  # pep-0484
        # print("menu", self._time, self._reset)
        if event is not None and event.pressed:
            if event.key_number == LEFT_KEY or event.key_number == RIGHT_KEY:
                # change menu item
                offset = 1
                if event.key_number == LEFT_KEY:
                    offset = len(self._items) - 1
                self._index = (self._index + offset) % len(self._items)
                self._time = 50
                # display menu text
                menu_manager.display(self._items[self._index])
                return self

            if event.key_number == ENTER_KEY:
                # select menu item
                self._time = 0
                if self._actions[self._index] is not None:
                    menu, self._content_fn = self._actions[self._index](self, menu_manager)
                    return menu

        if self._time > 0:
            self._time -= 1

        if self._time == 0:
            if self._content_fn is not None:
                # display value
                menu_manager.display(self._content_fn())

        return self

    def enter(self, menu_manager: MenuManager):
        menu_manager.display(self._items[self._index])
        return


class Cmd(BaseMenu):
    """
    Cmd is a menu that performs a function, displays the result for 1 second and then returns to the previous menu.
    """
    def __init__(self, func):
        # cmd function to perform
        # fn() -> string
        self._func = func
        self._timeout = 0

    def do(self, event, menu_manager: MenuManager) -> 'BaseMenu':  # pep-0484
        # print("cmd")
        if self._timeout == 0:
            # perform function and display result
            r = self._func()
            menu_manager.display(r)
            self._timeout = 10
        else:
            self._timeout -= 1
            if self._timeout == 0:
                return menu_manager.pop()

        return self
