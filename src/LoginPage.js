import React from "react";
import { Box, Typography, Button } from "@mui/material";
import GoogleIcon from "@mui/icons-material/Google";
import GitHubIcon from "@mui/icons-material/GitHub";

function LoginPage() {
  const handleGoogleSignIn = () => {
    window.location.href = "https://accounts.google.com"; // Replace with actual Google OAuth URL
  };

  const handleGitHubSignIn = () => {
    window.location.href = "https://github.com/login"; // Replace with actual GitHub OAuth URL
  };

  return (
    <Box
      sx={{
        backgroundColor: "black",
        color: "white",
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        textAlign: "center",
        padding: "20px",
      }}
    >
      <Typography variant="h4" sx={{ mb: 2, fontWeight: "bold" }}>
        Login to Save Your Summary
      </Typography>

      {/* Google Login */}
      <Button
        variant="outlined"
        startIcon={<GoogleIcon />}
        onClick={handleGoogleSignIn}
        sx={{
          color: "white",
          border: "1px solid orange",
          borderRadius: "20px",
          padding: "10px 30px",
          fontWeight: "bold",
          mb: 2,
          "&:hover": {
            backgroundColor: "rgba(255, 165, 0, 0.2)",
            borderColor: "orange",
          },
        }}
      >
        Sign in with Google
      </Button>

      {/* GitHub Login */}
      <Button
        variant="outlined"
        startIcon={<GitHubIcon />}
        onClick={handleGitHubSignIn}
        sx={{
          color: "white",
          border: "1px solid orange",
          borderRadius: "20px",
          padding: "10px 30px",
          fontWeight: "bold",
          "&:hover": {
            backgroundColor: "rgba(255, 165, 0, 0.2)",
            borderColor: "orange",
          },
        }}
      >
        Sign in with GitHub
      </Button>
    </Box>
  );
}

export default LoginPage;
