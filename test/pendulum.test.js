import test from "node:test";
import assert from "node:assert/strict";

import {
  States,
  initialController,
  stepPendulum,
  targetsForState,
} from "../src/control/pendulum.js";

test("enable starts phase A with balanced opposite directions", () => {
  const result = stepPendulum({
    controller: initialController(0),
    now_ms: 100,
    enabled: true,
    pwm_pct: 65,
  });
  assert.equal(result.controller.state, States.PHASE_A);
  assert.deepEqual(result.targets.room_a, { intake_pct: 65, exhaust_pct: 0, mode: "SUPPLY" });
  assert.deepEqual(result.targets.room_b, { intake_pct: 0, exhaust_pct: 65, mode: "EXHAUST" });
});

test("phase A transitions through all-off dead time to phase B", () => {
  const phaseA = { state: States.PHASE_A, entered_at_ms: 0 };
  const dead = stepPendulum({
    controller: phaseA,
    now_ms: 60000,
    enabled: true,
    phase_time_ms: 60000,
    dead_time_ms: 3000,
  });
  assert.equal(dead.controller.state, States.DEADTIME_TO_B);
  assert.equal(dead.targets.room_a.mode, "OFF");
  assert.equal(dead.targets.room_b.mode, "OFF");

  const phaseB = stepPendulum({
    controller: dead.controller,
    now_ms: 63000,
    enabled: true,
    phase_time_ms: 60000,
    dead_time_ms: 3000,
  });
  assert.equal(phaseB.controller.state, States.PHASE_B);
  assert.equal(phaseB.targets.room_a.mode, "EXHAUST");
  assert.equal(phaseB.targets.room_b.mode, "SUPPLY");
});

test("fault immediately turns both modules off", () => {
  const result = stepPendulum({
    controller: { state: States.PHASE_B, entered_at_ms: 0 },
    now_ms: 5000,
    enabled: true,
    fault: true,
  });
  assert.equal(result.controller.state, States.FAULT);
  assert.equal(result.targets.room_a.mode, "OFF");
  assert.equal(result.targets.room_b.mode, "OFF");
});

test("no normal state commands intake and exhaust together in one module", () => {
  for (const state of Object.values(States)) {
    const targets = targetsForState(state, 80);
    for (const room of [targets.room_a, targets.room_b]) {
      assert.ok(room.intake_pct === 0 || room.exhaust_pct === 0);
    }
  }
});
