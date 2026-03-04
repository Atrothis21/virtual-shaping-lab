(function attachVslApiClient(globalObj) {
  "use strict";

  /**
   * @typedef {Object} ApiErrorEnvelope
   * @property {string} [code]
   * @property {string} [message]
   * @property {Object<string, any>} [details]
   */

  /**
   * @typedef {Object} ApiRequestError
   * @property {number} status
   * @property {ApiErrorEnvelope | null} envelope
   * @property {string} message
   */

  /**
   * @typedef {Object} ApiClient
   * @property {(path: string, body: Object<string, any>) => Promise<any>} postJson
   * @property {(path: string) => Promise<any>} getJson
   * @property {(path: string) => string} buildUrl
   */

  function normalizeBase(baseUrl) {
    if (!baseUrl) return "";
    return String(baseUrl).replace(/\/+$/, "");
  }

  function toRequestError(status, envelope, fallbackMessage) {
    return {
      status: status,
      envelope: envelope,
      message:
        (envelope && envelope.message) ||
        fallbackMessage ||
        "Request failed.",
    };
  }

  async function parseJsonSafe(response) {
    try {
      return await response.json();
    } catch (_err) {
      return null;
    }
  }

  function createApiClient(options) {
    var opts = options || {};
    var baseUrl = normalizeBase(opts.baseUrl || "");

    async function handleResponse(response) {
      var payload = await parseJsonSafe(response);
      if (response.ok) {
        return payload;
      }
      throw toRequestError(
        response.status,
        payload && typeof payload === "object" ? payload : null,
        "API request failed."
      );
    }

    /** @type {ApiClient} */
    var client = {
      buildUrl: function buildUrl(path) {
        var cleaned = String(path || "").replace(/^\/+/, "");
        return baseUrl ? baseUrl + "/" + cleaned : "/" + cleaned;
      },
      postJson: async function postJson(path, body) {
        var url = client.buildUrl(path);
        var response = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body || {}),
        });
        return handleResponse(response);
      },
      getJson: async function getJson(path) {
        var url = client.buildUrl(path);
        var response = await fetch(url, { method: "GET" });
        return handleResponse(response);
      },
    };

    return client;
  }

  globalObj.VSLApi = {
    createApiClient: createApiClient,
  };
})(window);
