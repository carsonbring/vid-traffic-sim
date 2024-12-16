import psutil
import pyshark
from rich import print
from rich.console import Console
import threading
from autogen import ConversableAgent, ChatResult


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


def run_workflow(console: Console, packet_string: str):
    console.print("Running autogen workflow")
    generator = ConversableAgent(
        name="Video Traffic Packet Generator",
        llm_config={
            "config_list": [
                {
                    "model": "llama3.2:3b",
                    "temperature": 0.6,
                    "base_url": "http://localhost:11434/v1",
                    "api_key": "ollama",
                }
            ]
        },
        system_message="""<Profile> \n You are a cybersecurity expert and have lots of experience dealing with video network traffic. \n</Profile> \n
        <Goal> \n Your ONLY goal is to generate 3 video traffic packets in the same format as the packets in your context. ONLY RESPOND WITH THE GENERATED PACKETS AND NOTHING ELSE. YOU MUST ONLY RESPOND WITH THREE generated packets in the same format as the ones given to you by the reviewer and they MUST have the same level of detail. \n </Goal> \n
        """,
        human_input_mode="NEVER",
        is_termination_msg=lambda msg: "terminate" in msg["content"].lower(),
    )
    reviewer = ConversableAgent(
        name="Video Traffic Packet Reviewer",
        llm_config={
            "config_list": [
                {
                    "model": "llama3.2:3b",
                    "temperature": 0.6,
                    "base_url": "http://localhost:11434/v1",
                    "api_key": "ollama",
                }
            ]
        },
        system_message="""<Profile> \n You are a cybersecurity expert and have lots of experience dealing with video network traffic. \n</Profile> \n
        <Goal> \n Your goal is to review the Video Traffic Packet Generator's generated packets and ensure they fit with the previous packets in the conversation history. If they do not, tell the Generator how to fix the problem. \n </Goal> \n
        ONLY SAY 'TERMINATE' if the generated packets look correct. You shouldn't say 'TERMINATE' in any other context""",
        human_input_mode="NEVER",
    )

    try:
        result = reviewer.initiate_chat(
            generator,
            message=f"Generate video traffic packets based on the following input: \n<INPUT>\n{packet_string}\n</INPUT>\n",
        )
        console.print("[bold green]Workflow completed successfully.[/bold green]")

        write_output(result)
        console.print(f"[bold blue] RESULT WRITTEN at output.txt[/bold blue]")

    except Exception as e:
        console.print(
            f"[bold red]An error occurred during the workflow: {e}[/bold red]"
        )


def write_output(result: ChatResult):
    with open("output.txt", "w") as file:
        for i, message in enumerate(result.chat_history[1:]):
            file.write(f"\n---------------------Message {i}-----------------------\n")
            file.write(
                f"++++++++++++++++++Agent {message['name']}+++++++++++++++++++++++++++\n"
            )
            file.write(message["content"])
