import React, { useEffect, useState } from "react";
import { Box, Button, Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";

const DummyLogin = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const navigate = useNavigate(); // Hook for navigation

  const handleLogin = () => {
    window.location.href = "https://code-summarizer.onrender.com/github-login";
  };

  useEffect(() => {
    const query = new URLSearchParams(window.location.search);
    const access_token = query.get("access_token");

    if (access_token) {
      localStorage.setItem("token", access_token);
      console.log("Access Token:", access_token);
      setIsLoggedIn(true); // Mark user as logged in
      alert("Successfully logged in! 🎉"); // Show success popup
      navigate("/"); // Redirect to Home.js
    } else if (localStorage.getItem("token")) {
      setIsLoggedIn(true); // User is already logged in
    }
  }, [navigate]); // Include navigate to avoid dependency issues

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        flexDirection: "column",
        backgroundColor: "#0d1117", // GitHub dark theme background
        color: "white",
        textAlign: "center",
        position: "relative", // Required for absolute positioning of the Home button
      }}
    >
      {/* Home Button (Top Right) */}
      <Button
        variant="contained"
        onClick={() => navigate("/")}
        sx={{
          position: "absolute",
          top: 20,
          right: 20,
          backgroundColor: "green",
          color: "white",
          fontWeight: "bold",
          borderRadius: "20px",
          "&:hover": { backgroundColor: "darkgreen" },
        }}
      >
        Home
      </Button>

      {isLoggedIn ? (
        // Show Welcome Message if Logged In
        <Typography variant="h4" sx={{ fontWeight: "bold", mb: 2, color: "green" }}>
          Welcome to Code Essence 🎉
        </Typography>
      ) : (
        // Show Login Button if Not Logged In
        <>
          <Typography variant="h4" sx={{ fontWeight: "bold", mb: 2 }}>
            Sign in to <span style={{ color: "green" }}>Code Essence</span>
          </Typography>

          <Button
            variant="contained"
            sx={{
              backgroundColor: "#2ea44f",
              color: "white",
              padding: "10px 20px",
              borderRadius: "10px",
              fontWeight: "bold",
              "&:hover": { backgroundColor: "#22863a" },
            }}
            onClick={handleLogin}
          >
            Login with GitHub
          </Button>
        </>
      )}
    </Box>
  );
};

export default DummyLogin;
