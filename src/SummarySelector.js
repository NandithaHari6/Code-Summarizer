import React, { useState } from "react";
import {
  Box,
  Typography,
  Button,
  TextareaAutosize,
  Divider,
  IconButton,
} from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import SaveIcon from "@mui/icons-material/Save";

function SummarySelector() {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [textInput, setTextInput] = useState("");
  const [summary, setSummary] = useState("");

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setUploadedFile(file);
    }
  };

  const handleSummarize = () => {
    
    setSummary("This is a placeholder summary for the uploaded text or input.");
  };

  const handleSave = () => {
    
    alert("Summary saved!");
  };

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "row",
        height: "100vh",
        backgroundColor: "#121212",
        color: "white",
      }}
    >
      {/* Sidebar */}
      <Box
        sx={{
          width: "300px",
          backgroundColor: "#1E1E1E",
          padding: "20px",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <Typography
          variant="h6"
          sx={{ fontWeight: "bold", mb: 2, color: "lightgray" }}
        >
          Summary Level
        </Typography>
        <Button
          variant="contained"
          sx={{
            backgroundColor: "darkgreen",
            mb: 2,
            "&:hover": { backgroundColor: "green" },
          }}
        >
          File Level
        </Button>
        <Button
          variant="contained"
          sx={{
            backgroundColor: "darkgreen",
            "&:hover": { backgroundColor: "green" },
          }}
        >
          Project Level
        </Button>
        <Button
          variant="contained"
          sx={{
            backgroundColor: "darkgreen",
            "&:hover": { backgroundColor: "green" },
          }}
        >
          Folder Level
        </Button>
        <Button
          variant="contained"
          sx={{
            backgroundColor: "darkgreen",
            "&:hover": { backgroundColor: "green" },
          }}
        >
          Code Snippet Level
        </Button>
      </Box>

      {/* Main Content */}
      <Box
        sx={{
          flex: 1,
          padding: "40px",
          display: "flex",
          flexDirection: "column",
          position: "relative",
        }}
      >
        {/* Header with Save Option */}
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 4,
          }}
        >
          <Typography variant="h5" sx={{ fontWeight: "bold" }}>
            Multilingual Text Summarizer
          </Typography>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            sx={{
              backgroundColor: "#4CAF50",
              "&:hover": { backgroundColor: "#388E3C" },
            }}
            onClick={handleSave}
          >
            Save
          </Button>
        </Box>

        {/* File Upload Section */}
        <Box
          sx={{
            border: "2px dashed gray",
            borderRadius: "10px",
            padding: "40px",
            textAlign: "center",
            mb: 4,
          }}
        >
          <Typography variant="h6" sx={{ mb: 2 }}>
            Choose a file (PDF, TXT, Image)
          </Typography>
          <input
            type="file"
            onChange={handleFileUpload}
            style={{ display: "none" }}
            id="file-upload"
          />
          <label htmlFor="file-upload">
            <Button
              variant="contained"
              startIcon={<CloudUploadIcon />}
              sx={{
                backgroundColor: "darkgreen",
                "&:hover": { backgroundColor: "green" },
              }}
              component="span"
            >
              Browse files
            </Button>
          </label>
          {uploadedFile && (
            <Typography variant="body2" sx={{ mt: 2 }}>
              Uploaded: {uploadedFile.name}
            </Typography>
          )}
        </Box>

        {/* Text Input Area */}
        <TextareaAutosize
          minRows={8}
          placeholder="Enter text or paste content here..."
          value={textInput}
          onChange={(e) => setTextInput(e.target.value)}
          style={{
            width: "100%",
            backgroundColor: "#1E1E1E",
            color: "white",
            padding: "10px",
            borderRadius: "5px",
            border: "1px solid gray",
            marginBottom: "20px",
          }}
        />

        {/* Summarize Button */}
        <Button
          variant="contained"
          sx={{
            backgroundColor: "darkgreen",
            mb: 4,
            "&:hover": { backgroundColor: "green" },
          }}
          onClick={handleSummarize}
        >
          Summarize
        </Button>

        {/* Display Summary */}
        {summary && (
          <Box
            sx={{
              backgroundColor: "#1E1E1E",
              padding: "20px",
              borderRadius: "10px",
              border: "1px solid gray",
            }}
          >
            <Typography variant="h6" sx={{ mb: 2 }}>
              Summary:
            </Typography>
            <Typography variant="body1">{summary}</Typography>
          </Box>
        )}
      </Box>
    </Box>
  );
}

export default SummarySelector;
