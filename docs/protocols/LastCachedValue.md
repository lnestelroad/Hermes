# The Last Cached Value Service

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

All services that publish will be subscribed by this component in order to cache the most recent message. This is so any new client can get an immediate update without having to wait (what could be minutes) for the next round.

## Architecture
---

<img src="../images/LMB_architecture-Last Cached Value Service.png" width="900px" style="display: block;
  margin-left: auto;
  margin-right: auto;
  width: 50%;">

#### Specifications
---