import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

import {
  controlStep,
  initialSystemState,
} from "../src/control/controller.js";

const config = JSON.parse(
  readFileSync(new URL("../config/defaults.json", import.meta.url)),
);

const dryOutside = (now) => ({
  indoor: { temperature_c: 18, relative_humidity_pct: 75, timestamp_ms: now },
  outdoor: { temperature_c: 10, relative_humidity_pct: 60, timestamp_ms: now },
});

test("integrated controller starts pendulum when drying is useful", () => {
  const now = 1000;
  const measurements = dryOutside(now);
  const result = controlStep({
    state: initialSystemState(0),
    ...measurements,
    now_ms: now,
    config,
  });

  assert.equal(result.output.ventilation_eligible, true);
  assert.equal(result.output.phase, "PHASE_A");
  assert.equal(result.output.targets.room_a.mode, "SUPPLY");
  assert.equal(result.output.targets.room_b.mode, "EXHAUST");
});

test("controller fault forces fan targets off", () => {
  const now = 1000;
  const measurements = dryOutside(now);
  const result = controlStep({
    state: initialSystemState(0),
    ...measurements,
    now_ms: now,
    controller_fault: true,
    config,
  });

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
