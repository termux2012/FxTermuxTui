from textual.widgets import Button
from textual.containers import Vertical


def build_files_menu(panel: Vertical):
    for child in panel.children:
        child.remove()
    for cmd_id in ("mc", "nnn", "vifm"):
        panel.mount(Button(cmd_id, id=cmd_id))
    panel.mount(Button("返回", id="back_files"))

