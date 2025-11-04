# Task 6 — React.js Front-End (Light Version)

**Goal:** Demonstrate ability to consume an API and render results in a simple, functional UI.

**Requirements:**
- Create a **minimal React.js app** in `/frontend/` (Vite or Create-React-App).
- Build a **single component or page** that:
  - Calls `GET /health` to confirm connectivity.
  - Calls `GET /orders/{order_id}` (you may hard-code an order ID or make it a simple input).
  - Displays the returned JSON **as formatted text or a small table**.
- No routing, CSS framework, or complex styling required.
- Must run locally via `npm install && npm start`.

**Evaluation (5 pts):**
- (3) Successful fetch and render of API data.
- (2) Code clarity and correct React hooks usage (`useEffect`, `useState`).

**Optional (no extra credit):**
If desired, allow user to input a different order ID dynamically.
