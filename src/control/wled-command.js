function pct(value, label) {
  if (!Number.isFinite(value) || value < 0 || value > 100) {
    throw new RangeError(label + " must be within 0..100");
  }
  return Math.round(value);
}

export function buildWledDuePointCommand(physicalOutput) {
  if (!physicalOutput || typeof physicalOutput !== "object") {
    throw new TypeError("physical actuator output is required");
  }

  if (physicalOutput.accepted !== true) {
    throw new Error(
      "physical actuator output is not accepted: " +
        String(physicalOutput.interlock_reason ?? "unknown"),
    );
  }

  const fans = physicalOutput.fans || {};
  const fan1 = pct(fans.fan_1, "fan_1");
  const fan2 = pct(fans.fan_2, "fan_2");
  const fan3 = pct(fans.fan_3, "fan_3");

  if (fan1 !== fan2) {
    throw new Error(
      "supply-bank physical targets diverge; fan_1 and fan_2 must match",
    );
  }

  const route = physicalOutput.routing?.commanded_position;
  if (
    route !== "ROOM_A_SUPPLY_ROOM_B_EXHAUST" &&
    route !== "ROOM_B_SUPPLY_ROOM_A_EXHAUST" &&
    route !== "SAFE"
  ) {
    throw new Error("unsupported physical route: " + String(route));
  }

  if (
    !Number.isInteger(physicalOutput.sequence) ||
    physicalOutput.sequence < 0
  ) {
    throw new Error("physical actuator sequence is invalid");
  }

  return {
    duepoint: {
      sequence: physicalOutput.sequence,
      supply_pct: fan1,
      exhaust_pct: fan3,
      route,
    },
  };
}
