import psutil
import pyshark
from rich import print
from rich.console import Console
import threading


def list_network_interfaces(console: Console) -> list[str]:
    interfaces = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    names = []

    for name, _ in interfaces.items():
        console.print(f"Interface: {name}")
        names.append(name)
        if name in stats:
            is_up = "Up" if stats[name].isup else "Down"
            console.print(f"  Status: {is_up}")
            console.print(f"  Speed: {stats[name].speed}Mbps")
            console.print(f"  MTU: {stats[name].mtu}")
        console.print()
    return names


def wait_for_stop(
    stop_event: threading.Event, capture_thread: threading.Thread, console: Console
):
    input()
    stop_event.set()
    console.print("[bold red]Stopping packet capture...[/bold red]")
    if capture_thread:
        capture_thread.join()
