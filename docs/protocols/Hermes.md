# The Hermes Interconnect Protocol

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


## Port Bindings
---

All LIAMb Nodes shall have each subsequently generated sockets bind to ports of incrementing values starting at 5246. In the case of broker type nodes, the following internal services shall use the designated schema:

+ Beacon -> 5246
+ Bus Interface -> 5247
+ Monitor -> 5248
+ Network Proxy -> 5249