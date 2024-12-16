# Video Network Traffic Simulator

## How to run (Python 3.12 supported)

* Create venv, pip install the requirement.txt file
`python main.py`
* setup ollama server (see below)

## Information

* This project utilizes the following core libraries:
  * pyshark
  * microsoft autogen
  * ollama

* The application is intended to:
  * Collect video traffic information on a network interface
  * Generate simulated traffic using an LLM (with tool calling functionality)
  * Show generated data in real time + in file output for longevity

* Output is located at `output.txt`
* By default, packets are stored at `packets.txt`

## Ollama setup

* In order to run this project you must serve an ollama server on your local machine.
There are multiple ways to do this, but It must be done. I use systemd on linux to do so, but if you download ollama using your package manager of choice or via their website and follow these steps

Download llama3.2:3b
`ollama pull llama3.2:3b`
Serve ollama
`ollama serve`

After you do this, everything should work.
