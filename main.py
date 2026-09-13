import sys
import subprocess
import threading
from textual.app import App, ComposeResult
from textual.widgets import Header, Button, RichLog
from textual.containers import Container, Horizontal
from textual.events import Key

class AutonomousNetworkApp(App):
    TITLE = "Ai_Freenet Autonomous Engine"
    SUB_TITLE = "Dev by Victor Geek"

    # Explicit Textual key bindings so single-key shortcuts work even when widgets have focus
    BINDINGS = [
        ("r", "run_agent", "Run"),
        ("c", "clear_logs", "Clear"),
        ("q", "quit_app", "Exit"),
    ]

    # Termux Screen နှင့် ကိုက်ညီမည့် Modern Linux Terminal CSS (Layout Clipping မဖြစ်အောင် ပြင်ဆင်ထားသည်)
    CSS = """
    Screen {
        background: #0d1117;
        layout: vertical;
    }
    Header {
        background: #161b22;
        color: #58a6ff;
        dock: top;
        height: 3;
    }
    #log-container {
        height: 1fr;
        margin: 1 1 0 1;
    }
    #log-view {
        background: #010409;
        color: #3fb950;
        border: solid #30363d;
        height: 100%;
    }
    Horizontal {
        height: 4;
        align: center middle;
        dock: bottom;
        background: #161b22;
        padding: 0 1;
    }
    Button {
        width: 1fr;
        margin: 0 1;
        height: 3;
        border: none;
        text-style: bold;
    }
    #run-btn {
        background: #238636;
        color: #ffffff;
    }
    #run-btn:focus, #run-btn:hover {
        background: #2ea043;
        border: heavy #ffffff;
    }
    #clear-btn {
        background: #1f6beb;
        color: #ffffff;
    }
    #clear-btn:focus, #clear-btn:hover {
        background: #388bfd;
        border: heavy #ffffff;
    }
    #exit-btn {
        background: #da3633;
        color: #ffffff;
    }
    #exit-btn:focus, #exit-btn:hover {
        background: #f85149;
        border: heavy #ffffff;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="log-container"):
            log = RichLog(id="log-view", highlight=True, markup=True)
            log.can_focus = False  # Keyboard Input ကို Log view က ဖမ်းမထားနိုင်အောင် ပိတ်ထားသည်
            yield log
        with Horizontal():
            yield Button("Run (R)", id="run-btn")
            yield Button("Clear (C)", id="clear-btn")
            yield Button("Exit (Q)", id="exit-btn")

    def on_mount(self) -> None:
        log = self.query_one(RichLog)
        log.write("[bold cyan][*] Ai_Freenet Autonomous Engine Initialized.[/bold cyan] [dim](Dev by Victor Geek)[/dim]")
        log.write("[yellow][*] Ready to execute autonomous self-healing agent.py...[/yellow]\n")
        log.write("[dim blue]Controls: Press [R] Run | [C] Clear | [Q] Exit | Tab & Enter fully functional[/dim blue]\n")
        self.query_one("#run-btn", Button).focus()

    # We removed the fragile / truncated on_key docstring handler and rely on BINDINGS

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "run-btn":
            self.action_run_agent()
        elif button_id == "clear-btn":
            self.action_clear_logs()
        elif button_id == "exit-btn":
            self.action_quit_app()

    def action_run_agent(self) -> None:
        log = self.query_one(RichLog)
        log.write("[bold green][*] Executing agent.py in background...[/bold green]")
        threading.Thread(target=self.run_agent_script, daemon=True).start()

    def action_clear_logs(self) -> None:
        log = self.query_one(RichLog)
        log.clear()
        log.write("[green]Logs cleared.[/green]")

    def action_quit_app(self) -> None:
        self.exit()

    def run_agent_script(self) -> None:
        log = self.query_one(RichLog)
        try:
            process = subprocess.Popen(
                [sys.executable, 'agent.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            
            if stdout:
                self.call_from_thread(log.write, stdout)
            if stderr:
                self.call_from_thread(log.write, f"[red]{stderr}[/red]")
        except Exception as e:
            self.call_from_thread(log.write, f"[red][Exception] {str(e)}[/red]")

if __name__ == "__main__":
    app = AutonomousNetworkApp()
    app.run()
