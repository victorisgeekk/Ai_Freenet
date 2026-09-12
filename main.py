import sys
import subprocess
import threading
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, RichLog
from textual.containers import Horizontal
from textual.binding import Binding

class AutonomousNetworkApp(App):
    BINDINGS = [
        Binding("r", "run_agent", "Run Agent (R)"),
        Binding("c", "clear_logs", "Clear Logs (C)"),
        Binding("q", "quit_app", "Exit (Q)"),
    ]

    CSS = """
    Screen {
        background: #0d1117;
    }
    #log-view {
        background: #050505;
        color: #00ff00;
        border: solid #00ff00;
        height: 1fr;
        margin: 1;
    }
    Horizontal {
        height: auto;
        align: center middle;
        dock: bottom;
    }
    Button {
        margin: 1 2;
        background: #238636;
        color: #ffffff;
    }
    Button:focus {
        border: double #ffffff;
        background: #2ea043;
    }
    #exit-btn {
        background: #da3633;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield RichLog(id="log-view", highlight=True, markup=True)
        with Horizontal():
            yield Button("Run Agent (R)", id="run-btn", variant="success")
            yield Button("Clear Logs (C)", id="clear-btn", variant="primary")
            yield Button("Exit (Q)", id="exit-btn", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        log = self.query_one(RichLog)
        log.write("[green][*] Autonomous Network Suite (TUI Mode) Initialized.[/green]")
        log.write("[yellow][*] Ready to execute agent.py with Ollama backend...[/yellow]\n")
        log.write("[dim]Shortcuts: Press 'R' to Run | 'C' to Clear | 'Q' to Exit | Enter on Focused Button[/dim]\n")
        self.query_one("#run-btn", Button).focus()

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
        log.write("[cyan][*] Executing agent.py in background...[/cyan]")
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

