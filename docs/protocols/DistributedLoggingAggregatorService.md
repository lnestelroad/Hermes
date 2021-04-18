# The Distributed Logging Aggregator Service Protocol

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

Each node on the bus will come include with a logging component as part of the base template. Logs will be generated on specific events (a list in which the user can also add to). Critical events and warning logs will need to be saved in order to determine faulty software occurrence. The log aggregator will be used to pull in all of those into the bus for future analysis. Everything else will be saved to the nodes internal system via the Syslog program.

## Architecture
---

<img src="../images/LMB_architecture-Log Aggregator.png" width="900px" style="display: block;
  margin-left: auto;
  margin-right: auto;
  width: 50%;">

## Specifications
---