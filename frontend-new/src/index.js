import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import App from "./App";
import SummarySelector from "./SummarySelector";
import LoginPage from "./LoginPage"; // Ensure this file exists
import Profile from "./Profile"; // Ensure this file exists

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <Router>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/summary-selector" element={<SummarySelector />} />
        <Route path="/login" element={<LoginPage />} /> {/* Login Page */}
        <Route path="/profile" element={<Profile />} /> {/* User Profile */}
      </Routes>
    </Router>
  </React.StrictMode>
);

