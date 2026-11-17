import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from textual.app import App, ComposeResult
from textual.widgets import Header, Button, Static
from textual.containers import Horizontal, Vertical
from textual import events
from textual_tty import Terminal

from FxTermuxTui.shell import build_shell_submenu
from FxTermuxTui.base import build_base_menu
from FxTermuxTui.files import build_files_menu
from FxTermuxTui.Downloads import build_downloads_menu
from FxTermuxTui.web import build_web_menu
from FxTermuxTui.popup import CmdInputScreen


class RamBar(Static):
    def __init__(self, bar_len: int = 12):
        super().__init__("ram: --")
        self.bar_len = bar_len

    def refresh_ram(self):
        try:
            import psutil
            mem = psutil.virtual_memory()
            pct = mem.percent
            used_gb = mem.used / (1024 ** 3)
            total_gb = mem.total / (1024 ** 3)
        except Exception:
            self.update("[red]ram: unavailable[/]")
            return

        fill = int(self.bar_len * pct / 100)
        bar = f"[green]{'█' * fill}[/][dim]{'░' * (self.bar_len - fill)}[/]"
        self.update(f"{bar} {pct:.0f}% {used_gb:.1f}/{total_gb:.1f}g")


class FxTermuxTui(App):
    TITLE = "FxTermuxTui"
    CSS = """
    Horizontal { height: 100%; }
    Vertical#btn_panel {
        width: 22;
        height: 100%;
        background: $surface;
        border: solid $primary;
        padding: 1;
    }
    #ram_top {
        height: auto;
        margin-bottom: 1;
    }
    #menu_container {
        height: 1fr;
    }
    Terminal { width: 1fr; height: 100%; }
    Button { margin: 1; }
    """

    SPEC = {
        "apt": {
            "remove": ("包名", "", "", ""),
            "install": ("包名", "", "", ""),
            "reinstall": ("包名", "", "", ""),
            "show": ("包名", "", "", ""),
            "search": ("关键词", "", "", ""),
            "update": ("", "", "", ""),
            "upgrade": ("", "", "", ""),
            "full-upgrade": ("", "", "", ""),
            "autoremove": ("", "", "", ""),
            "clean": ("", "", "", ""),
            "list": ("", "", "", ""),
        },
        "pkg": {
            "uninstall": ("包名", "", "", ""),
            "install": ("包名", "", "", ""),
            "reinstall": ("包名", "", "", ""),
            "show": ("包名", "", "", ""),
            "search": ("关键词", "", "", ""),
            "update": ("", "", "", ""),
            "upgrade": ("", "", "", ""),
            "full-upgrade": ("", "", "", ""),
            "autoremove": ("", "", "", ""),
            "clean": ("", "", "", ""),
            "autoclean": ("", "", "", ""),
            "list-all": ("", "", "", ""),
            "list-installed": ("", "", "", ""),
        },
        "cargo": {
            "update": ("包名（可选）", "", "", ""),
            "search": ("关键词", "", "", ""),
            "install": ("包名", "", "", ""),
            "uninstall": ("包名", "", "", ""),
        },
        "pip": {
            "install": ("包名", "", "", ""),
            "uninstall": ("包名", "", "", ""),
        },
        "npm": {
            "install": ("包名", "", "", ""),
        },
    }

    def __init__(self):
        super().__init__()
        self.selected_shell = "fish"
        self.menu_state = "main"
        self.ram_widget = RamBar()

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="btn_panel"):
                yield self.ram_widget
                yield Vertical(id="menu_container")
            yield Terminal(command=[self.selected_shell])

    async def on_mount(self) -> None:
        self.show_main_menu()

        async def ram_loop():
            while True:
                self.ram_widget.refresh_ram()
                await asyncio.sleep(2)

        self.run_worker(ram_loop, exclusive=False)

    def get_menu_container(self):
        return self.query_one("#menu_container", Vertical)

    def clear_menu(self):
        c = self.get_menu_container()
        for child in c.children:
            child.remove()

    def show_main_menu(self) -> None:
        self.menu_state = "main"
        self.clear_menu()
        self.get_menu_container().mount(Button("tools", id="tools"))

    def show_tools_menu(self) -> None:
        self.menu_state = "tools"
        self.clear_menu()
        c = self.get_menu_container()
        c.mount(Button("shell", id="shell"))
        c.mount(Button("base", id="base"))
        c.mount(Button("files", id="files"))
        c.mount(Button("web", id="web"))
        c.mount(Button("Downloads", id="Downloads"))
        c.mount(Button("返回", id="back_main"))

    def show_shell_submenu(self) -> None:
        self.menu_state = "shell_sub"
        self.clear_menu()
        build_shell_submenu(self.get_menu_container())

    def show_base_submenu(self) -> None:
        self.menu_state = "base_sub"
        self.clear_menu()
        build_base_menu(self.get_menu_container())

    def show_files_submenu(self) -> None:
        self.menu_state = "files_sub"
        self.clear_menu()
        build_files_menu(self.get_menu_container())

    def show_web_submenu(self) -> None:
        self.menu_state = "web_sub"
        self.clear_menu()
        build_web_menu(self.get_menu_container())

    def show_downloads_submenu(self) -> None:
        self.menu_state = "downloads_sub"
        self.clear_menu()
        build_downloads_menu(self.get_menu_container())

    def switch_shell(self, shell_cmd: str) -> None:
        self.selected_shell = shell_cmd
        old_term = self.query_one(Terminal)
        parent = old_term.parent
        old_term.remove()
        parent.mount(Terminal(command=[shell_cmd]))

    def send_command_to_terminal(self, cmd_line: str) -> None:
        term = self.query_one(Terminal)
        term.focus()
        for ch in cmd_line:
            term.post_message(events.Key(key=ch, character=ch))
        term.post_message(events.Key(key="enter", character="\r"))

    def run_base_cmd(self, cmd_id: str) -> None:
        cfg = {
            "cd": ("输入目标路径", "~/", "", ""),
            "mkdir": ("目录名", "", "附加参数", ""),
            "rm": ("文件/路径", "", "附加参数", ""),
            "rip": ("目标", "", "附加参数", ""),
            "zoxide": ("跳转路径", "", "", ""),
            "ls": ("路径", ".", "附加参数", "-la"),
            "eza": ("路径", ".", "附加参数", "-l"),
            "find": ("起始目录", ".", "搜索条件", ""),
            "clear": ("", "", "", ""),
            "cat": ("文件名", "", "", ""),
            "bat": ("文件名", "", "", ""),
        }
        p1, d1, p2, d2 = cfg[cmd_id]

        def callback(res: tuple[str, str] | None) -> None:
            if res is None:
                return
            v1, v2 = res
            parts = [cmd_id]
            if v1:
                parts.append(v1)
            if v2:
                parts.append(v2)
            self.send_command_to_terminal(" ".join(parts))

        if not p1 and not p2:
            callback(("", ""))
        else:
            self.push_screen(CmdInputScreen(p1, d1, p2, d2), callback)

    def run_downloads_action(self, tool: str, action: str) -> None:
        spec = self.SPEC
        if tool not in spec or action not in spec:
            return
        p1, d1, p2, d2 = spec[tool][action]

        def callback(res: tuple[str, str] | None) -> None:
            if res is None:
                return
            v1, v2 = res
            cmd_parts = [tool, action]
            if v1:
                cmd_parts.append(v1)
            if v2:
                cmd_parts.append(v2)
            self.send_command_to_terminal(" ".join(cmd_parts))

        if not p1 and not p2:
            callback(("", ""))
        else:
            self.push_screen(CmdInputScreen(p1, d1, p2, d2), callback)

    def run_web_browser(self, browser: str) -> None:
        def callback(res: tuple[str, str] | None) -> None:
            if res is None:
                return
            url, _ = res
            url = url.strip()
            if url:
                self.send_command_to_terminal(f"{browser} {url}")

        self.push_screen(CmdInputScreen("输入网址", "https://", "", ""), callback)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid is None:
            return

        if self.menu_state == "main":
            if bid == "tools":
                self.show_tools_menu()

        elif self.menu_state == "tools":
            if bid == "shell":
                self.show_shell_submenu()
            elif bid == "base":
                self.show_base_submenu()
            elif bid == "files":
                self.show_files_submenu()
            elif bid == "web":
                self.show_web_submenu()
            elif bid == "Downloads":
                self.show_downloads_submenu()
            elif bid == "back_main":
                self.show_main_menu()

        elif self.menu_state == "shell_sub":
            if bid in {"bash", "zsh", "fish"}:
                self.switch_shell(bid)
            elif bid == "back_shell":
                self.show_tools_menu()

        elif self.menu_state == "base_sub":
            base_actions = {
                "cd",
                "mkdir",
                "rm",
                "rip",
                "zoxide",
                "ls",
                "eza",
                "find",
                "clear",
                "cat",
                "bat",
            }
            if bid in base_actions:
                self.run_base_cmd(bid)
            elif bid == "back_base":
                self.show_tools_menu()

        elif self.menu_state == "files_sub":
            if bid in {"mc", "nnn", "vifm"}:
                self.send_command_to_terminal(bid)
            elif bid == "back_files":
                self.show_tools_menu()

        elif self.menu_state == "web_sub":
            if bid == "lynx":
                self.run_web_browser("lynx")
            elif bid == "w3m":
                self.run_web_browser("w3m")
            elif bid == "back_web":
                self.show_tools_menu()

        elif self.menu_state == "downloads_sub":
            if bid == "apt":
                self.menu_state = "apt_sub"
                self.clear_menu()
                c = self.get_menu_container()
                for a in self.SPEC["apt"]:
                    c.mount(Button(a, id=a))
                c.mount(Button("返回", id="back_apt"))
            elif bid == "pkg":
                self.menu_state = "pkg_sub"
                self.clear_menu()
                c = self.get_menu_container()
                for a in self.SPEC["pkg"]:
                    c.mount(Button(a, id=a))
                c.mount(Button("返回", id="back_pkg"))
            elif bid == "cargo":
                self.menu_state = "cargo_sub"
                self.clear_menu()
                c = self.get_menu_container()
                for a in self.SPEC["cargo"]:
                    c.mount(Button(a, id=a))
                c.mount(Button("返回", id="back_cargo"))
            elif bid == "pip":
                self.menu_state = "pip_sub"
                self.clear_menu()
                c = self.get_menu_container()
                for a in self.SPEC["pip"]:
                    c.mount(Button(a, id=a))
                c.mount(Button("返回", id="back_pip"))
            elif bid == "npm":
                self.menu_state = "npm_sub"
                self.clear_menu()
                c = self.get_menu_container()
                for a in self.SPEC["npm"]:
                    c.mount(Button(a, id=a))
                c.mount(Button("返回", id="back_npm"))
            elif bid == "back_downloads_root":
                self.show_tools_menu()

        elif self.menu_state == "apt_sub":
            if bid in self.SPEC["apt"]:
                self.run_downloads_action("apt", bid)
            elif bid == "back_apt":
                self.show_downloads_submenu()

        elif self.menu_state == "pkg_sub":
            if bid in self.SPEC["pkg"]:
                self.run_downloads_action("pkg", bid)
            elif bid == "back_pkg":
                self.show_downloads_submenu()

        elif self.menu_state == "cargo_sub":
            if bid in self.SPEC["cargo"]:
                self.run_downloads_action("cargo", bid)
            elif bid == "back_cargo":
                self.show_downloads_submenu()

        elif self.menu_state == "pip_sub":
            if bid in self.SPEC["pip"]:
                self.run_downloads_action("pip", bid)
            elif bid == "back_pip":
                self.show_downloads_submenu()

        elif self.menu_state == "npm_sub":
            if bid in self.SPEC["npm"]:
                self.run_downloads_action("npm", bid)
            elif bid == "back_npm":
                self.show_downloads_submenu()


def main() -> None:
    FxTermuxTui().run()


if __name__ == "__main__":
    main()

