from rich import print, box
import threading
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from utils import list_network_interfaces, wait_for_stop
import pyshark
from pyshark.packet.packet import Packet


class VideoTrafficSimulator:
    def __init__(self):
        self.running = True
        self.console = Console()
        self.menu = True
        self.packets = []

    def run(self):
        self.display_menu()
        user_input = Prompt.ask(
            "Select an action",
            choices=["shark", "load", "exit"],
            default="exit",
        )
        self.handle_command(user_input)

    def display_menu(self):
        table = Table(
            title="[bold italic red u]Video Traffic Simulator[/bold italic red u]",
            box=box.DOUBLE,
            padding=1,
        )
        table.add_column("Action")
        table.add_column("Description")
        table.add_column("Command", style="yellow")
        table.add_row(
            "Listen for Traffic",
            "Use PyShark to listen to network traffic on your internet interface \n [italic] file output or take data into generation [/italic]",
            "shark",
        )
        table.add_row(
            "Load Network Data",
            "Skip listening and upload data directly from a file",
            "load",
        )
        table.add_row(
            "Exit Application",
            "Self explanitory",
            "exit",
        )

        self.console.print("\n")
        self.console.print(table)
        self.menu = False

    def handle_command(self, command: str):
        if command == "shark":
            self.listen_for_traffic()
        elif command == "load":
            self.load_network_data()
        elif command == "exit":
            self.exit_application()
        else:
            self.console.print(f"[red]Unknown command: {command}[/red]")

    def capture_packets(
        self, interface: str, stop_event: threading.Event, console: Console
    ) -> list[Packet] | None:
        try:
            capture = pyshark.LiveCapture(interface=interface)
            for packet in capture.sniff_continuously():
                if stop_event.is_set():
                    capture.close()
                    console.print(
                        f"[bold green]Packet capture stopped. {len(self.packets)} packets captured.[/bold green]"
                    )
                self.packets.append(packet)
                console.print(f"[green]Packet received: {packet}[/green]")
        except Exception as e:
            console.print(f"[red]Error during packet capture: {e}[/red]")

    def listen_for_traffic(self):
        self.console.print("[bold blue]Listening for traffic...[/bold blue]")
        interface_names = list_network_interfaces(self.console)
        interface_names.append("exit")
        user_input = Prompt.ask(
            "Select an interface",
            choices=interface_names,
            default="exit",
        )
        if user_input == "exit":
            return

        stop_event = threading.Event()
        capture_thread = threading.Thread(
            target=self.capture_packets,
            args=(
                user_input,
                stop_event,
                self.console,
            ),
            daemon=True,
        )
        capture_thread.start()
        self.console.print(
            "[green]PyShark is now listening to network traffic.[/green]"
        )
        stop_thread = threading.Thread(
            target=wait_for_stop,
            args=(stop_event, capture_thread, self.console),
            daemon=True,
        )
        stop_thread.start()

    def load_network_data(self):
        self.console.print("[bold blue]Loading network data...[/bold blue]")
        file_path = Prompt.ask("Enter the path to your data file")
        self.console.print(f"[green]Loaded data from {file_path}.[/green]")

    def exit_application(self):
        self.console.print("[bold red]Exiting the application. Goodbye![/bold red]")
        self.running = False
