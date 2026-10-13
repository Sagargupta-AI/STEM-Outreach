# STEM Outreach for School Children — Working Flask Project

A small local web application based on the CEP report topic. It includes a STEM activity library, student survey form, SQLite storage, account registration/login, live response analysis, and CSV export.

## Features
- Public home page and STEM activity ideas
- Registration and login; passwords are stored as hashes, not plain text
- Ten-question survey matching the questions in the CEP report
- Saves genuine submitted survey answers in a local SQLite database
- Results page with response counts and percentages calculated from actual submissions
- CSV export for opening in Excel
- Mobile-friendly layout

## Important academic integrity note
The PDF contains an *illustrative* dataset of 50 respondents, not verified survey results. This app does **not** seed those example numbers as real responses. Submit real, permission-based survey responses; the charts show zero until genuine responses are submitted.

## Run on Windows / VS Code
1. Install Python 3.10+.
2. Extract the ZIP to a normal folder.
3. Open that folder in VS Code (`File > Open Folder`).
4. Open Terminal (`Terminal > New Terminal`).
5. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again. Or use Command Prompt:
   ```bat
   .venv\Scripts\activate.bat
   ```

6. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
7. Start the app:
   ```powershell
   python app.py
   ```
8. Open `http://127.0.0.1:5000` in Chrome.

The database `stem_outreach.db` is created automatically on first run.

## Quick demo
1. Register an account with your name, email, and a password of 8+ characters.
2. Log in and open Dashboard.
3. Open Survey and submit a response. You can use your own test response for checking the app, but do not represent test data as school field data.
4. Submit more responses only with appropriate school permission and privacy safeguards.
5. Open Results to see counts and percentages from stored responses.
6. Use Export CSV to download a spreadsheet.

## Safety and privacy
- Get permission from school management before surveying children.
- Avoid collecting children's names or personal contact details; use anonymous respondent codes.
- Do not upload the local database or real children's responses to a public GitHub repository.
- This is a college demo, not a production-secure service. Change `SECRET_KEY`, disable debug mode, and add proper deployment security before publishing online.
