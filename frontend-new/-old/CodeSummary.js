import React, { useState } from "react";
import { Box, Typography, TextField, Button, Alert, CircularProgress } from "@mui/material";
import axios from "axios"; // ✅ Import axios for API requests

function CodeSummary() {
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [summary, setSummary] = useState(""); // ✅ Store API response
  const [loading, setLoading] = useState(false); // ✅ Show loading state

  const handleSummarize = async () => {
    setError("");
    setSummary(""); // Reset summary on new request
    setLoading(true); // Show loading indicator

    if (!code.trim()) {
      setError("Please enter some code to summarize.");
      setLoading(false);
      return;
    }

    try {
      const response = await axios.post("https://code-summarizer.onrender.com/generate_code_summary", {
        code: code,
      });

      setSummary(response.data.summary || "No summary generated."); // ✅ Update summary
    } catch (error) {
      console.error("Error fetching summary:", error);
      setError("Failed to fetch summary. Please try again.");
    }

    setLoading(false); // Hide loading indicator
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
        Paste Your <span style={{ color: "green", textDecoration: "underline" }}>Code</span> Below
      </Typography>

      {/* Code Input Field */}
      <TextField
        placeholder="Paste your code here"
        variant="outlined"
        value={code}
        onChange={(e) => setCode(e.target.value)}
        multiline
        rows={10}
        fullWidth
        sx={{
          maxWidth: "600px",
          mb: 3,
          "& .MuiOutlinedInput-root": { background: "white", borderRadius: "10px" },
          "& textarea": { color: "black" },
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
        disabled={loading} // Disable button when loading
      >
        {loading ? <CircularProgress size={24} sx={{ color: "white" }} /> : "Summarize"}
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

      {/* Display Summary */}
      {summary && (
        <Box
          sx={{
            backgroundColor: "#333",
            padding: "20px",
            borderRadius: "10px",
            color: "white",
            marginTop: "20px",
            maxWidth: "600px",
            textAlign: "left",
          }}
        >
          <Typography variant="h5" sx={{ fontWeight: "bold", mb: 1 }}>
            Code Summary:
          </Typography>
          <Typography>{summary}</Typography>
        </Box>
      )}
    </Box>
  );
}

export default CodeSummary;
