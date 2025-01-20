import React, { useState } from "react";
import {
  Box,
  Typography,
  FormControl,
  RadioGroup,
  FormControlLabel,
  Radio,
  Button,
  TextField,
} from "@mui/material";
import { useNavigate } from "react-router-dom";

function SummarySelector() {
  const [summaryLevel, setSummaryLevel] = useState("file");
  const navigate = useNavigate();

  const handleSaveSummary = () => {
    // Navigate to login page
    navigate("/login");
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
        <span style={{ color: "green" }}>Choose Your Summary Level</span>
      </Typography>

      <Typography variant="body1" sx={{ mb: 4, color: "rgba(255, 255, 255, 0.8)" }}>
        Select the level of summary you'd like: File-level, Folder-level, or Code Snippet-level.
      </Typography>

      {/* Summary Level Options */}
      <FormControl>
        <RadioGroup
          value={summaryLevel}
          onChange={(e) => setSummaryLevel(e.target.value)}
          sx={{ mb: 3 }}
        >
          <FormControlLabel
            value="file"
            control={<Radio sx={{ color: "darkgreen" }} />}
            label={<Typography sx={{ color: "white" }}>File Level</Typography>}
          />
          <FormControlLabel
            value="folder"
            control={<Radio sx={{ color: "green" }} />}
            label={<Typography sx={{ color: "white" }}>Folder Level</Typography>}
          />
          <FormControlLabel
            value="code"
            control={<Radio sx={{ color: "green" }} />}
            label={<Typography sx={{ color: "white" }}>Code Snippet</Typography>}
          />
        </RadioGroup>
      </FormControl>

      {/* Save Button */}
      <Button
        variant="contained"
        onClick={handleSaveSummary}
        sx={{
          backgroundColor: "darkgreen",
          color: "black",
          padding: "10px 30px",
          borderRadius: "20px",
          fontWeight: "bold",
          "&:hover": { backgroundColor: "green" },
        }}
      >
        Save Summary
      </Button>
    </Box>
  );
}

export default SummarySelector;
