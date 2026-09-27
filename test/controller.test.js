import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { controlStep, initialSystemState } from "../src/control/controller.js";

const config = JSON.parse(readFileSync(new URL("../config/defaults.json", import.meta.url)));
const dryOutside = (now) => ({
  indoor: { temperature_c: 18, relative_humidity_pct: 75, timestamp_ms: now },
  outdoor: { temperature_c: 10, relative_humidity_pct: 60, timestamp_ms: now },
});

test("integrated controller starts with safe all-off deadtime", () => {
  const now = 1000;
  const result = controlStep({state: initialSystemState(0), ...dryOutside(now), now_ms: now, config});
  assert.equal(result.output.ventilation_eligible, true);
  assert.equal(result.output.phase, "STARTUP_DEADTIME");
  assert.equal(result.output.targets.room_a.mode, "OFF");
  assert.equal(result.output.targets.room_b.mode, "OFF");
});

test("actuator output carries TTL and transition sequence", () => {
  const now = 1000;
  const first = controlStep({state: initialSystemState(0), ...dryOutside(now), now_ms: now, config});
  assert.equal(first.output.valid_until_ms, now + config.actuator.command_ttl_ms);
  assert.equal(first.output.sequence, 1);
  const second = controlStep({state: first.state, ...dryOutside(4000), now_ms: 4000, config});
  assert.equal(second.output.phase, "PHASE_A");
  assert.equal(second.output.sequence, 2);
});

test("controller fault forces fan targets off", () => {
  const now = 1000;
  const result = controlStep({state: initialSystemState(0), ...dryOutside(now), now_ms: now, controller_fault: true, config});
  assert.equal(result.output.phase, "FAULT");
  assert.equal(result.output.reason, "CONTROLLER_FAULT");
  assert.equal(result.output.targets.room_a.mode, "OFF");
  assert.equal(result.output.targets.room_b.mode, "OFF");
});

test("wet outside air keeps pendulum off", () => {
  const now = 1000;
  const result = controlStep({
    state: initialSystemState(0),
    indoor: { temperature_c: 16, relative_humidity_pct: 60, timestamp_ms: now },
    outdoor: { temperature_c: 22, relative_humidity_pct: 90, timestamp_ms: now },
    now_ms: now,
    config,
  });
  assert.equal(result.output.ventilation_eligible, false);
  assert.equal(result.output.phase, "OFF");
});
