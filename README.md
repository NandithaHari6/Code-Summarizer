To run,
python -m venv .venv
pip install requirements.txt
Create groq API key from https://console.groq.com/keys
Create a .env file with groq_api_key="YOUR_KEY"

Run Fast API server using the command:
uvicorn main:app --reload

To test the proper functioning of the API , send POST  requests to
 http://127.0.0.1:8000/generate_summary
 with the following body format:
 {
    "level":"folder",
"repo_link":"https://github.com/mcanet/STL-Volume-Model-Calculator"
}

