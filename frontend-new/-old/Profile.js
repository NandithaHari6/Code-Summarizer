import React, { useEffect, useState } from "react";
import { Box, Typography, Card, CardContent, Button, CircularProgress } from "@mui/material";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import config from "./config";
function Profile() {
  const navigate = useNavigate();
  const [userInfo, setUserInfo] = useState(null);
  const [summaries, setSummaries] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem("token");

      if (!token) {
        console.error("No authentication token found. Please log in.");
        setError("Authentication required. Please log in again.");
        setLoading(false);
        return;
      }

      try {
        const userResponse = await axios.get(`${config.API_BASE_URL}/user_info`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        setUserInfo(userResponse.data);

        const summariesResponse = await axios.get(`${config.API_BASE_URL}/view_saved_sum`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        setSummaries(summariesResponse.data);
      } catch (err) {
        console.error("Error fetching data:", err.response?.data || err.message);
        setError("Failed to fetch profile data. Please try again.");
      }
      setLoading(false);
    };

    fetchData();
  }, []);

  const handleDelete = async (sumid) => {
    const token = localStorage.getItem("token");
    if (!token) {
      setError("Authentication required. Please log in again.");
      return;
    }

    try {
      await axios.delete(`${config.API_BASE_URL}/delete_summary/${sumid}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setSummaries(summaries.filter((item) => item.sumid !== sumid));
    } catch (err) {
      console.error("Error deleting summary:", err.response?.data || err.message);
      setError("Failed to delete summary. Please try again.");
    }
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
        onClick={() => navigate("/")}
      >
        Back to Home
      </Button>

      {loading ? <CircularProgress sx={{ color: "green", mt: 2 }} /> : null}
      {error && <Typography sx={{ color: "red", mb: 2 }}>{error}</Typography>}

      {userInfo && (
        <Card
          sx={{
            background: "rgba(255, 255, 255, 0.1)",
            color: "white",
            mb: 3,
            padding: "15px",
            borderRadius: "10px",
            border: "1px solid white",
            textAlign: "left",
            width: "90%",
            maxWidth: "500px",
          }}
        >
          <CardContent>
            <Typography variant="h5" sx={{ fontWeight: "bold", textAlign: "center", color: "green" }}>
              {userInfo.name}
            </Typography>
            <Typography sx={{ color: "rgba(255, 255, 255, 0.8)", textAlign: "center" }}>
              @{userInfo.username}
            </Typography>
            <Typography sx={{ mt: 1 }}>
              <strong>Repositories:</strong> {userInfo.no_of_repos}
            </Typography>
            <Typography>
              <strong>Followers:</strong> {userInfo.followers} | <strong>Following:</strong> {userInfo.following}
            </Typography>
            <Typography sx={{ textAlign: "center", mt: 2 }}>
              <a href={userInfo.url} target="_blank" rel="noopener noreferrer" style={{ color: "green", textDecoration: "none" }}>
                View GitHub Profile
              </a>
            </Typography>
          </CardContent>
        </Card>
      )}

      <Typography variant="h3" sx={{ fontWeight: "bold", mb: 2 }}>
        Your <span style={{ color: "green" }}>Generated Summaries</span>
      </Typography>

      {summaries.length === 0 && !loading && !error ? (
        <Typography variant="body1" sx={{ color: "rgba(255, 255, 255, 0.7)" }}>
          No summaries generated yet.
        </Typography>
      ) : (
        <Box sx={{ maxWidth: "600px", width: "100%" }}>
          {summaries.map((item) => (
            <Card
              key={item.sumid}
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
                  <a href={item.repo_link} target="_blank" rel="noopener noreferrer" style={{ color: "green", textDecoration: "none" }}>
                    {item.repo_link}
                  </a>
                </Typography>
                <Typography variant="body2" sx={{ color: "rgba(255, 255, 255, 0.8)" }}>
                  {item.summary || "No summary available"}
                </Typography>
                <Button
                  variant="contained"
                  color="error"
                  sx={{ mt: 2 }}
                  onClick={() => handleDelete(item.sumid)}
                >
                  Delete
                </Button>
              </CardContent>
            </Card>
          ))}
        </Box>
      )}
    </Box>
  );
}

export default Profile;