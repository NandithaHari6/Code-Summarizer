import React, { useState, useEffect } from "react";
import {
  Box,
  Button,
  Typography,
  Menu,
  MenuItem,
  CircularProgress,
} from "@mui/material";

import { useLocation, useNavigate } from "react-router-dom"; 

function SummarySelector() {
  const location = useLocation();
  const repoURL = new URLSearchParams(location.search).get("repoURL");
  const navigate = useNavigate();
  const [selectedSummary, setSelectedSummary] = useState("Project Level");
  const [anchorEl, setAnchorEl] = useState(null);
  const [repoFiles, setRepoFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [loadingFiles, setLoadingFiles] = useState(false);
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [summary, setSummary] = useState("");

  // Extract repo details from GitHub URL
  const getRepoDetails = () => {
    if (!repoURL) return { owner: null, repo: null };
    const parts = repoURL.split("github.com/")[1]?.split("/");
    return parts && parts.length >= 2 ? { owner: parts[0], repo: parts[1] } : { owner: null, repo: null };
  };

  const { owner, repo } = getRepoDetails();
  const extractFilePaths = (structure, prefix = "/tmp/clonedfile") => {
    let paths = [];
    for (const [key, value] of Object.entries(structure)) {
      const fullPath = `${prefix}/${key}`;
      if (value === null) {
        // It's a file, add to list
        paths.push(fullPath);
      } else {
        // It's a folder, recurse
        paths = paths.concat(extractFilePaths(value, fullPath));
      }
    }
    return paths;
  };
  const fetchRepoFiles = async () => {
    setLoadingFiles(true);
    try {
      const response = await fetch("https://code-summarizer.onrender.com/get_file_structure", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_link: repoURL }),
      });
  
      const data = await response.json();
      
      // Extract correctly formatted full file paths
      const files = extractFilePaths(data.structure);
      
      setRepoFiles(files); // Store full paths in state
    } catch (error) {
      console.error("Error fetching repo files:", error);
      setRepoFiles([]);
    }
    setLoadingFiles(false);
  };
  // Fetch repository file structure
  // const fetchRepoFiles = async () => {
  //   if (!repoURL) return;
  //   setLoadingFiles(true);
  //   try {
  //     const response = await fetch("https://code-summarizer.onrender.com/get_file_structure", {
  //       method: "POST",
  //       headers: {
  //         "Content-Type": "application/json"
         
  //       },
  //       body: JSON.stringify({ repo_link: repoURL }),
  //     });
  //     const data = await response.json();
  //     if (data.structure) {
  //       setRepoFiles(Object.keys(data.structure));
  //     }
  //   } catch (error) {
  //     console.error("Error fetching file structure:", error);
  //   }
  //   setLoadingFiles(false);
  // };

  // Fetch project-level summary
  const fetchProjectSummary = async () => {
    if (!repoURL) return;
    setLoadingSummary(true);
    setSelectedSummary("Project Level");
    setSelectedFile(null);
    try {
      const response = await fetch("https://code-summarizer.onrender.com/generate_folder_summary", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
          
        },
        body: JSON.stringify({ repo_link: repoURL, level: "folder" }),
      });
      const data = await response.json();
      console.log(data.summary);
      setSummary(data.summary || "No summary available.");
    } catch (error) {
      console.error("Error fetching project summary:", error);
      setSummary("Error fetching summary.");
    }
    setLoadingSummary(false);
  };

  // Fetch file-level summary
  const fetchFileSummary = async (filePath) => {
    if (!repoURL || !filePath) return;
    setLoadingSummary(true);
    setSelectedSummary("File Level");
    setSelectedFile(filePath);
    console.log(filePath);
    try {
      const response = await fetch("https://code-summarizer.onrender.com/generate_file_summary", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
          
        },
        body: JSON.stringify({ repo_link: repoURL, level: "file", file_path: filePath }),
      });
      const data = await response.json();
      setSummary(data.summary || "No summary available.");
    } catch (error) {
      console.error("Error fetching file summary:", error);
      setSummary("Error fetching summary.");
    }
    setLoadingSummary(false);
    
  };

  // Generate GitHub URL for the selected file
  const extractGitHubFileURL = (filePath) => {
    return repoURL ? `${repoURL}/blob/main/${filePath}` : "#";
  };

  return (
    <Box
      sx={{
        display: "flex",
        height: "100vh",
        backgroundColor: "black",
        color: "white",
      }}
    >
      {/* Sidebar */}
      <Box
        sx={{
          width: "250px",
          backgroundColor: "#222",
          padding: "20px",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 2,
        }}
      >
        <Typography variant="h5" sx={{ fontWeight: "bold", color: "green" }}>
          Summary Options
        </Typography>
       
        <Button
          variant="contained"
          sx={{ backgroundColor: "green", color: "white", borderRadius: "20px", width: "100%" }}
          onClick={fetchProjectSummary}
        >
          Project Level
        </Button>

        <Button
          variant="contained"
          sx={{ backgroundColor: "green", color: "white", borderRadius: "20px", width: "100%" }}
          onClick={(e) => {
            setAnchorEl(e.currentTarget);
            fetchRepoFiles();
          }}
        >
          File Level ▼
        </Button>
        <Button
  variant="contained"
  sx={{ backgroundColor: "green", color: "white", borderRadius: "20px", width: "100%" }}
  onClick={() => navigate("/codesummary")}

>
Code Level
</Button>
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={() => setAnchorEl(null)}
        >
          {loadingFiles ? (
    <MenuItem disabled>
      <CircularProgress size={20} />
    </MenuItem>
  ) : repoFiles.length === 0 ? (
    <MenuItem disabled>No files found</MenuItem>
  ) : (
    repoFiles.map((file) => (
      <MenuItem
        key={file}
        onClick={() => {
          setSelectedFile(file); // Stores full file path
          fetchFileSummary(file); // Uses full path in API request
          setAnchorEl(null);
        }}
      >
        {file.replace("/tmp/clonedfile/", "")} {/* Display relative path */}
      </MenuItem>
    ))
  )}
          {/* {loadingFiles ? (
            <MenuItem disabled>
              <CircularProgress size={20} />
            </MenuItem>
          ) : repoFiles.length === 0 ? (
            <MenuItem disabled>No files found</MenuItem>
          ) : (
            repoFiles.map((file) => (
              <MenuItem
                key={file}
                onClick={() => {
                  setSelectedFile(file);
                  fetchFileSummary(file);
                  setAnchorEl(null);
                }}
              >
                {file}
              </MenuItem>
            ))
          )} */}
        </Menu>
      </Box>

      {/* Main Content */}
      <Box sx={{ flexGrow: 1, textAlign: "center", padding: "20px" }}>
        <Typography variant="h4" sx={{ fontWeight: "bold", mb: 2 }}>
          {selectedFile ? `File: ${selectedFile}` : "Project Level Summary"}
        </Typography>

        <Box sx={{ backgroundColor: "#333", padding: "20px", borderRadius: "10px", color: "white" }}>
          {loadingSummary ? <CircularProgress /> : <Typography>{summary}</Typography>}
        </Box>

        {/* "View Content" Button (Only for File Level) */}
        {selectedFile && (
          <Button
            variant="contained"
            sx={{
              backgroundColor: "green",
              color: "white",
              borderRadius: "10px",
              mt: 3,
              padding: "10px 20px",
              fontSize: "16px",
              fontWeight: "bold",
              "&:hover": { backgroundColor: "#4caf50" },
            }}
            onClick={() => window.open(extractGitHubFileURL(selectedFile), "_blank")}
          >
            View Content
          </Button>
        )}
      </Box>
    </Box>
  );
}

export default SummarySelector;