import React, { useEffect, useState } from "react";

const API_BASE_URL = process.env.REACT_APP_API_URL;

function App() {
  const [health, setHealth] = useState(null);
  const [orderId, setOrderId] = useState("O00034");
  const [orderData, setOrderData] = useState(null);
  const [error, setError] = useState(null);

  // Fetch backend health when component loads
  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/health`);
        const data = await res.json();
        setHealth(data);
      } catch (err) {
        setError("Failed to reach backend: " + err.message);
      }
    };
    fetchHealth();
  }, []);

  // Fetch order by ID
  const fetchOrder = async () => {
    setError(null);
    setOrderData(null);
    try {
      const res = await fetch(`${API_BASE_URL}/orders/${orderId}`);
      if (!res.ok) throw new Error(`Order ${orderId} not found`);
      const data = await res.json();
      setOrderData(data);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div style={{ fontFamily: "sans-serif", padding: "2rem", maxWidth: "600px" }}>
      <h2>BXS ETL Frontend</h2>

      <section style={{ marginBottom: "2rem" }}>
        <h4>Backend Health</h4>
        <pre
          style={{
            background: "#f4f4f4",
            padding: "1rem",
            borderRadius: "8px",
            overflowX: "auto",
          }}
        >
          {health ? JSON.stringify(health, null, 2) : "Checking..."}
        </pre>
      </section>

      <section>
        <h4>Order Lookup</h4>
        <div style={{ marginBottom: "1rem" }}>
          <input
            value={orderId}
            onChange={(e) => setOrderId(e.target.value)}
            placeholder="Enter order ID"
            style={{ padding: "6px", marginRight: "10px", width: "200px" }}
          />
          <button onClick={fetchOrder} style={{ padding: "6px 12px" }}>
            Fetch
          </button>
        </div>

        {error && <p style={{ color: "red" }}>{error}</p>}

        {orderData && (
          <div>
            <h4>Order Details</h4>
            <table
              border="1"
              cellPadding="8"
              style={{ borderCollapse: "collapse", width: "100%" }}
            >
              <tbody>
                {Object.entries(orderData).map(([key, value]) => (
                  <tr key={key}>
                    <td style={{ fontWeight: "bold", background: "#fafafa" }}>
                      {key}
                    </td>
                    <td>{String(value)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

export default App;
