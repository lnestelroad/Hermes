# Hermes


<!-- <img src="images/IMG_6857.jpg" style="display: block;
  margin-left: auto;
  margin-right: auto;
  width: 50%;">   -->

+ Status: draft
+ Editor: Liam Nestelroad nestelroadliam@gmail.com
+ Contributors:

## Summary
---

Hermes is a collection of tools to stand up a distributed message bus system and add new nodes to send/receive messages. This project is a formalized architecture topology over the Zero Message Queue library which includes standardized message protocols and exchange patterns. 

## Installation
---

Hermes is uploaded on the PyPI and can therefore be install with the following command:
  ```bash
  pip3 install hermes-lnestelroad
  ```
<!-- ## Build -->
<!-- --- -->

<!-- To build this project, it is recommended that you use a python virtual environment. You will first need to install the appropriate Python modules with the provided requirement.txt file using the following command:
```bash
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
``` -->

## Usage
---

There are a few different ways to use Hermes depending on if you are a developer or want to get data out from an existing instance.

### Initial Bus Standup

### Adding New Services

### Getting Messages From the Bus.

## Architecture
---

When I say "decentralized" in this document, what I am really saying is pseudo-decentralized. This is because while there is still going to be a main node which everything has to first go though, once the information is returned, the connections between the services and clients go off the bus and talk amongst themselves. There are a few concerns regarding this setup as it makes for a much looser environment and harder to keep track of, but using the zmq monitoring and distributed logging concepts, I will try and show that these can be overcome. Refer to the following diagram for further clarification:

<img src="docs/images/LMB_architecture-Functional Interconnect.png" width="900px" style="display: block;
  margin-left: auto;
  margin-right: auto;
  width: 100%;">
