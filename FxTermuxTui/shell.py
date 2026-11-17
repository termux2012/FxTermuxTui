from textual.widgets import Button
from textual.containers import Vertical


def build_shell_submenu(panel: Vertical):
    for child in panel.children:
        child.remove()
    for name in ("bash", "zsh", "fish"):
        panel.mount(Button(name, id=name))
    panel.mount(Button("返回", id="back_shell"))

