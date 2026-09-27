import test from "node:test";
import assert from "node:assert/strict";

import {
  absoluteHumidityGm3,
  dewPointC,
  evaluateVentilation,
} from "../src/control/psychrometrics.js";

test("20 C / 50 % RH gives plausible psychrometric values", () => {
  assert.ok(Math.abs(dewPointC(20, 50) - 9.26) < 0.15);
  assert.ok(Math.abs(absoluteHumidityGm3(20, 50) - 8.62) < 0.15);
});

test("drier outdoor air enables ventilation", () => {
  const now = 1_000_000;
  const result = evaluateVentilation({
    indoor: { temperature_c: 18, relative_humidity_pct: 75, timestamp_ms: now },
    outdoor: { temperature_c: 10, relative_humidity_pct: 60, timestamp_ms: now },
    now_ms: now,
  });
  assert.equal(result.eligible, true);
  assert.equal(result.reason, "OUTSIDE_AIR_DRIER");
  assert.ok(result.delta_absolute_humidity_gm3 >= 1);
});

test("stale outside sensor inhibits automatic ventilation", () => {
  const now = 1_000_000;
  const result = evaluateVentilation({
    indoor: { temperature_c: 18, relative_humidity_pct: 75, timestamp_ms: now },
    outdoor: { temperature_c: 10, relative_humidity_pct: 60, timestamp_ms: now - 181000 },
    now_ms: now,
  });
  assert.equal(result.eligible, false);
  assert.equal(result.reason, "OUTDOOR_SENSOR_STALE");
});

test("hysteresis uses lower stop threshold while already ventilating", () => {
  const now = 1_000_000;
  const input = {
    indoor: { temperature_c: 20, relative_humidity_pct: 55, timestamp_ms: now },
    outdoor: { temperature_c: 19, relative_humidity_pct: 55, timestamp_ms: now },
    now_ms: now,
    start_delta_gm3: 1.0,
    stop_delta_gm3: 0.2,
  };
  const stopped = evaluateVentilation({ ...input, currently_ventilating: false });
  const running = evaluateVentilation({ ...input, currently_ventilating: true });
  assert.equal(stopped.eligible, false);
  assert.equal(running.eligible, true);
});
