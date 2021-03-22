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

The Distributive Broker Protocol (DBP) defines a set of reliable core services to govern communication across a pool of nodes. DBP covers discovery, monitoring, network bridging, last value caching, and logging aggregation.

## Installation
---

To run this project, it is recommended that you use a python virtual environment. You will first need to install the appropriate Python modules with the provided requirement.txt file using the following command:
```bash
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
```
The following modules will be installed. In reality you will only need `pyzmq`, but the others will be used for monitoring and visualizing metrics.
+ pyzmq==22.0.2 for message sending
+ matplotlib==3.3.3 for reports
<!-- + ipykernel==5.4.3 -->
+ tqdm==4.56.0 for testing progress

<!-- ### Optional Jupyter Notebook -->

<!-- TODO: Give directions for Jupyter Notebook Set up -->

## Usage
---

<!-- TODO: Give directions for usage after project code is finished. -->
Run the `main.py` file for a simulated test with the following command:

```bash
python3 main.py
```

optionally, you can run the `Broker.py`, `Client.py`, and `Service.py` individually in separate terminals (or different machines) to simulate a message bus. 

## Language
---

The key words “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”, “SHOULD”, “SHOULD NOT”, “RECOMMENDED”, “MAY”, and “OPTIONAL” in this document are to be interpreted as described in RFC 2119 (see [“Key words for use in RFCs to Indicate Requirement Levels"](http://tools.ietf.org/html/rfc2119)).

## Goals



## Architecture Overview
---

When I say "decentralized" in this document, what I am really saying is pseudo-decentralized. This is because while there is still going to be a main node which everything has to first go though, once the information is returned, the connections between the services and clients go off the bus and talk amongst themselves. There are a few concerns regarding this setup as it makes for a much looser environment and harder to keep track of, but using the zmq monitoring and distributed logging concepts, I will try and show that these can be overcome. Refer to the following diagram for further clarification:

<img src="images/LMB_architecture-Functional Interconnect.png" width="900px" style="display: block;
  margin-left: auto;
  margin-right: auto;
  width: 100%;">

### The Core Catalog Service 
---

In all maters of speaking, this IS the message bus. Everything will be going through this component before its allowed to interact with anything else. New nodes that want to publish or provide services will be required to register with the CCS so that people/processes can find its IP address and port. As for providing the location of the CCS itself, a beacon will be attached so anyone who knows what to listen for can find it (more on that later).

The CCS will also "house" the other core components either by including their logic in its event loop or by having them persistently attached. Refer to the following diagram for further clarification:

<img src="images/LMB_architecture-Core Catalog Service.png" width="900px" style="display: block;
  margin-left: auto;
  margin-right: auto;
  width: 50%;">

#### Specifications
---

We define 'client' applications as node that _request_ information from the broker and 'service' applications as nodes the _provide_ information to the broker. The DBP will consist of a few sub-protocols:

+ DBP/Info Request which covers how the Broker Node provides service info with client applications.
+ DBP/Service Registration, which covers how services register with the broker node
+ DBP/Heartbeats, which covers how heartbeat messages should be sent between services and the broker node

**ROUTER Addressing**

The broker MUST use a ROUTER socket on port 5246 to accept requests from clients, and connections from Services. The broker MAY use a separate socket for each sub-protocol, or MAY use a single socket for each sub-protocols.

Keep in mind, from the ØMQ Reference Manual:

    When receiving messages a ROUTER socket shall prepend a message part containing the identity of the originating peer to the message before passing it to the application. When sending messages a ROUTER socket shall remove the first part of the message and use it to determine the identity of the peer the message shall be routed to.

**DBP/Info Request**

DBP/Info Request is a strictly synchronous dialog initiated by the client (where ‘C’ represents the client, and ‘B’ represents the broker):

    Repeat:
      C: REQUEST
      B: REPLY
      ...

A **_REQUEST_** command consists of a multipart message of 4 or more frames, formatted on the wire as follows:

    Frame 0: Empty (zero bytes, invisible to REQ application)
    Frame 1: 'u_U' (3 bytes for info request command)
    Frame 2: time (current epoch time)
    Frame 3: Service(s) info request (printable string)

A **_REPLY_** command consists of a multipart message of 5 or more frames, formatted on the wire as follows:

    Frame 0: Message Reply Address (from request message header)
    Frame 1: Empty (zero bytes, invisible to REQ application)
    Frame 2: 'o_O' (3 bytes for info retrieval response)
    Frame 3: time (current epoch time)
    Frame 4: Information retrieval (serialized json object)

Clients SHOULD use a REQ socket when implementing a synchronous request-reply pattern. The REQ socket will silently create frame 0 for outgoing requests, and remove it for replies before passing them to the calling application. Clients MAY use a DEALER (XREQ) socket when implementing an asynchronous pattern. In that case the clients MUST create the empty frame 0 explicitly.

The information request is either a specified services name or a list of currently active services available. Information that is not available should be responded with by an inactive warning.

**DBP/Service Registration**

DBP/Service Registration is a strictly synchronous request-reply dialog, initiated by the service node. This is the synchronous dialog (where ‘S’ represents the service, and ‘B’ represents the broker node):

    S: READY
    Repeat:
        B: REQUEST
        S: REPLY
        ...

A **_REGISTRATION_** request consists of a multipart message of 4 frames, formatted on the wire as follows:

    Frame 0: Empty frame
    Frame 1: 'UwU' (3 byte, representing REGISTRATION)
    Frame 2: time (current epoch time)
    Frame 3+: Service information (serialized json object)

Service information shall consist of the services name, ip address, port, function, and heartbeat timing at a minimum.

An **_UPDATE_** request consists of a multipart message of 4 frames, formatted on the wire as follows:

    Frame 0: Empty frame
    Frame 1: 'UoU' (3 byte, representing config update)
    Frame 2: time (current epoch time)
    Frame 3+: Updated values (serialized json object)

An **_APPROVED_** reply consists of a multipart message of 6 or more frames, formatted on the wire as follows:

    Frame 0: Empty frame
    Frame 1: 'OwO' (3 byte, representing APPROVED)
    Frame 2: time (current epoch time)
    Frame 3+: Optional configuration changes 

An **_DENIED_** reply consists of a multipart message of 3 or more frames for unauthorized or unregistered services, formatted on the wire as follows:

    Frame 0: Empty frame
    Frame 1: '(O_O)' (one byte, representing DENIED)
    Frame 2: time (current epoch time)
    Frame 3+: Reasons for denial

**DBP/Heartbeats**
DBP/Heartbeats are a zmq independent messaging schema that uses raw UDP sockets to broadcast from the broker node and send one off's from the services top the broker. In the event of a missing beat, heartbeats will switch over to reliable TCP connections via req/rep zmq sockets.

The asynchronous heartbeat dialog operates on the same sockets and works thus:

    Repeat:                 Repeat:
        S: HEARTBEAT            B: HEARTBEAT
        ...                     ...
    S: DISCONNECT           B: DISCONNECT



A **_HEARTBEAT_** message consists of a multipart message of 3 frames, formatted on the wire as follows:

    Frame 0: Empty frame
    Frame 1: '<3' (two bytes, representing HEARTBEAT)
    Frame 2: time (current epoch time)
    Frame 3: Service name.

A **_DISCONNECT_** command consists of a multipart message of 3 frames, formatted on the wire as follows:

    Frame 0: Empty frame
    Frame 1: '</3' (3 byte, representing DISCONNECT)
    Frame 2: time (current epoch time)

An **AWK** command consists of a multipart message of 3 frames, formatted on the wire as follows:

    Frame 0: Empty frame
    Frame 1: 'u.u' (3 byte, representing DISCONNECT)
    Frame 2: time (current epoch time)

DBP/Service commands all start with an empty frame to allow consistent processing of client and Service frames in a broker, over a single socket. The empty frame has no other significance.

**Opening and Closing a Connection**

+ The service node is responsible for opening and closing a logical connection. One service node MUST connect to exactly one broker using a single ØMQ DEALER (XREQ) socket.

+ Since ØMQ automatically reconnects peers after a failure, every DBP command includes the protocol header to allow proper validation of all messages that a peer receives.

+ The service node opens the connection to the broker by creating a new socket, connecting it, and then sending a REGISTER command. The service node MUST NOT send a further READY.

+ The service node MAY send DISCONNECT at any time, including before READY. When the broker receives DISCONNECT from a service node it MUST send no further commands to that service node.

+ The broker MAY send DISCONNECT at any time, by definition after it has received at least one command from the service node.

+ The broker MUST respond to any valid but unexpected command by sending DISCONNECT and then no further commands to that service node. The broker SHOULD respond to invalid messages by dropping them and treating that peer as invalid.

+ When the service node receives DISCONNECT it must send no further commands to the broker; it MUST close its socket, and reconnect to the broker on a new socket. This mechanism allows service nodes to re-register after a broker failure and recovery.

**Heartbeating**

+ HEARTBEAT commands are valid at any time, after a READY command.

+ Any received command except DISCONNECT acts as a heartbeat. Peers SHOULD NOT send HEARTBEAT commands while also sending other commands.

+ Both broker and worker MUST send heartbeats at regular and agreed-upon intervals. A peer MUST consider the other peer “disconnected” if no heartbeat arrives within some multiple of that interval (usually 3-5).

+ If the worker detects that the broker has disconnected, it SHOULD restart a new conversation.

+ If the broker detects that the worked has disconnected, it SHOULD stop sending it messages of any type.

**Reference Implementations**

The C99 Majordomo examples from Chapter 4 of the Guide (see “ØMQ - The Guide") act as the prime reference implementation for MDP. There is a Python implementation of MDP by Guido Goldstein.

### The Last Cached Value Service
---

All services that publish will be subscribed by this component in order to cache the most recent message. This is so any new client can get an immediate update without having to wait (what could be minutes) for the next round.

<img src="images/LMB_architecture-Last Cached Value Service.png" width="900px" style="display: block;
  margin-left: auto;
  margin-right: auto;
  width: 50%;">

#### Specifications
---

### The Distributed Logging Aggregator Service
---

Each node on the bus will come include with a logging component as part of the base template. Logs will be generated on specific events (a list in which the user can also add to). Critical events and warning logs will need to be saved in order to determine faulty software occurrence. The log aggregator will be used to pull in all of those into the bus for future analysis. Everything else will be saved to the nodes internal system via the Syslog program.

<img src="images/LMB_architecture-Log Aggregator.png" width="900px" style="display: block;
  margin-left: auto;
  margin-right: auto;
  width: 50%;">

### The Network Proxy Bridge Service
---

One of the main goals for this bus was to be able to generate a message at a higher network level and propagate it down to a lower listener (or vise versa). For obvious reasons, we do not want nodes talking directly to each other over the firewalls (kinda defeats the purpose) so all messages will be routed through the interconnected brokers. This is where the bus acts like a centralized brokering system. Refer to the following image for further clarification:

<img src="images/LMB_architecture-Network Bridge.png" style="display: block;
  margin-left: auto;
  margin-right: auto;
  width: 50%;">

### The UDP Beaconing Service
---

If the CCS provides location for every other node in the system, then who provides the location for the CCS? I'm glad you asked. The beaconing service will provide a UDP broadcast across the network with a dedicated tcp header (kinda) so for those who know what to listen for can find it. Thankfully, this will be prebuilt into the base node template so every LIAMb Node can find the bus (other wise LIAMb nodes would be kinda usless). Under the hood, these UDP broadcasts will also serve as heartbeats so beacons will also be able to utilize TCP in case the network gets hit with a lot of traffic.

<img src="images/LMB_architecture-Beaconing Service.png" width="900px" style="display: block;
  margin-left: auto;
  margin-right: auto;
  width: 50%;">

### The Distributed Monitoring Service
---

While the goal here is to have a distributed like system where nodes can go off and have their own conversation with out the help of the CCS or some other broker, sometimes its necessary to listen in on either for debugging or metric gathering purposes. For that reason, the bus will come with a socket monitoring service that will inform services/clients to open a monitoring port for it to connect to and watch upon request. 

Additionally, I will be necessary for the bus to know the liveliness status of all services registered so the monitoring service will handel idle heartbeats (idle meaning when the service is not in use).

<img src="images/LMB_architecture-Distributive Monitoring Service.png" width="900px" style="display: block;
  margin-left: auto;
  margin-right: auto;
  width: 50%;">

## Specifications

Because there are going to be a lot of moving parts here in terms of implementation, it is going to be necessary to set up standards for bus components. This ranges from assigned port numbers, topic names, message formats, and sequencing.

### Port Bindings

All LIAMb Nodes shall have each subsequently generated sockets bind to ports of incrementing values starting at 5246. In the case of broker type nodes, the following internal services shall use the designated schema:

+ Beacon -> 5246
+ Bus Interface -> 5247
+ Monitor -> 5248
+ Network Proxy -> 5249