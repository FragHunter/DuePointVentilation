import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

import {
  resolvePhysicalFanTargets,
  validateHardwareMap,
} from "../src/control/hardware-map.js";

const unresolved = JSON.parse(
  readFileSync(
    new URL("../config/hardware/gl-c-211wl-three-fan.json", import.meta.url),
  ),
);

test("three-fan production map stays invalid until role mapping is explicit", () => {
  const result = validateHardwareMap(unresolved);
  assert.equal(result.valid, false);
  assert.equal(
    result.errors.filter((error) => error.includes("is not mapped")).length,
    4,
  );
});

test("sharing one fan requires explicit mechanical acknowledgement", () => {
  const config = structuredClone(unresolved);
  config.logical_role_mapping = {
    room_a_supply: "fan_1",
    room_a_exhaust: "fan_1",
    room_b_supply: "fan_2",
    room_b_exhaust: "fan_3",
  };

  const result = validateHardwareMap(config);
  assert.equal(result.valid, false);
  assert.ok(
    result.errors.some((error) => error.includes("mechanical acknowledgement")),
  );
});

test("explicitly acknowledged sharing resolves non-overlapping phase commands", () => {
  const config = structuredClone(unresolved);
  config.logical_role_mapping = {
    room_a_supply: "fan_1",
    room_a_exhaust: "fan_1",
    room_b_supply: "fan_2",
    room_b_exhaust: "fan_3",
  };
  config.shared_fan_acknowledgements = { fan_1: true };

  const physical = resolvePhysicalFanTargets(
    {
      room_a: { intake_pct: 65, exhaust_pct: 0 },
      room_b: { intake_pct: 0, exhaust_pct: 70 },
    },
    config,
  );

  assert.deepEqual(physical, {
    fan_1: 65,
    fan_2: 0,
    fan_3: 70,
  });
});

test("shared fan fails safe when two logical roles command it simultaneously", () => {
  const config = structuredClone(unresolved);
  config.logical_role_mapping = {
    room_a_supply: "fan_1",
    room_a_exhaust: "fan_1",
    room_b_supply: "fan_2",
    room_b_exhaust: "fan_3",
  };
  config.shared_fan_acknowledgements = { fan_1: true };

  assert.throws(
    () =>
      resolvePhysicalFanTargets(
        {
          room_a: { intake_pct: 60, exhaust_pct: 50 },
          room_b: { intake_pct: 0, exhaust_pct: 70 },
        },
        config,
      ),
    /simultaneous logical commands/,
  );
});
