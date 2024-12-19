# Video Network Traffic Simulator

## Outline

---

Pyshark is a Python wrapper for tshark, allowing python packet parsing using wireshark dissectors.
PyShark was used to monitor network traffic on a user-selected network interface.
After the user inputs an IPv4 address or a port that is sending video traffic to the selected network interface, the simulator program filters the incoming network traffic.
This decreased network traffic noise, and allowed for relatively pure video traffic data to be used to train the simulator’s LLM. The program also enables the user to save collected video data and load into the program later.

After the data is loaded, we used Microsoft's Autogen API to access local a local model running on our machines (llama3.2:3b) using ollama, an open source local llm model hosting server.
Through the Autogen Agentic Framework, we created a generator agent and a reviewer agent that iterate until it generates three packets of data using the input packet data as a reference.
Both agents are using llama3.2:3b, and the speed of the program is proportional to the specs of the computer that this is running on.
The output is stored in output.txt and it includes the generated packets along with the conversation between the agents.

---

## Results

### Data

Collecting the data through Pyshark was a bit difficult due to some restraints of bpf filtering and the fact that streaming/video services assign a dynamic port and usually a dynamic host address depending on which server its coming from.
Because of this, we bpf filter based off of udp and either a port or IPv4 address instead and put the responsibility on the user to use wireshark in tandem with our program
Using this technique, we are able to capture video data effectively

### Analysis

Since we are decently familiar with Autogen from previous projects, the analysis was more straight forward since we just created an agentic workflow that takes into account the generation and review aspects of the assignment.
Both agents are using Llama3.2:3b, and most modern computers will be able to run a model that small.

### Discussion

Overall, we are fairly happy with the results of our project, and the choice to use a review/generation autogen workflow was a good one. Its very interesting to watch the agents interact with each other and ensure that their packet output fits in with the original data provided

## Demo

A demo of running the application through screenshots can be found in the ```screenshots/``` dir
the result of the demo screenshots can be found in the  ```demo_output.txt``` file

## How to run (Python 3.12 supported)

* Create venv, pip install the requirement.txt file
`python main.py`
* setup ollama server (see below)
* Install tshark

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
