# Node-RED integration

Node-RED is the orchestration layer, not the place where untested psychrometric formulas are duplicated.

Recommended flow stages:

1. Zigbee2MQTT input
2. normalize Aqara T1 payloads
3. keep latest room A / room B / outdoor measurements
4. call the control-core step on a periodic tick or sensor update
5. publish pair state
6. pass the logical control command through duepoint-actuator
7. actuator interlock maps fan banks + V0.3 route and independently enforces servo settle timing
8. WLED/GPIO protocol adapter converts safe physical targets to device commands
9. log measurements and decisions

## Runtime integration

The JavaScript control core can be exposed to Node-RED either as:

- a small custom Node-RED node/package, or
- a Function node with external-module access to the project package.

The project should prefer one shared implementation rather than copy/pasting control formulas into multiple Function nodes.

The first importable production flow will be added after the exact Zigbee2MQTT friendly names and WLED controller endpoints are known.

## Actuator adapter safety requirements

The project now provides a dedicated duepoint-actuator Node-RED node around the
tested physical interlock.

It:

- defaults all physical fan outputs to OFF after deployment/reconnect,
- rejects commands past valid_until_ms,
- rejects sequence regression,
- maps logical room roles onto supply/exhaust fan banks,
- commands the ROUTING-V0.3 dual-T-diverter route,
- independently keeps fans OFF for measured servo travel + settle time,
- refuses fan release while servo_travel_ms is uncalibrated,
- preserves command/sequence metadata for downstream telemetry.

The later WLED/GPIO protocol adapter must consume this physical safe output,
not bypass it with raw logical targets.

Transient non-zero fan commands must not be retained in MQTT.
