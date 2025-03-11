import React, { useEffect, useState } from "react";
import { Box, Button, Typography } from "@mui/material";

const DummyLogin = () => {
  const [user, setUser] = useState(null);

  const handleLogin = () => {
    window.location.href = "https://code-summarizer.onrender.com/github-login";
  };

  useEffect(() => {
    const query = new URLSearchParams(window.location.search);
    const access_token = query.get("access_token"); 

    if (access_token) {
      localStorage.setItem("token", access_token);
      console.log("Access Token:", access_token);
      // You can fetch user details from GitHub API if needed
    }
  }, []);

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
      }}
    >
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
    </Box>
  );
};

export default DummyLogin;
