import React from "react";
import { Box, Button, Typography } from "@mui/material";

const Login = () => {
  const handleLogin = () => {
    const clientId = "YOUR_GITHUB_CLIENT_ID"; // Replace with your actual GitHub OAuth Client ID
    const redirectUri = "http://localhost:3000"; // Update to match your GitHub app's settings
    window.location.href = `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=user:email`;
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        flexDirection: "column",
        backgroundColor: "#0d1117", // GitHub dark background
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
          "&:hover": { backgroundColor: "#22863a" },
        }}
        onClick={handleLogin}
      >
        Login with GitHub
      </Button>
    </Box>
  );
};

export default Login;

