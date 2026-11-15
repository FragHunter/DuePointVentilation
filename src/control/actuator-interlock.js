import {
  resolvePhysicalActuatorTargets,
  validateHardwareMap,
} from "./hardware-map.js";

function zeroFanTargets(config) {
  return Object.fromEntries(
    (config?.physical_fans || []).map((fan) => [fan.id, 0]),
  );
}

function safeRoute(config) {
  return config?.routing?.safe_position ?? "SAFE";
}

function finiteTimestamp(value, label) {
  if (!Number.isFinite(value)) {
    throw new TypeError(label + " must be finite");
  }
}

function validSequence(value) {
  return Number.isInteger(value) && value >= 0;
}

function timingConfig(config) {
  const travel = config?.servo_travel_ms;
  const settle = config?.servo_settle_ms ?? 0;

  if (travel !== null && travel !== undefined) {
    if (!Number.isFinite(travel) || travel <= 0) {
      throw new RangeError("servo_travel_ms must be null or > 0");
    }
  }
  if (!Number.isFinite(settle) || settle < 0) {
    throw new RangeError("servo_settle_ms must be >= 0");
  }

  return {
    calibrated: Number.isFinite(travel) && travel > 0,
    travel_ms: travel ?? null,
    settle_ms: settle,
    required_ms:
      Number.isFinite(travel) && travel > 0 ? travel + settle : null,
  };
}

export function initialActuatorState() {
  return {
    commanded_route: null,
    stable_route: null,
    route_started_at_ms: null,
    last_sequence: -1,
    last_command_id: null,
  };
}

export function buildFailsafeActuatorOutput({
  hardware_config,
  now_ms,
  reason,
  command = undefined,
  state = undefined,
}) {
  finiteTimestamp(now_ms, "now_ms");

  return {
    accepted: false,
    interlock_reason: reason,
    command_id: command?.command_id ?? null,
    sequence: validSequence(command?.sequence) ? command.sequence : null,
    generated_at_ms: command?.generated_at_ms ?? null,
    valid_until_ms: command?.valid_until_ms ?? null,
    evaluated_at_ms: now_ms,
    fans: zeroFanTargets(hardware_config),
    routing: {
      actuator_id: hardware_config?.routing?.actuator_id ?? null,
      mechanism: hardware_config?.routing?.mechanism ?? null,
      coupling: hardware_config?.routing?.coupling ?? null,
      mechanical_units: {
        ...(hardware_config?.routing?.mechanical_units || {}),
      },
      commanded_position:
        state?.commanded_route ?? safeRoute(hardware_config),
      stable_position: state?.stable_route ?? null,
      moving: false,
      timing_calibrated: false,
      required_settle_ms: null,
      fan_off_required_while_moving: true,
    },
  };
}

function validateCommand(command, nowMs) {
  if (!command || typeof command !== "object") {
    return "COMMAND_MISSING";
  }
  if (!validSequence(command.sequence)) {
    return "SEQUENCE_INVALID";
  }
  if (typeof command.command_id !== "string" || !command.command_id) {
    return "COMMAND_ID_INVALID";
  }
  if (!Number.isFinite(command.generated_at_ms)) {
    return "GENERATED_AT_INVALID";
  }
  if (!Number.isFinite(command.valid_until_ms)) {
    return "VALID_UNTIL_INVALID";
  }
  if (command.valid_until_ms < command.generated_at_ms) {
    return "TTL_INVALID";
  }
  if (nowMs > command.valid_until_ms) {
    return "COMMAND_EXPIRED";
  }
  return null;
}

export function actuatorStep({
  state,
  command,
  now_ms,
  hardware_config,
  actuator_config = {},
}) {
  finiteTimestamp(now_ms, "now_ms");

  const validation = validateHardwareMap(hardware_config);
  if (!validation.valid) {
    throw new Error(
      "hardware map invalid: " + validation.errors.join("; "),
    );
  }

  const current = state || initialActuatorState();
  const commandError = validateCommand(command, now_ms);
  if (commandError) {
    return {
      state: current,
      output: buildFailsafeActuatorOutput({
        hardware_config,
        now_ms,
        reason: commandError,
        command,
        state: current,
      }),
    };
  }

  if (
    validSequence(current.last_sequence) &&
    command.sequence < current.last_sequence
  ) {
    return {
      state: current,
      output: buildFailsafeActuatorOutput({
        hardware_config,
        now_ms,
        reason: "SEQUENCE_REGRESSION",
        command,
        state: current,
      }),
    };
  }

  const physical = resolvePhysicalActuatorTargets(
    {
      logicalTargets: command.targets,
      phase: command.phase,
    },
    hardware_config,
  );
  const timing = timingConfig(actuator_config);
  const desiredRoute = physical.routing.position;

  let next = {
    ...current,
    last_sequence: command.sequence,
    last_command_id: command.command_id,
  };

  if (desiredRoute !== current.commanded_route) {
    if (desiredRoute === current.stable_route) {
      next = {
        ...next,
        commanded_route: desiredRoute,
        route_started_at_ms: null,
      };
    } else {
      next = {
        ...next,
        commanded_route: desiredRoute,
        route_started_at_ms: now_ms,
      };
    }
  }

  let moving = next.stable_route !== desiredRoute;

  if (moving && timing.calibrated) {
    const started = next.route_started_at_ms ?? now_ms;
    if (now_ms - started >= timing.required_ms) {
      next = {
        ...next,
        stable_route: desiredRoute,
        route_started_at_ms: null,
      };
      moving = false;
    }
  }

  let reason = "READY";
  let fanTargets = { ...physical.fans };

  if (moving) {
    fanTargets = zeroFanTargets(hardware_config);
    reason = timing.calibrated
      ? "ROUTE_MOVING"
      : "SERVO_TIMING_UNCALIBRATED";
  }

  return {
    state: next,
    output: {
      accepted: true,
      interlock_reason: reason,
      command_id: command.command_id,
      sequence: command.sequence,
      generated_at_ms: command.generated_at_ms,
      valid_until_ms: command.valid_until_ms,
      evaluated_at_ms: now_ms,
      fans: fanTargets,
      routing: {
        actuator_id: physical.routing.actuator_id,
        mechanism: physical.routing.mechanism,
        coupling: physical.routing.coupling,
        mechanical_units: { ...physical.routing.mechanical_units },
        commanded_position: desiredRoute,
        stable_position: next.stable_route,
        moving,
        timing_calibrated: timing.calibrated,
        servo_travel_ms: timing.travel_ms,
        servo_settle_ms: timing.settle_ms,
        required_settle_ms: timing.required_ms,
        route_started_at_ms: next.route_started_at_ms,
        fan_off_required_while_moving: true,
      },
    },
  };
}
