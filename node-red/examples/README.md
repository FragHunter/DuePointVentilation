# Node-RED control-node example

The duepoint-control node is a thin wrapper around the tested JavaScript control core.

Input payload fields:

- indoor: normalized measurement
- outdoor: normalized measurement
- now_ms: optional timestamp; Date.now() is used if omitted
- controller_fault: optional boolean
- config: optional complete config override

The node stores the finite-state-machine state in Node-RED node context and emits logical actuator targets plus command freshness metadata.

The WLED adapter is a separate downstream concern. It must reject expired commands and start with all fan outputs OFF.
