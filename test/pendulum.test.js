import test from "node:test";
import assert from "node:assert/strict";
import { States, initialController, stepPendulum, targetsForState } from "../src/control/pendulum.js";

test("enable enters startup deadtime before first active phase", () => {
  const start = stepPendulum({controller: initialController(0), now_ms: 100, enabled: true, dead_time_ms: 3000, pwm_pct: 65});
  assert.equal(start.controller.state, States.STARTUP_DEADTIME);
  assert.equal(start.targets.room_a.mode, "OFF");
  assert.equal(start.targets.room_b.mode, "OFF");
  const active = stepPendulum({controller: start.controller, now_ms: 3100, enabled: true, dead_time_ms: 3000, pwm_pct: 65});
  assert.equal(active.controller.state, States.PHASE_A);
  assert.deepEqual(active.targets.room_a, { intake_pct: 65, exhaust_pct: 0, mode: "SUPPLY" });
  assert.deepEqual(active.targets.room_b, { intake_pct: 0, exhaust_pct: 65, mode: "EXHAUST" });
});

test("phase A transitions through all-off dead time to phase B", () => {
  const phaseA = { state: States.PHASE_A, entered_at_ms: 0, sequence: 1 };
  const dead = stepPendulum({controller: phaseA, now_ms: 60000, enabled: true, phase_time_ms: 60000, dead_time_ms: 3000});
  assert.equal(dead.controller.state, States.DEADTIME_TO_B);
  assert.equal(dead.targets.room_a.mode, "OFF");
  assert.equal(dead.targets.room_b.mode, "OFF");
  const phaseB = stepPendulum({controller: dead.controller, now_ms: 63000, enabled: true, phase_time_ms: 60000, dead_time_ms: 3000});
  assert.equal(phaseB.controller.state, States.PHASE_B);
  assert.equal(phaseB.targets.room_a.mode, "EXHAUST");
  assert.equal(phaseB.targets.room_b.mode, "SUPPLY");
});

test("fault immediately turns both modules off", () => {
  const result = stepPendulum({controller: { state: States.PHASE_B, entered_at_ms: 0, sequence: 2 }, now_ms: 5000, enabled: true, fault: true});
  assert.equal(result.controller.state, States.FAULT);
  assert.equal(result.targets.room_a.mode, "OFF");
  assert.equal(result.targets.room_b.mode, "OFF");
});

test("calibration factors independently trim direction targets", () => {
  const targets = targetsForState(States.PHASE_A, 80, {room_a: { supply: 0.9 }, room_b: { exhaust: 1.1 }});
  assert.equal(targets.room_a.intake_pct, 72);
  assert.equal(targets.room_b.exhaust_pct, 88);
});

test("calibrated PWM is clamped to 100 percent", () => {
  const targets = targetsForState(States.PHASE_B, 90, {room_b: { supply: 1.5 }});
  assert.equal(targets.room_b.intake_pct, 100);
});

test("no state commands intake and exhaust together in one module", () => {
  for (const state of Object.values(States)) {
    const targets = targetsForState(state, 80);
    for (const room of [targets.room_a, targets.room_b]) {
      assert.ok(room.intake_pct === 0 || room.exhaust_pct === 0);
    }
  }
});
