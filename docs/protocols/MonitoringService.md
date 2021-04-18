# The Distributed Monitoring Service

+ Status: draft
+ Editor: Liam Nestelroad liam.nestelroad@lasp.colorado.edu
+ Contributors: 

## Summary
---



## Language
---

The key words “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”, “SHOULD”, “SHOULD NOT”, “RECOMMENDED”, “MAY”, and “OPTIONAL” in this document are to be interpreted as described in RFC 2119 (see [“Key words for use in RFCs to Indicate Requirement Levels"](http://tools.ietf.org/html/rfc2119)).

## Goals
---

While the goal here is to have a distributed like system where nodes can go off and have their own conversation with out the help of the CCS or some other broker, sometimes its necessary to listen in on either for debugging or metric gathering purposes. For that reason, the bus will come with a socket monitoring service that will inform services/clients to open a monitoring port for it to connect to and watch upon request. 

Additionally, I will be necessary for the bus to know the liveliness status of all services registered so the monitoring service will handel idle heartbeats (idle meaning when the service is not in use).

## Architecture

<img src="../images/LMB_architecture-Distributive Monitoring Service.png" width="900px" style="display: block;
  margin-left: auto;
  margin-right: auto;
  width: 50%;">

## Specifications
---

Because there are going to be a lot of moving parts here in terms of implementation, it is going to be necessary to set up standards for bus components. This ranges from assigned port numbers, topic names, message formats, and sequencing.
