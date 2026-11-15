import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

import {
  actuatorStep,
  initialActuatorState,
} from "../src/control/actuator-interlock.js";

const hardware = JSON.parse(
  readFileSync(
    new URL("../config/hardware/gl-c-211wl-three-fan.json", import.meta.url),
  ),
);

function command({
  phase = "PHASE_A",
  sequence = 1,
  commandId = "1:1000",
  generated = 1000,
  validUntil = 10000,
  supply = 60,
  exhaust = 70,
} = {}) {
  const phaseA = phase === "PHASE_A";
  const phaseB = phase === "PHASE_B";

  return {
    phase,
    sequence,
    command_id: commandId,
    generated_at_ms: generated,
    valid_until_ms: validUntil,
    targets: {
      room_a: {
        intake_pct: phaseA ? supply : 0,
        exhaust_pct: phaseB ? exhaust : 0,
      },
      room_b: {
        intake_pct: phaseB ? supply : 0,
        exhaust_pct: phaseA ? exhaust : 0,
      },
    },
  };
}

test("uncalibrated servo timing fails safe with all fans off", () => {
  const result = actuatorStep({
    state: initialActuatorState(),
    command: command(),
    now_ms: 1000,
    hardware_config: hardware,
    actuator_config: {
      servo_travel_ms: null,
      servo_settle_ms: 500,
    },
  });

  assert.equal(result.output.accepted, true);
  assert.equal(result.output.interlock_reason, "SERVO_TIMING_UNCALIBRATED");
  assert.deepEqual(result.output.fans, {
    fan_1: 0,
    fan_2: 0,
    fan_3: 0,
  });
  assert.equal(
    result.output.routing.commanded_position,
    "ROOM_A_SUPPLY_ROOM_B_EXHAUST",
  );
  assert.equal(result.output.routing.moving, true);
});

test("startup route must settle before active fan targets are released", () => {
  const cfg = {
    servo_travel_ms: 1200,
    servo_settle_ms: 300,
  };

  const start = actuatorStep({
    state: initialActuatorState(),
    command: command(),
    now_ms: 1000,
    hardware_config: hardware,
    actuator_config: cfg,
  });
  assert.equal(start.output.interlock_reason, "ROUTE_MOVING");
  assert.deepEqual(start.output.fans, {
    fan_1: 0,
    fan_2: 0,
    fan_3: 0,
  });

  const early = actuatorStep({
    state: start.state,
    command: command({ commandId: "1:2200", generated: 2200 }),
    now_ms: 2200,
    hardware_config: hardware,
    actuator_config: cfg,
  });
  assert.equal(early.output.interlock_reason, "ROUTE_MOVING");

  const settled = actuatorStep({
    state: early.state,
    command: command({ commandId: "1:2500", generated: 2500 }),
    now_ms: 2500,
    hardware_config: hardware,
    actuator_config: cfg,
  });
  assert.equal(settled.output.interlock_reason, "READY");
  assert.deepEqual(settled.output.fans, {
    fan_1: 60,
    fan_2: 60,
    fan_3: 70,
  });
  assert.equal(
    settled.output.routing.stable_position,
    "ROOM_A_SUPPLY_ROOM_B_EXHAUST",
  );
});

test("route reversal independently forces fans off until both-diverter settle window expires", () => {
  const cfg = {
    servo_travel_ms: 1000,
    servo_settle_ms: 250,
  };

  const a0 = actuatorStep({
    state: initialActuatorState(),
    command: command(),
    now_ms: 1000,
    hardware_config: hardware,
    actuator_config: cfg,
  });
  const aReady = actuatorStep({
    state: a0.state,
    command: command({ commandId: "1:2250", generated: 2250 }),
    now_ms: 2250,
    hardware_config: hardware,
    actuator_config: cfg,
  });
  assert.equal(aReady.output.interlock_reason, "READY");

  const bMove = actuatorStep({
    state: aReady.state,
    command: command({
      phase: "PHASE_B",
      sequence: 2,
      commandId: "2:3000",
      generated: 3000,
    }),
    now_ms: 3000,
    hardware_config: hardware,
    actuator_config: cfg,
  });

  assert.equal(bMove.output.interlock_reason, "ROUTE_MOVING");
  assert.deepEqual(bMove.output.fans, {
    fan_1: 0,
    fan_2: 0,
    fan_3: 0,
  });
  assert.equal(
    bMove.output.routing.commanded_position,
    "ROOM_B_SUPPLY_ROOM_A_EXHAUST",
  );

  const bReady = actuatorStep({
    state: bMove.state,
    command: command({
      phase: "PHASE_B",
      sequence: 2,
      commandId: "2:4250",
      generated: 4250,
    }),
    now_ms: 4250,
    hardware_config: hardware,
    actuator_config: cfg,
  });

  assert.equal(bReady.output.interlock_reason, "READY");
  assert.deepEqual(bReady.output.fans, {
    fan_1: 60,
    fan_2: 60,
    fan_3: 70,
  });
});

test("expired command always forces all fan outputs off", () => {
  const result = actuatorStep({
    state: initialActuatorState(),
    command: command({ validUntil: 1500 }),
    now_ms: 1501,
    hardware_config: hardware,
    actuator_config: {
      servo_travel_ms: 1000,
      servo_settle_ms: 250,
    },
  });

  assert.equal(result.output.accepted, false);
  assert.equal(result.output.interlock_reason, "COMMAND_EXPIRED");
  assert.deepEqual(result.output.fans, {
    fan_1: 0,
    fan_2: 0,
    fan_3: 0,
  });
});

test("sequence regression is rejected fail-safe", () => {
  const state = {
    ...initialActuatorState(),
    last_sequence: 4,
    last_command_id: "4:1000",
  };

  const result = actuatorStep({
    state,
    command: command({ sequence: 3, commandId: "3:2000", generated: 2000 }),
    now_ms: 2000,
    hardware_config: hardware,
    actuator_config: {
      servo_travel_ms: 1000,
      servo_settle_ms: 250,
    },
  });

  assert.equal(result.output.accepted, false);
  assert.equal(result.output.interlock_reason, "SEQUENCE_REGRESSION");
  assert.deepEqual(result.output.fans, {
    fan_1: 0,
    fan_2: 0,
    fan_3: 0,
  });
});

test("dead-time command may move route but never releases fan targets", () => {
  const result = actuatorStep({
    state: initialActuatorState(),
    command: {
      ...command({
        phase: "DEADTIME_TO_B",
        sequence: 2,
        commandId: "2:3000",
        generated: 3000,
      }),
      targets: {
        room_a: { intake_pct: 0, exhaust_pct: 0 },
        room_b: { intake_pct: 0, exhaust_pct: 0 },
      },
    },
    now_ms: 3000,
    hardware_config: hardware,
    actuator_config: {
      servo_travel_ms: 1000,
      servo_settle_ms: 250,
    },
  });

  assert.deepEqual(result.output.fans, {
    fan_1: 0,
    fan_2: 0,
    fan_3: 0,
  });
  assert.equal(
    result.output.routing.commanded_position,
    "ROOM_B_SUPPLY_ROOM_A_EXHAUST",
  );
});
