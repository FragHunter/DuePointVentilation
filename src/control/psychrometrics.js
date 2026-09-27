const MAGNUS_A = 17.62;
const MAGNUS_B_C = 243.12;

export function validateMeasurement(measurement) {
  if (!measurement || typeof measurement !== "object") {
    return { valid: false, reason: "MISSING_MEASUREMENT" };
  }
  const { temperature_c, relative_humidity_pct, timestamp_ms } = measurement;
  if (!Number.isFinite(temperature_c) || temperature_c < -50 || temperature_c > 80) {
    return { valid: false, reason: "TEMPERATURE_INVALID" };
  }
  if (!Number.isFinite(relative_humidity_pct) || relative_humidity_pct <= 0 || relative_humidity_pct > 100) {
    return { valid: false, reason: "HUMIDITY_INVALID" };
  }
  if (!Number.isFinite(timestamp_ms) || timestamp_ms < 0) {
    return { valid: false, reason: "TIMESTAMP_INVALID" };
  }
  return { valid: true, reason: "OK" };
}

export function saturationVaporPressureHpa(temperatureC) {
  return 6.112 * Math.exp(
    (MAGNUS_A * temperatureC) / (MAGNUS_B_C + temperatureC),
  );
}

export function vaporPressureHpa(temperatureC, relativeHumidityPct) {
  return saturationVaporPressureHpa(temperatureC) * relativeHumidityPct / 100;
}

export function absoluteHumidityGm3(temperatureC, relativeHumidityPct) {
  const e = vaporPressureHpa(temperatureC, relativeHumidityPct);
  return 216.7 * e / (temperatureC + 273.15);
}

export function dewPointC(temperatureC, relativeHumidityPct) {
  const gamma =
    Math.log(relativeHumidityPct / 100) +
    (MAGNUS_A * temperatureC) / (MAGNUS_B_C + temperatureC);
  return (MAGNUS_B_C * gamma) / (MAGNUS_A - gamma);
}

export function enrichMeasurement(measurement) {
  const validation = validateMeasurement(measurement);
  if (!validation.valid) {
    return { ...measurement, valid: false, validation_reason: validation.reason };
  }
  return {
    ...measurement,
    valid: true,
    validation_reason: "OK",
    dew_point_c: dewPointC(
      measurement.temperature_c,
      measurement.relative_humidity_pct,
    ),
    absolute_humidity_gm3: absoluteHumidityGm3(
      measurement.temperature_c,
      measurement.relative_humidity_pct,
    ),
  };
}

export function evaluateVentilation({
  indoor,
  outdoor,
  now_ms,
  currently_ventilating = false,
  stale_after_ms = 180000,
  start_delta_gm3 = 1.0,
  stop_delta_gm3 = 0.4,
  minimum_outdoor_temperature_c = -10,
}) {
  const inside = enrichMeasurement(indoor);
  const outside = enrichMeasurement(outdoor);

  if (!inside.valid) {
    return { eligible: false, reason: "INDOOR_SENSOR_INVALID", indoor: inside, outdoor: outside };
  }
  if (!outside.valid) {
    return { eligible: false, reason: "OUTDOOR_SENSOR_INVALID", indoor: inside, outdoor: outside };
  }

  if (!Number.isFinite(now_ms)) {
    throw new TypeError("now_ms must be a finite timestamp");
  }

  if (now_ms - inside.timestamp_ms > stale_after_ms) {
    return { eligible: false, reason: "INDOOR_SENSOR_STALE", indoor: inside, outdoor: outside };
  }
  if (now_ms - outside.timestamp_ms > stale_after_ms) {
    return { eligible: false, reason: "OUTDOOR_SENSOR_STALE", indoor: inside, outdoor: outside };
  }
  if (outside.temperature_c < minimum_outdoor_temperature_c) {
    return { eligible: false, reason: "OUTDOOR_TEMPERATURE_LOCKOUT", indoor: inside, outdoor: outside };
  }

  const delta = inside.absolute_humidity_gm3 - outside.absolute_humidity_gm3;
  const threshold = currently_ventilating ? stop_delta_gm3 : start_delta_gm3;
  const eligible = delta >= threshold;

  return {
    eligible,
    reason: eligible ? "OUTSIDE_AIR_DRIER" : "INSUFFICIENT_DRYING_POTENTIAL",
    delta_absolute_humidity_gm3: delta,
    threshold_gm3: threshold,
    indoor: inside,
    outdoor: outside,
  };
}
