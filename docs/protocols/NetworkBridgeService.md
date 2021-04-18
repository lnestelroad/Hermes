# The Network Bridge Service

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

One of the main goals for this bus was to be able to generate a message at a higher network level and propagate it down to a lower listener (or vise versa). For obvious reasons, we do not want nodes talking directly to each other over the firewalls (kinda defeats the purpose) so all messages will be routed through the interconnected brokers. This is where the bus acts like a centralized brokering system. Refer to the following image for further clarification:

## Architecture
---

<img src="images/LMB_architecture-Network Bridge.png" style="display: block;
  margin-left: auto;
  margin-right: auto;
  width: 50%;">

## Specification
---