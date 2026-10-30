# After the Discovery Call Agent

A small Python automation for the fictional Riya Mehta / Mehta Organics transcript. It creates a Google Drive folder, a Google Doc with a consistent client record, and a Gmail **draft**. It never sends email.

## Why Python + Google APIs?

The brief permits a short Python script and free tiers. Python keeps the workflow transparent and easy to inspect, while Google APIs place the outputs directly in Drive and Gmail. The summary and email are deliberately template-based for this fixed transcript: this reduces hallucination risk and makes privacy exclusions explicit. No paid LLM is required.

## Requirements

- Python 3.10+
- A Google account
- Google Cloud project with **Google Drive API**, **Google Docs API**, and **Gmail API** enabled
- OAuth 2.0 Desktop app credentials saved as `credentials.json` beside `agent.py`

## Setup (Windows PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe agent.py
```

When prompted, type `CREATE` to authorize Google access and create outputs. A browser window opens for Google sign-in and consent. Token credentials are saved locally in `token.json`; never commit either `credentials.json` or `token.json`.

## Google OAuth setup

1. Open Google Cloud Console and create/select a project.
2. Enable Google Drive API, Google Docs API, and Gmail API.
3. Configure the OAuth consent screen. If the app is in Testing, add your Google account as a test user.
4. Create OAuth client credentials of type **Desktop app** and download the JSON.
5. Rename the downloaded file to `credentials.json` and place it beside `agent.py`.
6. Run the script and complete consent. If you change scopes, delete local `token.json` and authorize again.

Google may show an unverified-app warning for a personal test app; only continue if this is your own Cloud project and you understand the requested permissions.

## Safety and transcript handling

- The Gmail message is created as a **draft only**. The script does not call Gmail's send endpoint.
- The recipient is intentionally a placeholder because the transcript does not provide an email address. Add a verified address manually.
- The Cal.com booking URL remains `[CAL.COM BOOKING LINK]` because no actual URL was supplied.
- The client's personal phone number is not stored in the Doc or email.
- The transcript's explicitly off-record speculation about Green Basket is excluded entirely, including from the generated client record.
- The ₹25,000–₹30,000 monthly budget is recorded in the internal Doc as unconfirmed; it is omitted from the client email.
- The exact Thursday date/time is not inferred; the Doc marks it for confirmation.
- No real data is used.

## Outputs

- Drive folder: `Client - Riya Mehta - 2026-10-26`
- Google Doc with client details, goals, pain points, budget/timeline, objections, next steps, confirmation list, privacy note, and WhatsApp reminder
- Gmail draft titled `Next steps for Mehta Organics workflow automation`
- WhatsApp reminder text printed to terminal (under 300 characters)

## Important retry note

If the script creates the Doc and then fails while creating the Gmail draft, it may leave the Doc in Drive. Check Drive and Gmail Drafts before rerunning to avoid duplicate artifacts. This prototype does not yet implement idempotency or automatic retries.

### Three failure points you can explain
You can use these:
- Google authentication failure: OAuth credentials may expire or permissions may change. Fix: reauthorize the Google account and verify API access.
- Incorrect AI-generated content: The LLM may misunderstand a customer's requirements or invent details. Fix: mark missing information as [CONFIRM] and require human review before approval.
- Duplicate or failed records: Repeated runs or API failures may create duplicate folders, documents or drafts. Fix: add duplicate checks, logging and retry handling.