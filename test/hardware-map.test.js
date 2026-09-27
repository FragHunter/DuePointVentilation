import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

import {
  resolvePhysicalActuatorTargets,
  resolvePhysicalFanTargets,
  validateHardwareMap,
} from "../src/control/hardware-map.js";

const config = JSON.parse(
  readFileSync(
    new URL("../config/hardware/gl-c-211wl-three-fan.json", import.meta.url),
  ),
);

test("servo-routed 2+1 production map is structurally valid", () => {
  const result = validateHardwareMap(config);
  assert.equal(result.valid, true, result.errors.join("; "));
});



test("V0.3 routing requires two distinct full-area T-diverter units", () => {
  assert.equal(config.routing.mechanism, "coupled_dual_t_diverter");
  assert.equal(config.routing.coupling, "single_servo_linkage");
  assert.deepEqual(config.routing.mechanical_units, {
    supply: "supply_t_diverter",
    exhaust: "exhaust_t_diverter",
  });

  const invalid = structuredClone(config);
  invalid.routing.mechanism = "coupled_double_diverter";
  const result = validateHardwareMap(invalid);
  assert.equal(result.valid, false);
  assert.ok(
    result.errors.some((error) =>
      error.includes("coupled_dual_t_diverter"),
    ),
  );
});

test("phase A drives two parallel supply fans and one exhaust fan", () => {
  const result = resolvePhysicalActuatorTargets(
    {
      phase: "PHASE_A",
      logicalTargets: {
        room_a: { intake_pct: 58, exhaust_pct: 0 },
        room_b: { intake_pct: 0, exhaust_pct: 73 },
      },
    },
    config,
  );

  assert.deepEqual(result.fans, {
    fan_1: 58,
    fan_2: 58,
    fan_3: 73,
  });
  assert.equal(
    result.routing.position,
    "ROOM_A_SUPPLY_ROOM_B_EXHAUST",
  );
  assert.equal(result.routing.mechanism, "coupled_dual_t_diverter");
  assert.equal(result.routing.coupling, "single_servo_linkage");
  assert.deepEqual(result.routing.mechanical_units, {
    supply: "supply_t_diverter",
    exhaust: "exhaust_t_diverter",
  });
});

test("phase B swaps room routing without reversing fan banks", () => {
  const result = resolvePhysicalActuatorTargets(
    {
      phase: "PHASE_B",
      logicalTargets: {
        room_a: { intake_pct: 0, exhaust_pct: 66 },
        room_b: { intake_pct: 54, exhaust_pct: 0 },
      },
    },
    config,
  );

  assert.deepEqual(result.fans, {
    fan_1: 54,
    fan_2: 54,
    fan_3: 66,
  });
  assert.equal(
    result.routing.position,
    "ROOM_B_SUPPLY_ROOM_A_EXHAUST",
  );
});

test("dead-time keeps all fans off while pre-positioning the next route", () => {
  const result = resolvePhysicalActuatorTargets(
    {
      phase: "DEADTIME_TO_B",
      logicalTargets: {
        room_a: { intake_pct: 0, exhaust_pct: 0 },
        room_b: { intake_pct: 0, exhaust_pct: 0 },
      },
    },
    config,
  );

  assert.deepEqual(result.fans, {
    fan_1: 0,
    fan_2: 0,
    fan_3: 0,
  });
  assert.equal(
    result.routing.position,
    "ROOM_B_SUPPLY_ROOM_A_EXHAUST",
  );
  assert.equal(result.routing.fan_off_required_while_moving, true);
});

test("active phase rejects logical commands that disagree with damper routing", () => {
  assert.throws(
    () =>
      resolvePhysicalActuatorTargets(
        {
          phase: "PHASE_A",
          logicalTargets: {
            room_a: { intake_pct: 40, exhaust_pct: 20 },
            room_b: { intake_pct: 0, exhaust_pct: 55 },
          },
        },
        config,
      ),
    /do not match servo routing/,
  );
});

test("compatibility fan-only resolver returns physical PWM targets", () => {
  const fans = resolvePhysicalFanTargets(
    {
      room_a: { intake_pct: 42, exhaust_pct: 0 },
      room_b: { intake_pct: 0, exhaust_pct: 64 },
    },
    config,
    "PHASE_A",
  );

  assert.deepEqual(fans, {
    fan_1: 42,
    fan_2: 42,
    fan_3: 64,
  });
});

test("fan group overlap is rejected", () => {
  const invalid = structuredClone(config);
  invalid.fan_groups.exhaust_bank.members = ["fan_2"];

  const result = validateHardwareMap(invalid);
  assert.equal(result.valid, false);
  assert.ok(
    result.errors.some((error) =>
      error.includes("must not belong to more than one fan group"),
    ),
  );
});
