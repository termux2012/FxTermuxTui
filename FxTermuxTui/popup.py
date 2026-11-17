from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label
from textual.containers import Vertical, Horizontal


class CmdInputScreen(ModalScreen[tuple[str, str] | None]):
    CSS = """
    Screen {
        align: center middle;
    }
    Vertical {
        width: 60;
        background: $panel;
        border: solid $primary;
        padding: 1;
    }
    """

    def __init__(
        self,
        prompt1: str,
        default1: str,
        prompt2: str,
        default2: str,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.prompt1 = prompt1
        self.default1 = default1
        self.prompt2 = prompt2
        self.default2 = default2

    def compose(self) -> ComposeResult:
        with Vertical():
            if self.prompt1:
                yield Label(self.prompt1)
                yield Input(value=self.default1, id="i1")
            if self.prompt2:
                yield Label(self.prompt2)
                yield Input(value=self.default2, id="i2")
            with Horizontal():
                yield Button("确定", id="ok")
                yield Button("取消", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok":
            v1 = self.query_one("#i1", Input).value if self.prompt1 else ""
            v2 = self.query_one("#i2", Input).value if self.prompt2 else ""
            self.dismiss((v1, v2))
        else:
            self.dismiss(None)


