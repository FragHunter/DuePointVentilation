export const LogicalFanRoles = Object.freeze([
  "room_a_supply",
  "room_a_exhaust",
  "room_b_supply",
  "room_b_exhaust",
]);

const ActivePhases = Object.freeze({
  PHASE_A: {
    supplyRole: "room_a_supply",
    exhaustRole: "room_b_exhaust",
  },
  PHASE_B: {
    supplyRole: "room_b_supply",
    exhaustRole: "room_a_exhaust",
  },
});

function knownFanIds(config) {
  return new Set((config.physical_fans || []).map((fan) => fan.id));
}

function logicalRoleTargets(logicalTargets) {
  return {
    room_a_supply: logicalTargets?.room_a?.intake_pct ?? 0,
    room_a_exhaust: logicalTargets?.room_a?.exhaust_pct ?? 0,
    room_b_supply: logicalTargets?.room_b?.intake_pct ?? 0,
    room_b_exhaust: logicalTargets?.room_b?.exhaust_pct ?? 0,
  };
}

function groupMembers(config, groupId) {
  return config.fan_groups?.[groupId]?.members || [];
}

function validateServoRouted2Plus1(config, errors) {
  const ids = knownFanIds(config);
  const supplyMembers = groupMembers(config, "supply_bank");
  const exhaustMembers = groupMembers(config, "exhaust_bank");

  if (supplyMembers.length !== 2) {
    errors.push(
      "servo_routed_2plus1 requires exactly 2 fans in supply_bank",
    );
  }
  if (exhaustMembers.length !== 1) {
    errors.push(
      "servo_routed_2plus1 requires exactly 1 fan in exhaust_bank",
    );
  }

  const allMembers = [...supplyMembers, ...exhaustMembers];
  const uniqueMembers = new Set(allMembers);

  if (uniqueMembers.size !== allMembers.length) {
    errors.push("a physical fan must not belong to more than one fan group");
  }

  for (const fanId of allMembers) {
    if (!ids.has(fanId)) {
      errors.push("fan group references unknown fan " + fanId);
    }
  }

  for (const fanId of ids) {
    if (!uniqueMembers.has(fanId)) {
      errors.push("physical fan " + fanId + " is not assigned to a fan group");
    }
  }

  const mapping = config.logical_role_mapping || {};
  const expectedMapping = {
    room_a_supply: "supply_bank",
    room_b_supply: "supply_bank",
    room_a_exhaust: "exhaust_bank",
    room_b_exhaust: "exhaust_bank",
  };

  for (const [role, expectedGroup] of Object.entries(expectedMapping)) {
    if (mapping[role] !== expectedGroup) {
      errors.push(
        "logical role " + role + " must map to " + expectedGroup,
      );
    }
  }

  const routing = config.routing;
  if (!routing || routing.mechanism !== "coupled_double_diverter") {
    errors.push("servo_routed_2plus1 requires a coupled_double_diverter");
  }
  if (routing?.fan_off_required_while_moving !== true) {
    errors.push("routing must require fan-off while the servo is moving");
  }

  for (const state of [
    "OFF",
    "FAULT",
    "STARTUP_DEADTIME",
    "PHASE_A",
    "DEADTIME_TO_B",
    "PHASE_B",
    "DEADTIME_TO_A",
  ]) {
    if (!routing?.positions?.[state]) {
      errors.push("routing position is missing for " + state);
    }
  }
}

export function validateHardwareMap(config) {
  const errors = [];

  if (!config || typeof config !== "object") {
    return { valid: false, errors: ["hardware map is missing"] };
  }

  const fans = config.physical_fans || [];
  if (fans.length !== 3) {
    errors.push("expected 3 physical fans, got " + fans.length);
  }

  const ids = knownFanIds(config);
  if (ids.size !== fans.length) {
    errors.push("physical fan IDs must be unique");
  }

  if (config.topology === "servo_routed_2plus1") {
    validateServoRouted2Plus1(config, errors);
  } else {
    errors.push(
      "unsupported or unresolved hardware topology: " +
        String(config.topology ?? "missing"),
    );
  }

  return { valid: errors.length === 0, errors };
}

function assertActiveTargetsMatchPhase(roles, phase) {
  const expected = ActivePhases[phase];
  if (!expected) return;

  const active = Object.entries(roles)
    .filter(([, value]) => value > 0)
    .map(([role]) => role)
    .sort();

  const expectedActive = [expected.supplyRole, expected.exhaustRole].sort();

  if (
    active.length !== expectedActive.length ||
    active.some((role, index) => role !== expectedActive[index])
  ) {
    throw new Error(
      phase +
        " logical targets do not match servo routing: active roles=" +
        active.join(","),
    );
  }
}

function targetForRole(roles, role) {
  const value = roles[role];
  if (!Number.isFinite(value) || value < 0 || value > 100) {
    throw new RangeError("logical role " + role + " target must be within 0..100");
  }
  return value;
}

export function resolvePhysicalActuatorTargets(
  { logicalTargets, phase },
  config,
) {
  const validation = validateHardwareMap(config);
  if (!validation.valid) {
    throw new Error(
      "hardware map invalid: " + validation.errors.join("; "),
    );
  }

  const roles = logicalRoleTargets(logicalTargets);
  const fans = Object.fromEntries(
    config.physical_fans.map((fan) => [fan.id, 0]),
  );

  const routingPosition =
    config.routing.positions[phase] ?? config.routing.safe_position;

  if (!Object.hasOwn(config.routing.positions, phase)) {
    throw new Error("no routing position configured for phase " + phase);
  }

  if (!ActivePhases[phase]) {
    return {
      fans,
      routing: {
        actuator_id: config.routing.actuator_id,
        position: routingPosition,
        fan_off_required_while_moving:
          config.routing.fan_off_required_while_moving,
      },
    };
  }

  assertActiveTargetsMatchPhase(roles, phase);

  const { supplyRole, exhaustRole } = ActivePhases[phase];
  const supplyTarget = targetForRole(roles, supplyRole);
  const exhaustTarget = targetForRole(roles, exhaustRole);

  for (const fanId of groupMembers(config, "supply_bank")) {
    fans[fanId] = supplyTarget;
  }
  for (const fanId of groupMembers(config, "exhaust_bank")) {
    fans[fanId] = exhaustTarget;
  }

  return {
    fans,
    routing: {
      actuator_id: config.routing.actuator_id,
      position: routingPosition,
      fan_off_required_while_moving:
        config.routing.fan_off_required_while_moving,
    },
  };
}

export function resolvePhysicalFanTargets(logicalTargets, config, phase) {
  return resolvePhysicalActuatorTargets(
    { logicalTargets, phase },
    config,
  ).fans;
}
