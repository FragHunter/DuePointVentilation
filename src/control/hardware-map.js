export const LogicalFanRoles = Object.freeze([
  "room_a_supply",
  "room_a_exhaust",
  "room_b_supply",
  "room_b_exhaust",
]);

function knownFanIds(config) {
  return new Set((config.physical_fans || []).map((fan) => fan.id));
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

  const mapping = config.logical_role_mapping || {};
  const fanToRoles = new Map();

  for (const role of LogicalFanRoles) {
    const fanId = mapping[role];
    if (!fanId) {
      errors.push("logical role " + role + " is not mapped");
      continue;
    }
    if (!ids.has(fanId)) {
      errors.push("logical role " + role + " references unknown fan " + fanId);
      continue;
    }
    const roles = fanToRoles.get(fanId) || [];
    roles.push(role);
    fanToRoles.set(fanId, roles);
  }

  for (const [fanId, roles] of fanToRoles) {
    if (roles.length <= 1) continue;
    const ack = config.shared_fan_acknowledgements?.[fanId];
    if (ack !== true) {
      errors.push(
        "physical fan " + fanId + " is shared by " + roles.join(", ") +
        " without explicit mechanical acknowledgement",
      );
    }
  }

  return { valid: errors.length === 0, errors };
}

function logicalRoleTargets(logicalTargets) {
  return {
    room_a_supply: logicalTargets?.room_a?.intake_pct ?? 0,
    room_a_exhaust: logicalTargets?.room_a?.exhaust_pct ?? 0,
    room_b_supply: logicalTargets?.room_b?.intake_pct ?? 0,
    room_b_exhaust: logicalTargets?.room_b?.exhaust_pct ?? 0,
  };
}

export function resolvePhysicalFanTargets(logicalTargets, config) {
  const validation = validateHardwareMap(config);
  if (!validation.valid) {
    throw new Error(
      "hardware map invalid: " + validation.errors.join("; "),
    );
  }

  const roles = logicalRoleTargets(logicalTargets);
  const result = Object.fromEntries(
    config.physical_fans.map((fan) => [fan.id, 0]),
  );

  const roleAssignmentsByFan = new Map();
  for (const role of LogicalFanRoles) {
    const fanId = config.logical_role_mapping[role];
    const value = roles[role];
    const assignments = roleAssignmentsByFan.get(fanId) || [];
    assignments.push({ role, value });
    roleAssignmentsByFan.set(fanId, assignments);
  }

  for (const [fanId, assignments] of roleAssignmentsByFan) {
    const active = assignments.filter(({ value }) => value > 0);
    if (active.length > 1) {
      throw new Error(
        "physical fan " + fanId +
        " receives simultaneous logical commands: " +
        active.map(({ role }) => role).join(", "),
      );
    }
    result[fanId] = active.length === 1 ? active[0].value : 0;
  }

  return result;
}
