window.VSLReact = window.VSLReact || {};

const REQUEST_STATUS = Object.freeze({
  IDLE: "idle",
  LOADING: "loading",
  SUCCESS: "success",
  ERROR: "error",
});

function makeRequestState() {
  return {
    status: REQUEST_STATUS.IDLE,
    data: null,
    error: null,
  };
}

function requestIdle() {
  return { status: REQUEST_STATUS.IDLE, data: null, error: null };
}

function requestLoading(prevData = null) {
  return { status: REQUEST_STATUS.LOADING, data: prevData, error: null };
}

function requestSuccess(data) {
  return { status: REQUEST_STATUS.SUCCESS, data: data, error: null };
}

function requestError(err, prevData = null) {
  return { status: REQUEST_STATUS.ERROR, data: prevData, error: err };
}

function ErrorEnvelopePanel({ error }) {
  if (!error) return null;
  const envelope = error.envelope || null;
  const code = envelope && envelope.code ? envelope.code : "request_error";
  const message = envelope && envelope.message ? envelope.message : (error.message || "Request failed.");
  const details = envelope && envelope.details ? envelope.details : null;

  return (
    <div style={{
      marginTop: "1rem",
      padding: "0.75rem",
      border: "1px solid #ef4444",
      borderRadius: "10px",
      background: "#fef2f2",
      color: "#7f1d1d",
    }}>
      <div><strong>Error Code:</strong> <code>{code}</code></div>
      <div><strong>Message:</strong> {message}</div>
      {details ? (
        <pre style={{
          marginTop: "0.5rem",
          whiteSpace: "pre-wrap",
          background: "#fff",
          border: "1px solid #fecaca",
          borderRadius: "8px",
          padding: "0.5rem",
          color: "#7f1d1d",
        }}>
          {JSON.stringify(details, null, 2)}
        </pre>
      ) : null}
    </div>
  );
}

window.VSLReact.REQUEST_STATUS = REQUEST_STATUS;
window.VSLReact.makeRequestState = makeRequestState;
window.VSLReact.requestIdle = requestIdle;
window.VSLReact.requestLoading = requestLoading;
window.VSLReact.requestSuccess = requestSuccess;
window.VSLReact.requestError = requestError;
window.VSLReact.ErrorEnvelopePanel = ErrorEnvelopePanel;
