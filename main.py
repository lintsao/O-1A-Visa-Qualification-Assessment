from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from PyPDF2 import PdfReader
import io
import os
from openai import OpenAI
import json
import uvicorn
from dotenv import load_dotenv

from utils import pdf_parser, make_prompt, client_response

# Config.
criteria_file_path = "./O-1AEvidentiaryRequirements.json"

# Load environment variables from .env file
load_dotenv()

# Connect to the OpenAI Client.
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

# Read the criteria from the JSON file.
with open(criteria_file_path, "r") as f:
    criteria = json.load(f)
    criteria_list = list(criteria.keys())

# Use FastAPI for uploading the CV.
app = FastAPI()
@app.get("/")
async def main():
    content = """
    <html>
        <body>
            <form action="/uploadfile/" enctype="multipart/form-data" method="post">
                <input name="file" type="file">
                <input type="submit">
            </form>
        </body>
    </html>
    """

    return HTMLResponse(content=content)

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    pdf_stream = io.BytesIO(contents)
    pdf_reader = PdfReader(pdf_stream)

    cv_text = pdf_parser(pdf_reader)
    prompt = make_prompt(criteria, criteria_list, cv_text)
    result_text = client_response(client, prompt)

    # analysis_dict = json.loads(result_text)
    # print(analysis_dict)

    # # Create HTML content
    # html_content = f"""
    # <html>
    #     <body>
    #         <h1>CV Analysis</h1>
    #         <pre>{formatted_analysis}</pre>
    #         <h2>Criteria</h2>
    #         <pre>{json.dumps(criteria, indent=2)}</pre>
    #     </body>
    # </html>
    # """
    return {
        "analysis": result_text
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
