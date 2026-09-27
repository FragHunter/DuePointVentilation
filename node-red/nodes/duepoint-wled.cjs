const path = require("node:path");
const { pathToFileURL } = require("node:url");

module.exports = function registerDuePointWled(RED) {
  function DuePointWledNode(config) {
    RED.nodes.createNode(this, config);
    const node = this;

    const root = path.resolve(__dirname, "../..");
    const mapperUrl = pathToFileURL(
      path.join(root, "src", "control", "wled-command.js"),
    ).href;
    let mapperPromise;

    function mapperModule() {
      if (!mapperPromise) mapperPromise = import(mapperUrl);
      return mapperPromise;
    }

    node.on("input", async (msg, send, done) => {
      try {
        const mapper = await mapperModule();
        const endpoint = String(msg.wled_endpoint || config.endpoint || "").trim();
        if (!endpoint) throw new Error("WLED endpoint is not configured");
        if (!/^https?:\/\//i.test(endpoint)) {
          throw new Error("WLED endpoint must start with http:// or https://");
        }

        const payload = mapper.buildWledDuePointCommand(msg.payload);
        msg.physical_actuator = msg.payload;
        msg.payload = payload;
        msg.method = "POST";
        msg.url = endpoint.replace(/\/+$/, "") + "/json/state";
        msg.headers = {
          ...(msg.headers || {}),
          "content-type": "application/json",
        };

        node.status({ fill: "green", shape: "dot", text: "WLED command ready" });
        send(msg);
        if (done) done();
      } catch (error) {
        node.status({ fill: "red", shape: "ring", text: "WLED command blocked" });
        if (done) done(error);
        else node.error(error, msg);
      }
    });

    node.on("close", () => {
      mapperPromise = undefined;
    });
  }

  RED.nodes.registerType("duepoint-wled", DuePointWledNode);
};
