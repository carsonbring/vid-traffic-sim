from inspect import Attribute
from rich import print, box
import threading
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from utils import list_network_interfaces, wait_for_stop, run_workflow
import pyshark
from pyshark.packet.packet import Packet


class VideoTrafficSimulator:
    def __init__(self):
        self.running = True
        self.console = Console()
        self.menu = True
        self.packets = []
        self.packet_string = ""

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
        self,
        interface: str,
        stop_event: threading.Event,
        console: Console,
        src_address: str,
        port: int,
    ) -> list[Packet] | None:
        try:
            if port != -1:
                capture = pyshark.LiveCapture(
                    interface=interface,
                    bpf_filter=f"udp port {port}",
                )
                console.print(
                    f"[bold blue]Listing to traffic on Port: {port}[/bold blue]"
                )
            else:
                capture = pyshark.LiveCapture(
                    interface=interface,
                    bpf_filter="udp",
                )
                console.print(
                    f"[bold blue]Listing to traffic from src address: {src_address}[/bold blue]"
                )

            print(interface)

            for packet in capture.sniff_continuously(packet_count=50):
                try:
                    if stop_event.is_set():
                        capture.close()
                        console.print(
                            f"[bold green]Packet capture stopped. {len(self.packets)} packets captured.[/bold green]"
                        )
                        break
                    if src_address != "":
                        if packet.ip.src == src_address:
                            console.print("Packet read")
                            self.packets.append(packet)
                    else:
                        console.print("Packet read")
                        self.packets.append(packet)
                except AttributeError as e:
                    pass

                # console.print(f"[green]Packet received: {packet}[/green]")

            console.print(
                f"[bold green]Packet capture stopped. {len(self.packets)} packets captured.[/bold green]"
            )

            capture.close()
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
        interface_name = user_input

        port = -1
        src_address = ""

        user_input = Prompt.ask(
            "Port or IP filter?",
            choices=["port", "ip"],
            default="exit",
        )
        if user_input == "exit":
            return
        elif user_input == "ip":
            user_input = Prompt.ask(
                "Source IP address to listen for:",
                default="exit",
            )
            if user_input == "exit":
                return
            src_address = user_input
        elif user_input == "port":
            user_input = IntPrompt.ask(
                "Port to listen on:",
                default=-1,
            )
            if user_input == -1:
                return
            port = user_input

        stop_event = threading.Event()
        capture_thread = threading.Thread(
            target=self.capture_packets,
            args=(interface_name, stop_event, self.console, src_address, port),
            daemon=False,
        )
        capture_thread.start()
        self.console.print(
            "[green]PyShark is now listening to network traffic. Press Enter to stop[/green]"
        )
        stop_thread = threading.Thread(
            target=wait_for_stop,
            args=(stop_event, capture_thread, self.console),
            daemon=False,
        )
        stop_thread.start()
        stop_thread.join()

        user_input = Prompt.ask(
            "Write result or generate packets?",
            choices=["write", "gen"],
            default="exit",
        )
        if user_input == "exit":
            return
        else:
            packet_string = "<PacketData>\n"
            for i, packet in enumerate(self.packets):
                packet_string = packet_string + f"<Packet{i}>\n"
                packet_string = packet_string + str(packet) + "\n"
                packet_string = packet_string + f"</Packet{i}>\n"
            packet_string = packet_string + "</PacketData>\n"
            if user_input == "write":
                with open("packets.txt", "w") as file:
                    file.write(packet_string)
                user_input = Prompt.ask(
                    "Continue..?",
                    choices=["yes", "no"],
                    default="no",
                )
                if user_input == "no":
                    return
                else:
                    self.run()
            else:
                self.packet_string = packet_string
                self.load_network_data(self.packet_string)

    def load_network_data(self, packet_string=""):
        self.console.print("[bold blue]Loading network data...[/bold blue]")
        if packet_string == "":
            file_path = Prompt.ask("Enter the path to your data file")
            with open(file_path) as file:
                packet_string = file.read()
            self.console.print(f"[green]Loaded data from {file_path}.[/green]")
        else:
            self.console.print("[green]Loaded data from PyShark session.[/green]")
        run_workflow(self.console, packet_string)
        user_input = Prompt.ask(
            "Continue..?",
            choices=["yes", "no"],
            default="no",
        )
        if user_input == "no":
            return
        else:
            self.run()

    def exit_application(self):
        self.console.print("[bold red]Exiting the application. Goodbye![/bold red]")
        self.running = False
