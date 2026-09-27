# Node-RED integration

Node-RED is the orchestration layer, not the place where untested psychrometric formulas are duplicated.

Recommended flow stages:

1. Zigbee2MQTT input
2. normalize Aqara T1 payloads
3. keep latest room A / room B / outdoor measurements
4. call the control-core step on a periodic tick or sensor update
5. publish pair state
6. publish four logical fan targets
7. WLED adapter converts targets to device commands
8. log measurements and decisions

## Runtime integration

The JavaScript control core can be exposed to Node-RED either as:

- a small custom Node-RED node/package, or
- a Function node with external-module access to the project package.

The project should prefer one shared implementation rather than copy/pasting control formulas into multiple Function nodes.

The first importable production flow will be added after the exact Zigbee2MQTT friendly names and WLED controller endpoints are known.

## Actuator adapter safety requirements

The Node-RED/WLED adapter must:

- default all outputs to OFF at deployment/reconnect,
- reject output commands past valid_until_ms,
- avoid retained non-zero fan target messages,
- preserve the controller sequence/command ID in telemetry,
- never bypass STARTUP_DEADTIME or reversal dead-time.
