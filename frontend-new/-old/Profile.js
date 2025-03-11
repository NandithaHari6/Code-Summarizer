import React, { useState } from "react";
import { Box, Typography, Card, CardContent, Button } from "@mui/material";
import { useNavigate } from "react-router-dom";

function Profile() {
  const navigate = useNavigate();

  // Mock summaries (Replace with API data later)
  const [summaries, setSummaries] = useState([
    { id: 1, repo: "React-App", summary: "A simple React app with authentication." },
    { id: 2, repo: "Node-Server", summary: "An Express.js server handling REST APIs." },
    { id: 3, repo: "Portfolio-Site", summary: "A portfolio website built using Next.js." }
  ]);

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
      {/* Back Button */}
      <Button
        variant="contained"
        sx={{
          position: "absolute",
          top: 20,
          left: 20,
          backgroundColor: "green",
          color: "white",
          borderRadius: "20px",
          "&:hover": { backgroundColor: "darkgreen" },
        }}
        onClick={() => navigate("/")}
      >
        Back to Home
      </Button>

      <Typography variant="h3" sx={{ fontWeight: "bold", mb: 2 }}>
        Your <span style={{ color: "green" }}>Generated Summaries</span>
      </Typography>

      {/* Summaries List */}
      <Box sx={{ maxWidth: "600px", width: "100%" }}>
        {summaries.length === 0 ? (
          <Typography variant="body1" sx={{ color: "rgba(255, 255, 255, 0.7)" }}>
            No summaries generated yet.
          </Typography>
        ) : (
          summaries.map((item) => (
            <Card
              key={item.id}
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
                  {item.repo}
                </Typography>
                <Typography variant="body2" sx={{ color: "rgba(255, 255, 255, 0.8)" }}>
                  {item.summary}
                </Typography>
              </CardContent>
            </Card>
          ))
        )}
      </Box>
    </Box>
  );
}

export default Profile;
