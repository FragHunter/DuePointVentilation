const fs = require("node:fs");
const path = require("node:path");
const { pathToFileURL } = require("node:url");

module.exports = function registerDuePointControl(RED) {
  function DuePointControlNode(config) {
    RED.nodes.createNode(this, config);
    const node = this;

    const root = path.resolve(__dirname, "../..");
    const defaultsPath = path.join(root, "config", "defaults.json");
    const controllerUrl = pathToFileURL(
      path.join(root, "src", "control", "controller.js"),
    ).href;

    const defaults = JSON.parse(fs.readFileSync(defaultsPath, "utf8"));
    let controllerPromise;

    function controllerModule() {
      if (!controllerPromise) controllerPromise = import(controllerUrl);
      return controllerPromise;
    }

    node.on("input", async (msg, send, done) => {
      try {
        const ctl = await controllerModule();
        const input = msg.payload || {};
        const now = Number.isFinite(input.now_ms) ? input.now_ms : Date.now();
        const state = node.context().get("duepoint_state") || ctl.initialSystemState(now);

        const result = ctl.controlStep({
          state,
          indoor: input.indoor,
          outdoor: input.outdoor,
          now_ms: now,
          controller_fault: Boolean(input.controller_fault),
          config: input.config || defaults,
        });

        node.context().set("duepoint_state", result.state);
        msg.payload = result.output;
        msg.duepoint_state = result.state;
        send(msg);
        if (done) done();
      } catch (error) {
        node.status({ fill: "red", shape: "ring", text: "control error" });
        if (done) done(error);
        else node.error(error, msg);
      }
    });

    node.on("close", () => {
      controllerPromise = undefined;
    });
  }

  RED.nodes.registerType("duepoint-control", DuePointControlNode);
};
