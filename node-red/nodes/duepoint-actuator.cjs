const fs = require("node:fs");
const path = require("node:path");
const { pathToFileURL } = require("node:url");

module.exports = function registerDuePointActuator(RED) {
  function DuePointActuatorNode(config) {
    RED.nodes.createNode(this, config);
    const node = this;

    const root = path.resolve(__dirname, "../..");
    const defaultsPath = path.join(root, "config", "defaults.json");
    const hardwarePath = path.join(
      root,
      "config",
      "hardware",
      "gl-c-211wl-three-fan.json",
    );
    const interlockUrl = pathToFileURL(
      path.join(root, "src", "control", "actuator-interlock.js"),
    ).href;

    const defaults = JSON.parse(fs.readFileSync(defaultsPath, "utf8"));
    const hardware = JSON.parse(fs.readFileSync(hardwarePath, "utf8"));
    let modulePromise;

    function interlockModule() {
      if (!modulePromise) modulePromise = import(interlockUrl);
      return modulePromise;
    }

    node.on("input", async (msg, send, done) => {
      const now = Number.isFinite(msg.now_ms)
        ? msg.now_ms
        : Number.isFinite(msg.payload?.now_ms)
          ? msg.payload.now_ms
          : Date.now();

      try {
        const interlock = await interlockModule();
        const previous =
          node.context().get("duepoint_actuator_state") ||
          interlock.initialActuatorState();

        const result = interlock.actuatorStep({
          state: previous,
          command: msg.payload,
          now_ms: now,
          hardware_config: msg.hardware_config || hardware,
          actuator_config: msg.actuator_config || defaults.actuator,
        });

        node.context().set("duepoint_actuator_state", result.state);
        msg.logical_command = msg.payload;
        msg.payload = result.output;

        const status = result.output.interlock_reason;
        if (status === "READY") {
          node.status({ fill: "green", shape: "dot", text: "route ready" });
        } else if (
          status === "ROUTE_MOVING" ||
          status === "SERVO_TIMING_UNCALIBRATED"
        ) {
          node.status({ fill: "yellow", shape: "ring", text: status });
        } else {
          node.status({ fill: "red", shape: "ring", text: status });
        }

        send(msg);
        if (done) done();
      } catch (error) {
        try {
          const interlock = await interlockModule();
          msg.logical_command = msg.payload;
          msg.payload = interlock.buildFailsafeActuatorOutput({
            hardware_config: msg.hardware_config || hardware,
            now_ms: now,
            reason: "ACTUATOR_ADAPTER_ERROR",
            command: msg.logical_command,
            state: node.context().get("duepoint_actuator_state"),
          });
          node.status({
            fill: "red",
            shape: "ring",
            text: "ACTUATOR_ADAPTER_ERROR",
          });
          send(msg);
        } catch (failsafeError) {
          node.error(failsafeError, msg);
        }

        if (done) done(error);
        else node.error(error, msg);
      }
    });

    node.on("close", () => {
      modulePromise = undefined;
    });
  }

  RED.nodes.registerType("duepoint-actuator", DuePointActuatorNode);
};
