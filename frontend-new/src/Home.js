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

    // Navigate to SummarySelector with repoURL as a query parameter
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
