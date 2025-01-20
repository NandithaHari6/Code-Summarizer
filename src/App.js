import React, { useState } from "react";
import {
  Box,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  CardActions,
  Alert,
  TextareaAutosize,
} from "@mui/material";
import { useNavigate } from "react-router-dom";  // Import useNavigate


function App() {
  const [githubURL, setGitHubURL] = useState("");
  const [repoData, setRepoData] = useState([]);
  const [error, setError] = useState("");
  const [codeSnippet, setCodeSnippet] = useState(""); // Track code snippet
  const [codeSummary, setCodeSummary] = useState("");
  const navigate = useNavigate();  // Initialize useNavigate

  const handleURLSubmit = async () => {
    setError(""); // Clear previous errors
    setRepoData([]); // Clear previous repo data

    // Extract username from the GitHub URL
    const username = githubURL.split("github.com/")[1]?.split("/")[0];

    if (!username) {
      setError("Invalid GitHub URL. Please enter a valid URL.");
      return;
    }

    try {
      // Fetch repository data from GitHub API
      const response = await fetch(`https://api.github.com/users/${username}/repos`);
      if (!response.ok) {
        throw new Error("Failed to fetch data. Please check the username.");
      }

      const result = await response.json();
      if (result.length === 0) {
        setError("No repositories found for this user.");
      } else {
        setRepoData(result);
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const handleCodeSummarize = () => {
    // Placeholder logic for summarizing code
    setCodeSummary(`Summary: ${codeSnippet.length > 0 ? "Code summary here" : "No code snippet provided."}`);
  };

  const handleRepoSummary = (repoName) => {
    // Navigate to SummarySelector page when Generate Summary is clicked
    navigate("/summary-selector"); // Use navigate to go to the summary selector page
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
      
      {/* Login Button */}
      <Button
        variant="contained"
        sx={{
          position: "absolute",
          top: 20,
          right: 20,
          backgroundColor: "green",
          color: "white",
          borderRadius: "20px",
          "&:hover": { backgroundColor: "darkgreen" },
        }}
      >
        Login
      </Button>

      {/* Header Section */}
      <Typography variant="h4" sx={{ fontWeight: "bold", mb: 2, color: "white" }}>
        <span style={{ color: "green" }}>Code Essence</span>
      </Typography>
      <Typography variant="h2" sx={{ fontWeight: "bold", mb: 2, lineHeight: 1.2 }}>
        Fetch any{" "}
        <span style={{ color: "green", textDecoration: "underline" }}>GitHub</span> Repositories
      </Typography>
      <Typography variant="body1" sx={{ mb: 4, color: "rgba(255, 255, 255, 0.7)" }}>
        Copy and paste any <span style={{ color: "green" }}>GitHub</span> profile URL below.
      </Typography>

      {/* Summarize Code Button and Text Area */}
      <Button
        variant="outlined"
        onClick={() => {}}
        sx={{
          backgroundColor: "green",
          color: "white",
          padding: "10px 30px",
          borderRadius: "20px",
          mb: 2,
          "&:hover": { backgroundColor: "darkgreen" },
        }}
      >
        Summarize Any Code Snippet
      </Button>
      <TextareaAutosize
        minRows={4}
        placeholder="Paste code snippet here..."
        value={codeSnippet}
        onChange={(e) => setCodeSnippet(e.target.value)}
        style={{
          width: "100%",
          maxWidth: "600px",
          backgroundColor: "white",
          color: "black",
          padding: "10px",
          borderRadius: "10px",
          marginBottom: "10px",
        }}
      />

      {/* Input Field */}
      <TextField
        placeholder="Enter GitHub profile URL"
        variant="outlined"
        value={githubURL}
        onChange={(e) => setGitHubURL(e.target.value)}
        fullWidth
        sx={{
          maxWidth: "600px",
          mb: 3,
          "& .MuiOutlinedInput-root": {
            background: "white",
            borderRadius: "10px",
          },
          "& input": { color: "black" },
        }}
      />

      {/* Submit Button */}
      <Button
        variant="contained"
        onClick={handleURLSubmit}
        sx={{
          backgroundColor: "green",
          color: "white",
          padding: "10px 30px",
          borderRadius: "20px",
          fontWeight: "bold",
          "&:hover": { backgroundColor: "darkgreen" },
        }}
      >
        Fetch Repos
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

      {/* Repository Data */}
      <Box sx={{ mt: 4, maxWidth: "600px", width: "100%" }}>
        {repoData.length > 0 && (
          <Typography variant="h6" sx={{ fontWeight: "bold", mb: 3 }}>
            Repositories:
          </Typography>
        )}
        {repoData.map((repo) => (
          <Card
            key={repo.id}
            sx={{
              background: "rgba(255, 255, 255, 0.1)",
              color: "white",
              mb: 2,
              borderRadius: "10px",
              border: "1px solid white",
            }}
          >
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: "bold" }}>
                {repo.name}
              </Typography>
              <Typography variant="body2" sx={{ color: "rgba(255, 255, 255, 0.8)" }}>
                {repo.description || "No description available."}
              </Typography>
            </CardContent>
            <CardActions>
              <Button
                size="small"
                href={repo.html_url}
                target="_blank"
                sx={{
                  backgroundColor: "darkgreen",
                  color: "white",
                  border: "1px solid white",
                  "&:hover": { backgroundColor: "green" },
                  marginRight: "276px",
                }}
              >
                View Repository
              </Button>
              {/* Generate Summary Button for each Repo */}
              <Button
                size="small"
                onClick={() => handleRepoSummary(repo.name)}
                sx={{
                  backgroundColor: "darkgreen",
                  color: "white",
                  border: "1px solid white",
                  "&:hover": { backgroundColor: "green" },
                }}
              >
                Generate Summary
              </Button>
            </CardActions>
          </Card>
        ))}
      </Box>
    </Box>
  );
}

export default App;
