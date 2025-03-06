To run,<br />

python -m venv .venv <br />

pip install requirements.txt<br />

Create groq API key from https://console.groq.com/keys<br />

Create a .env file with groq_api_key="YOUR_KEY"<br />


Run Fast API server using the command:<br />

uvicorn main:app --reload<br />


To test the proper functioning of the API , send POST  requests to<br />

 http://127.0.0.1:8000/generate_summary<br />

 with the following body format:<br />

{<br />
<br />

"level":"folder",<br />

"repo_link":"  repo//link//in//github//that //you//want//to//summarize"<br />

}

