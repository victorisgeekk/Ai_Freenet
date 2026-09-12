import sys
import subprocess
import threading
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, RichLog
from textual.containers import Horizontal
from textual.binding import Binding

class AutonomousNetworkApp(App):
    # ၁။ Header Subtitle တွင် Dev by Victor Geek ထည့်သွင်းခြင်း
    TITLE = "Ai_Freenet Autonomous Engine"
    SUB_TITLE = "Dev by Victor Geek"

    # ၂။ မူလ Keyboard Shortcuts (Bindings) များ
    BINDINGS = [
        Binding("r", "run_agent", "Run Agent (R)"),
        Binding("c", "clear_logs", "Clear Logs (C)"),
        Binding("q", "quit_app", "Exit (Q)"),
    ]

    # ၃။ Modern Linux Terminal (Cyberpunk / GitHub Dark CLI) UI Design CSS
    CSS = """
    Screen {
        background: #0d1117;
    }
    Header {
        background: #161b22;
        color: #58a6ff;
        text-style: bold;
    }
    #log-view {
        background: #010409;
        color: #3fb950;
        border: heavy #30363d;
        height: 1fr;
        margin: 1;
        padding: 0 1;
    }
    #log-view:focus {
        border: heavy #58a6ff;
    }
    Horizontal {
        height: auto;
        align: center middle;
        dock: bottom;
        background: #161b22;
        padding: 1;
    }
    Button {
        margin: 0 1;
        background: #21262d;
        color: #c9d1d9;
        border: tall #30363d;
        min-width: 16;
    }
    Button:hover {
        background: #30363d;
    }
    Button:focus {
        border: double #58a6ff;
        color: #ffffff;
        text-style: bold;
    }
    #run-btn {
        background: #238636;
        color: #ffffff;
    }
    #run-btn:hover {
        background: #2ea043;
    }
    #clear-btn {
        background: #1f6beb;
        color: #ffffff;
    }
    #clear-btn:hover {
        background: #388bfd;
    }
    #exit-btn {
        background: #da3633;
        color: #ffffff;
    }
    #exit-btn:hover {
        background: #f85149;
    }
    Footer {
        background: #161b22;
        color: #8b949e;
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
        log.write("[bold cyan][*] Ai_Freenet Autonomous Engine Initialized.[/bold cyan] [dim](Dev by Victor Geek)[/dim]")
        log.write("[yellow][*] Ready to execute autonomous self-healing agent.py...[/yellow]\n")
        log.write("[dim blue]Shortcuts: [R] Run Agent | [C] Clear Logs | [Q] Exit | Enter on Focused Button[/dim blue]\n")
        
        # ၄။ စဖွင့်သည်နှင့် ခလုတ်ပေါ် Auto Focus ရောက်ရှိစေရေး
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
            # ၅။ မူလ dynamic execution & thread-safe logging အပြည့်အဝပါဝင်မှု
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
    
