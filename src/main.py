import os
import io
import openai
import pandas as pd
from PyPDF2 import PdfReader
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv


load_dotenv()

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Google Drive Setup
SCOPES = ["https://www.googleapis.com/auth/drive"]
DRIVE_CREDENTIALS = "credentials.json"
REMOTE_FOLDER_ID = "your_google_drive_folder_id" 

# Define evaluation prompt
evaluation_prompt = """
You are an HR expert tasked with evaluating job applications.
For each application, assess the following criteria on a scale of 1 to 10:
1. Relevant Experience
2. Education Level
3. Technical Skills
4. Communication Skills
5. Overall Fit for the Role

Provide a structured response like this:
{
    "Relevant Experience": score,
    "Education Level": score,
    "Technical Skills": score,
    "Communication Skills": score,
    "Overall Fit for the Role": score
}
"""

def extract_text_from_pdf(file_path):
    """
    Extract text content from a PDF file.
    """
    reader = PdfReader(file_path)
    return " ".join(page.extract_text() for page in reader.pages)

def evaluate_application(file_path):
    """
    Evaluate a single application using OpenAI API.
    """
    application_text = extract_text_from_pdf(file_path)
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an assistant helping with candidate evaluation."},
            {"role": "user", "content": evaluation_prompt},
            {"role": "user", "content": f"Here is the application text:\n{application_text}"}
        ],
    )
    evaluation = response["choices"][0]["message"]["content"]
    return evaluation

def get_google_drive_service():
    """
    Authenticate and return a Google Drive service instance.
    """
    creds = Credentials.from_service_account_file(DRIVE_CREDENTIALS, scopes=SCOPES)
    service = build("drive", "v3", credentials=creds)
    return service

def download_files_from_drive(service, folder_id, local_folder="downloads"):
    """
    Download all PDF files from a Google Drive folder to a local folder.
    """
    os.makedirs(local_folder, exist_ok=True)
    query = f"'{folder_id}' in parents and mimeType='application/pdf'"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])
    for file in files:
        file_id = file["id"]
        file_name = file["name"]
        request = service.files().get_media(fileId=file_id)
        file_path = os.path.join(local_folder, file_name)
        with io.FileIO(file_path, "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
        print(f"Downloaded {file_name} to {file_path}")
    return local_folder

def main():
    # Specify local folder for downloaded or existing files
    local_folder = "applications"
    process_remote = input("Process remote Google Drive folder? (yes/no): ").strip().lower() == "yes"

    if process_remote:
        # Authenticate Google Drive service and download files
        service = get_google_drive_service()
        local_folder = download_files_from_drive(service, REMOTE_FOLDER_ID)

    # Get all PDF files in the local folder
    application_files = [
        os.path.join(local_folder, file)
        for file in os.listdir(local_folder)
        if file.endswith(".pdf")
    ]

    # Evaluate applications and store results
    results = []
    for file_path in application_files:
        try:
            print(f"Evaluating: {file_path}")
            evaluation = evaluate_application(file_path)
            results.append({"File": os.path.basename(file_path), "Evaluation": evaluation})
        except Exception as e:
            print(f"Error evaluating {file_path}: {e}")

    # Parse results into a DataFrame
    scores = []
    for result in results:
        try:
            evaluation = eval(result["Evaluation"])  # Convert string to dictionary
            scores.append({**evaluation, "File": result["File"]})
        except Exception as e:
            print(f"Error parsing evaluation for {result['File']}: {e}")

    df = pd.DataFrame(scores)

    # Calculate total score and rank
    df["Total Score"] = (
        df["Relevant Experience"] +
        df["Education Level"] +
        df["Technical Skills"] +
        df["Communication Skills"] +
        df["Overall Fit for the Role"]
    )
    df = df.sort_values(by="Total Score", ascending=False)

    # Select top 10 applications
    top_10 = df.head(10)

    # Save results to a CSV file
    top_10.to_csv("top_10_candidates.csv", index=False)
    print("Top 10 candidates saved to top_10_candidates.csv")

if __name__ == "__main__":
    main()
