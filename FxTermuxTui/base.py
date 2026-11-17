from textual.widgets import Button
from textual.containers import Vertical


def build_base_menu(panel: Vertical):
    for child in panel.children:
        child.remove()
    cmds = [
        ("cd", "cd"),
        ("mkdir", "mkdir"),
        ("rm", "rm"),
        ("rip", "rip"),
        ("zoxide", "zoxide"),
        ("ls", "ls"),
        ("eza", "eza"),
        ("find", "find"),
        ("clear", "clear"),
        ("cat", "cat"),
        ("bat", "bat"),
    ]
    for label, cmd_id in cmds:
        panel.mount(Button(label, id=cmd_id))
    panel.mount(Button("返回", id="back_base"))

