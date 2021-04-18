# The UDP Beaconing Service

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

If the CCS provides location for every other node in the system, then who provides the location for the CCS? I'm glad you asked. The beaconing service will provide a UDP broadcast across the network with a dedicated tcp header (kinda) so for those who know what to listen for can find it. Thankfully, this will be prebuilt into the base node template so every LIAMb Node can find the bus (other wise LIAMb nodes would be kinda usless). Under the hood, these UDP broadcasts will also serve as heartbeats so beacons will also be able to utilize TCP in case the network gets hit with a lot of traffic.

## Architecture
---

<img src="../images/LMB_architecture-Beaconing Service.png" width="900px" style="display: block;
  margin-left: auto;
  margin-right: auto;
  width: 50%;">

## Specifications
---