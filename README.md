# Video Network Traffic Simulator

## How to run (Python 3.12 supported)

* Create venv, pip install the requirement.txt file
`python main.py`

## Information

* This project utilizes the following core libraries:
  * pyshark
  * langchain
  * ollama

* The application is intended to:
  * Collect video traffic information on a network interface
  * Generate simulated traffic using an LLM (with tool calling functionality)
  * Show generated data in real time + in file output for longevity
