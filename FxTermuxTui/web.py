from textual.widgets import Button
from textual.containers import Vertical


def build_web_menu(panel: Vertical) -> None:
    for child in panel.children:
        child.remove()
    panel.mount(Button("lynx", id="lynx"))
    panel.mount(Button("w3m", id="w3m"))
    panel.mount(Button("返回", id="back_web"))

