import { evaluateVentilation } from "./psychrometrics.js";
import { States, initialController, stepPendulum } from "./pendulum.js";

function isCycleActive(state) {
  return [
    States.STARTUP_DEADTIME,
    States.PHASE_A,
    States.PHASE_B,
    States.DEADTIME_TO_A,
    States.DEADTIME_TO_B,
  ].includes(state);
}

export function initialSystemState(nowMs = 0) {
  return {
    pendulum: initialController(nowMs),
    last_eligibility: null,
  };
}

export function controlStep({
  state,
  indoor,
  outdoor,
  now_ms,
  controller_fault = false,
  config,
}) {
  const currentlyVentilating = isCycleActive(state.pendulum.state);

  const eligibility = evaluateVentilation({
    indoor,
    outdoor,
    now_ms,
    currently_ventilating: currentlyVentilating,
    stale_after_ms: config.sensors.stale_after_ms,
    start_delta_gm3: config.ventilation.start_delta_gm3,
    stop_delta_gm3: config.ventilation.stop_delta_gm3,
    minimum_outdoor_temperature_c:
      config.ventilation.minimum_outdoor_temperature_c,
  });

  const result = stepPendulum({
    controller: state.pendulum,
    now_ms,
    enabled: eligibility.eligible,
    fault: controller_fault,
    phase_time_ms: config.pendulum.phase_time_ms,
    dead_time_ms: config.pendulum.dead_time_ms,
    pwm_pct: config.pendulum.pwm_pct,
    calibration: config.pendulum.calibration,
  });

  const commandTtlMs = config.actuator?.command_ttl_ms ?? 5000;

  return {
    state: {
      pendulum: result.controller,
      last_eligibility: {
        eligible: eligibility.eligible,
        reason: eligibility.reason,
        at_ms: now_ms,
      },
    },
    output: {
      phase: result.controller.state,
      sequence: result.controller.sequence,
      command_id: `${result.controller.sequence}:${now_ms}`,
      generated_at_ms: now_ms,
      valid_until_ms: now_ms + commandTtlMs,
      reason: controller_fault ? "CONTROLLER_FAULT" : eligibility.reason,
      ventilation_eligible: eligibility.eligible,
      delta_absolute_humidity_gm3:
        eligibility.delta_absolute_humidity_gm3 ?? null,
      targets: result.targets,
    },
  };
}
