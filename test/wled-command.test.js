import test from "node:test";
import assert from "node:assert/strict";

import { buildWledDuePointCommand } from "../src/control/wled-command.js";

function physical({
  accepted = true,
  reason = "READY",
  fan1 = 60,
  fan2 = 60,
  fan3 = 68,
  route = "ROOM_A_SUPPLY_ROOM_B_EXHAUST",
  sequence = 42,
} = {}) {
  return {
    accepted,
    interlock_reason: reason,
    sequence,
    fans: {
      fan_1: fan1,
      fan_2: fan2,
      fan_3: fan3,
    },
    routing: {
      commanded_position: route,
    },
  };
}

test("maps safe physical 2+1 targets to DuePoint WLED JSON", () => {
  assert.deepEqual(buildWledDuePointCommand(physical()), {
    duepoint: {
      sequence: 42,
      supply_pct: 60,
      exhaust_pct: 68,
      route: "ROOM_A_SUPPLY_ROOM_B_EXHAUST",
    },
  });
});

test("all-off moving command stays all-off in WLED JSON", () => {
  const out = buildWledDuePointCommand(
    physical({
      reason: "ROUTE_MOVING",
      fan1: 0,
      fan2: 0,
      fan3: 0,
      route: "ROOM_B_SUPPLY_ROOM_A_EXHAUST",
      sequence: 43,
    }),
  );

  assert.equal(out.duepoint.supply_pct, 0);
  assert.equal(out.duepoint.exhaust_pct, 0);
  assert.equal(out.duepoint.sequence, 43);
});

test("rejects divergent supply-bank targets", () => {
  assert.throws(
    () => buildWledDuePointCommand(physical({ fan2: 59 })),
    /must match/,
  );
});

test("rejects unaccepted actuator outputs", () => {
  assert.throws(
    () =>
      buildWledDuePointCommand(
        physical({ accepted: false, reason: "COMMAND_EXPIRED" }),
      ),
    /not accepted/,
  );
});

test("rejects unknown route", () => {
  assert.throws(
    () => buildWledDuePointCommand(physical({ route: "UNKNOWN" })),
    /unsupported physical route/,
  );
});
