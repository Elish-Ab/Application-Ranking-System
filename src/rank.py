import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Authenticate with Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)

# Open the Google Sheet
sheet = client.open("Job Applications").sheet1

# Fetch all records including the header row
data = sheet.get_all_records()

# Convert data to a DataFrame
df = pd.DataFrame(data)

# Display the first few rows to ensure columns are read correctly
print("Data Preview:")
print(df.head())

# Convert "B2B Experience" to numeric
df["B2B Experience"] = pd.to_numeric(df["B2B Experience"], errors="coerce").fillna(0)

# Convert yes/no answers to numeric scores
for col in ["Direct Sales", "Administrative Experience", "Full-Time Availability"]:
    df[col] = df[col].apply(lambda x: 1 if x.strip().lower() == "yes" else 0)

# Calculate the total score
df["Score"] = (
    df["B2B Experience"] +
    df["Direct Sales"] +
    df["Administrative Experience"] +
    df["Full-Time Availability"]
)

# Sort by score in descending order
df = df.sort_values(by="Score", ascending=False)

# Get the top 10 candidates
top_10 = df.head(10)

# Print the results
print("Top 10 Candidates:")
print(top_10)
