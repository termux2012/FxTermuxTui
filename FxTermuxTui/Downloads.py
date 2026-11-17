from textual.widgets import Button
from textual.containers import Vertical


def build_downloads_menu(panel: Vertical):
    for child in panel.children:
        child.remove()
    items = [
        ("cargo", "cargo"),
        ("npm", "npm"),
        ("pip", "pip"),
        ("pkg", "pkg"),
        ("apt", "apt"),
    ]
    for label, cmd_id in items:
        panel.mount(Button(label, id=cmd_id))
    panel.mount(Button("返回", id="back_downloads_root"))

