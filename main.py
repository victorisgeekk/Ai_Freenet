from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, RichLog
from textual.containers import Container, Horizontal
import subprocess
import threading

class AutonomousNetworkApp(App):
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
    #exit-btn {
        background: #da3633;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield RichLog(id="log-view", highlight=True, markup=True)
        with Horizontal():
            yield Button("Run Agent", id="run-btn", variant="success")
            yield Button("Clear Logs", id="clear-btn", variant="primary")
            yield Button("Exit", id="exit-btn", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        log = self.query_one(RichLog)
        log.write("[green][*] Autonomous Network Suite (TUI Mode) Initialized.[/green]")
        log.write("[yellow][*] Ready to execute agent.py with Ollama backend...[/yellow]\n")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        log = self.query_one(RichLog)

        if button_id == "run-btn":
            log.write("[cyan][*] Executing agent.py in background...[/cyan]")
            threading.Thread(target=self.run_agent_script, args=(log,), daemon=True).start()
        elif button_id == "clear-btn":
            log.clear()
            log.write("[green]Logs cleared.[/green]")
        elif button_id == "exit-btn":
            self.exit()

    def run_agent_script(self, log):
        try:
            process = subprocess.Popen(
                ['python', 'agent.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            
            if stdout:
                log.write(stdout)
            if stderr:
                log.write(f"[red][Error] {stderr}[/red]")
        except Exception as e:
            log.write(f"[red][Exception] {str(e)}[/red]")

if __name__ == "__main__":
    app = AutonomousNetworkApp()
    app.run()

