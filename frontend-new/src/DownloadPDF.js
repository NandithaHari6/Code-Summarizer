import React from "react";
import config from './config'
const DownloadPDF = () => {
  const handleDownload = async () => {
    try {
      const response = await fetch(`${config.API_BASE_URL}/download_summary_pdf/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          summary: {
            projectTitle: "Dinosaur Game Project",
            techStack: "Python, Pygame, OS, Random",
            projectOverview:
              "The project is a simple dinosaur game where the player controls a dinosaur...",
            fileOverview:
              "main.py-contains the main game loop, Dinosaur.py-contains the dinosaur class...",
          },
          repo_link: "https://github.com/MaxRohowsky/chrome-dinosaur",
          level: "folder",
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to download PDF");
      }

      // Convert response to a Blob
      const blob = await response.blob();

      // ✅ Check if the File System API is available
      if (window.showSaveFilePicker) {
        // Open the "Save As" dialog
        const handle = await window.showSaveFilePicker({
          suggestedName: "summary.pdf",
          types: [
            {
              description: "PDF File",
              accept: { "application/pdf": [".pdf"] },
            },
          ],
        });

        // Write the file to the selected location
        const writable = await handle.createWritable();
        await writable.write(blob);
        await writable.close();
      } else {
        // Fallback for browsers without File System API
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "summary.pdf";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error("Error downloading PDF:", error);
    }
  };

  return (
    <div>
      <button onClick={handleDownload}>Download PDF</button>
    </div>
  );
};

export default DownloadPDF;
