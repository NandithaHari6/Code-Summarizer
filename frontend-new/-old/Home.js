import React, { useState } from "react";
import { Box, Typography, TextField, Button, Alert } from "@mui/material";
import { useNavigate } from "react-router-dom";

function Home() {
  const [repoURL, setRepoURL] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSummarize = () => {
    setError("");

    if (!repoURL.includes("github.com/")) {
      setError("Invalid GitHub repository URL. Please enter a valid URL.");
      return;
    }

    console.log("Navigating to SummarySelector with repoURL:", repoURL);
    navigate(`/summary-selector?repoURL=${encodeURIComponent(repoURL)}`);
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
        position: "relative",
      }}
    >
      {/* Profile Button (Top Left) */}
      <Button
        variant="contained"
        onClick={() => navigate("/profile")}
        sx={{
          position: "absolute",
          top: 20,
          left: 20,
          backgroundColor: "green",
          color: "white",
          fontWeight: "bold",
          borderRadius: "20px",
          "&:hover": { backgroundColor: "darkgreen" },
        }}
      >
        Profile
      </Button>

      {/* Login Button (Top Right) */}
      <Button
        variant="contained"
        onClick={() => (window.location.href = "http://localhost:3000/login")}
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
        Login
      </Button>

      <Typography variant="h4" sx={{ fontWeight: "bold", mb: 2, color: "white" }}>
        <span style={{ color: "green" }}>Code Essence</span>
      </Typography>

      <Typography variant="h2" sx={{ fontWeight: "bold", mb: 2, lineHeight: 1.2 }}>
        Summarize any{" "}
        <span style={{ color: "green", textDecoration: "underline" }}>GitHub</span> Repository
      </Typography>

      {/* GitHub Repo URL Input */}
      <TextField
        placeholder="Enter GitHub repository URL"
        variant="outlined"
        value={repoURL}
        onChange={(e) => setRepoURL(e.target.value)}
        fullWidth
        sx={{
          maxWidth: "600px",
          mb: 3,
          "& .MuiOutlinedInput-root": { background: "white", borderRadius: "10px" },
          "& input": { color: "black" },
        }}
      />

      {/* Summarize Button */}
      <Button
        variant="contained"
        onClick={handleSummarize}
        sx={{
          backgroundColor: "green",
          color: "white",
          padding: "10px 30px",
          borderRadius: "20px",
          fontWeight: "bold",
          "&:hover": { backgroundColor: "darkgreen" },
        }}
      >
        Summarize
      </Button>

      {/* Navigation to Code Level Summary */}
      <Typography sx={{ color: "green", mt: 2, fontWeight: "bold" }}>
        If you want to summarize any code, click on{" "}
        <span
          style={{ textDecoration: "underline", cursor: "pointer" }}
          onClick={() => navigate("/CodeSummary")}
        >
          Code Level
        </span>
      </Typography>

      {/* Error Message */}
      {error && (
        <Alert
          severity="error"
          sx={{
            marginTop: "20px",
            color: "black",
            backgroundColor: "rgba(255, 255, 255, 0.8)",
            border: "1px solid red",
          }}
        >
          {error}
        </Alert>
      )}
    </Box>
  );
}

export default Home;
