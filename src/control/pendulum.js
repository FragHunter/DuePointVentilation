export const States = Object.freeze({
  OFF: "OFF",
  STARTUP_DEADTIME: "STARTUP_DEADTIME",
  PHASE_A: "PHASE_A",
  DEADTIME_TO_B: "DEADTIME_TO_B",
  PHASE_B: "PHASE_B",
  DEADTIME_TO_A: "DEADTIME_TO_A",
  FAULT: "FAULT",
});

function clampPct(value) {
  return Math.max(0, Math.min(100, value));
}

function factor(calibration, room, direction) {
  const value = calibration?.[room]?.[direction];
  return Number.isFinite(value) ? value : 1.0;
}

function calibrated(pwmPct, calibration, room, direction) {
  return clampPct(pwmPct * factor(calibration, room, direction));
}

export function targetsForState(state, pwmPct = 65, calibration = undefined) {
  const off = { intake_pct: 0, exhaust_pct: 0, mode: "OFF" };
  switch (state) {
    case States.PHASE_A:
      return {
        room_a: {
          intake_pct: calibrated(pwmPct, calibration, "room_a", "supply"),
          exhaust_pct: 0,
          mode: "SUPPLY",
        },
        room_b: {
          intake_pct: 0,
          exhaust_pct: calibrated(pwmPct, calibration, "room_b", "exhaust"),
          mode: "EXHAUST",
        },
      };
    case States.PHASE_B:
      return {
        room_a: {
          intake_pct: 0,
          exhaust_pct: calibrated(pwmPct, calibration, "room_a", "exhaust"),
          mode: "EXHAUST",
        },
        room_b: {
          intake_pct: calibrated(pwmPct, calibration, "room_b", "supply"),
          exhaust_pct: 0,
          mode: "SUPPLY",
        },
      };
    default:
      return { room_a: { ...off }, room_b: { ...off } };
  }
}

export function initialController(nowMs = 0) {
  return { state: States.OFF, entered_at_ms: nowMs, sequence: 0 };
}

export function stepPendulum({
  controller,
  now_ms,
  enabled,
  fault = false,
  phase_time_ms = 60000,
  dead_time_ms = 3000,
  pwm_pct = 65,
  calibration = undefined,
}) {
  if (!controller || !Object.values(States).includes(controller.state)) {
    throw new TypeError("controller state is invalid");
  }
  if (!Number.isFinite(now_ms) || !Number.isFinite(controller.entered_at_ms)) {
    throw new TypeError("timestamps must be finite");
  }
  if (phase_time_ms <= 0 || dead_time_ms < 0) {
    throw new RangeError("phase/dead-time configuration is invalid");
  }
  if (pwm_pct < 0 || pwm_pct > 100) {
    throw new RangeError("pwm_pct must be within 0..100");
  }

  let state = controller.state;
  let entered = controller.entered_at_ms;
  let sequence = Number.isInteger(controller.sequence) ? controller.sequence : 0;

  const enter = (next) => {
    if (state !== next) sequence += 1;
    state = next;
    entered = now_ms;
  };

  if (fault) {
    if (state !== States.FAULT) enter(States.FAULT);
  } else if (!enabled) {
    if (state !== States.OFF) enter(States.OFF);
  } else {
    const elapsed = Math.max(0, now_ms - entered);
    switch (state) {
      case States.OFF:
      case States.FAULT:
        enter(States.STARTUP_DEADTIME);
        break;
      case States.STARTUP_DEADTIME:
        if (elapsed >= dead_time_ms) enter(States.PHASE_A);
        break;
      case States.PHASE_A:
        if (elapsed >= phase_time_ms) enter(States.DEADTIME_TO_B);
        break;
      case States.DEADTIME_TO_B:
        if (elapsed >= dead_time_ms) enter(States.PHASE_B);
        break;
      case States.PHASE_B:
        if (elapsed >= phase_time_ms) enter(States.DEADTIME_TO_A);
        break;
      case States.DEADTIME_TO_A:
        if (elapsed >= dead_time_ms) enter(States.PHASE_A);
        break;
    }
  }

  return {
    controller: { state, entered_at_ms: entered, sequence },
    targets: targetsForState(state, pwm_pct, calibration),
  };
}
