import React, { useState, useEffect } from "react";
import {
  Box,
  Button,
  Typography,
  Menu,
  MenuItem,
  CircularProgress,
} from "@mui/material";
import config from "./config";
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
  const [saving, setSaving] = useState(false); // For save button loading state

  // Get stored token
  const token = localStorage.getItem("token");
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
      const response = await fetch(`${config.API_BASE_URL}/get_file_structure`, {
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
      const response = await fetch(`${config.API_BASE_URL}/generate_folder_summary`, {
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
      const response = await fetch(`${config.API_BASE_URL}/generate_file_summary`, {
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
   // Save Summary to Backend
   const saveSummary = async () => {
    if (!token) {
      alert("You are not logged in. Please log in first.");
      return;
    }
  
    if (!summary) return;
  
    setSaving(true);
    try {
      // Convert summary to string if it's an object
      const summaryText = typeof summary === "object" ? JSON.stringify(summary, null, 2) : summary;
  
      const response = await fetch(`${config.API_BASE_URL}/save_summary`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`, // Pass token in headers
        },
        body: JSON.stringify({
          repo_link: repoURL,
          level: selectedFile ? "file" : "folder",
          summary: summaryText, // Send as string
        }),
      });
  
      const data = await response.json();
      if (response.ok) {
        alert("Summary saved successfully!");
      } else {
        alert("Error saving summary: " + data.message);
      }
    } catch (error) {
      console.error("Error saving summary:", error);
      alert("Failed to save summary.");
    }
    setSaving(false);
  };
  
  

  // Generate GitHub URL for the selected file
  const extractGitHubFileURL = (filePath) => {
    if (!repoURL || !filePath) return "#";
  
    const cleanPath = filePath.replace("/tmp/clonedfile/", ""); // Remove unwanted prefix
    return `${repoURL}/blob/main/${cleanPath}`;
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
  {selectedFile ? `File: ${selectedFile.replace("/tmp/clonedfile/", "")}` : "Project Level Summary"}
</Typography>


       
{/* Summary Box */}
<Box
  sx={{
    backgroundColor: "#333",
    padding: "20px",
    borderRadius: "10px",
    color: "white",
    minHeight: "150px",
    textAlign: "left",
    paddingBottom: "20px",
  }}
>
  {loadingSummary ? (
    <CircularProgress />
  ) : summary ? (
    typeof summary === "object" ? ( // Project-level summary (object)
      <>
        <Typography variant="h5" sx={{ fontWeight: "bold", color: "lightgreen" }}>
          {summary.projectTitle}
        </Typography>
        <Typography variant="body1" sx={{ fontWeight: "bold", mt: 1 }}>
          Tech Stack: <span style={{ color: "lightblue" }}>{summary.techStack}</span>
        </Typography>
        <Typography variant="body2" sx={{ mt: 2 }}>{summary.projectOverview}</Typography>
        
        <Typography variant="h6" sx={{ fontWeight: "bold", mt: 2 }}>Files Overview:</Typography>
        <Box component="ul" sx={{ marginLeft: 2 }}>
          {summary.fileOverview?.split(", ").map((file, index) => (
            <li key={index} style={{ color: "#ccc" }}>{file}</li>
          ))}
        </Box>
      </>
    ) : ( // File-level summary (string)
      <Typography variant="body1" sx={{ whiteSpace: "pre-line" }}>
        {summary}
      </Typography>
    )
  ) : (
    <Typography>No summary available.</Typography>
  )}
</Box>



{/* Buttons outside the summary box */}
<Box
  sx={{
    display: "flex",
    justifyContent: selectedFile ? "space-between" : "center", // Center for project, space-between for file
    mt: 2, // Add margin-top for spacing
  }}
>
  {/* Save Summary Button (Centered for Project Level) */}
  {summary && (
    <Button
      variant="contained"
      sx={{
        backgroundColor: "green",
        color: "white",
        "&:hover": { backgroundColor: "#4caf50" },
      }}
      onClick={saveSummary}
      disabled={saving}
    >
      {saving ? <CircularProgress size={20} color="inherit" /> : "Save Summary"}
    </Button>
  )}

  {/* View Content Button (Only for File Level, Right Aligned) */}
  {selectedFile && (
    <Button
      variant="contained"
      sx={{
        backgroundColor: "green",
        color: "white",
        "&:hover": { backgroundColor: "#4caf50" },
      }}
      onClick={() => window.open(extractGitHubFileURL(selectedFile), "_blank")}
    >
      View Content
    </Button>
  )}
</Box>



      </Box>
    </Box>
  );
}

export default SummarySelector;