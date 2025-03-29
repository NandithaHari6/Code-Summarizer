const config = {
    API_BASE_URL: process.env.NODE_ENV === "development"
      ? "http://localhost:8000"
      : "https://code-summarizer.onrender.com",
  };
  
  export default config;