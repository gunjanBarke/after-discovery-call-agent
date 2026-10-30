"""After the Discovery Call agent — creates a Google Drive client folder + Doc and Gmail draft.

Safety design:
- Uses only the fictional transcript included below.
- Creates a Gmail DRAFT; it never sends email.
- Excludes the client's private phone number from generated artifacts.
- Excludes the explicitly off-record speculation about Green Basket from every artifact.
- Uses deterministic extraction/template output so no model can invent facts.
"""
from __future__ import annotations
import os
import re
from datetime import date
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

BASE_DIR = Path(__file__).resolve().parent
TOKEN_FILE = BASE_DIR / "token.json"
CLIENT_SECRET_FILE = BASE_DIR / "credentials.json"
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/gmail.compose",
]

# Fictional source transcript supplied with the assignment. No real data.
TRANSCRIPT = """Call: Discovery - Riya Mehta, Mehta Organics - 26 Oct 2026, 32 min
Riya: We sell cold-pressed oils online, about 400 orders a month. I spend my evenings replying to WhatsApp customers and chasing payments. My team is me and one part-timer, Arjun.
Riya: Wholesale buyers pay late. Three shops owe us around 1.8 lakh in total. One shop is 60 days overdue. [The client explicitly asked that her speculation about that shop's financial condition not be written down anywhere; excluded entirely.]
Riya: In three months, success means evenings back, payment reminders going out automatically, and knowing which wholesale customers are worth keeping.
Riya: I could do 25 to 30 thousand a month, but I need to talk to my husband first; he handles the finances.
Riya: My personal number is private and must not be shared with Arjun. [Number excluded from all generated artifacts.]
Riya: I tried a chatbot last year and it sent wrong prices to customers. I'm nervous about automation talking to customers directly.
Next step agreed: consultant sends a short plan; a 45-minute workflow mapping session next week. Thursday afternoon works. Send the plan by Monday.
"""

CLIENT_NAME = "Riya Mehta"
COMPANY = "Mehta Organics"
CALL_DATE = "2026-10-26"
DOC_TITLE = f"Client - {CLIENT_NAME} - {CALL_DATE}"
CALCOM_PLACEHOLDER = "[CAL.COM BOOKING LINK]"

SUMMARY = {
    "Client and business": "Riya Mehta, Mehta Organics. Sells cold-pressed oils online; approximately 400 orders per month.",
    "Current team / workflow": "Riya and one part-time team member, Arjun. Riya spends evenings replying to WhatsApp customers and chasing payments.",
    "Goals / success in three months": [
        "Get evenings back.",
        "Automate payment reminders.",
        "Understand which wholesale customers are worth retaining.",
    ],
    "Pain points": [
        "Manual customer replies on WhatsApp take up evenings.",
        "Wholesale buyers pay late; three shops owe approximately ₹1.8 lakh in total.",
        "A previous chatbot sent incorrect prices, so Riya is concerned about automation communicating directly with customers.",
    ],
    "Budget": "₹25,000–₹30,000 per month was mentioned, subject to discussion with her husband, who handles finances. Not confirmed/approved.",
    "Timeline": "Desired outcomes within three months. Short plan requested by Monday. Workflow mapping session next week; Thursday afternoon works. Exact date/time [CONFIRM].",
    "Objections / risks": [
        "Concern that customer-facing automation could send incorrect prices.",
        "Budget decision requires discussion with her husband.",
    ],
    "Agreed next steps": [
        "Consultant sends a short plan by Monday.",
        "Schedule a 45-minute workflow mapping session next week; Thursday afternoon is acceptable. Confirm exact date/time.",
    ],
    "Details to confirm": [
        "Exact date and time for the Thursday workflow mapping session.",
        "Whether the stated monthly budget is approved after the finance discussion.",
        "Current tools/platforms and any required integrations [CONFIRM].",
        "Rules and approval controls for payment reminders and customer-facing messages [CONFIRM].",
    ],
}

EMAIL_SUBJECT = "Next steps for Mehta Organics workflow automation"
EMAIL_BODY = """Hi Riya,

Thank you for speaking with me on Monday. It was helpful to hear more about Mehta Organics and your goal of getting your evenings back from manual WhatsApp replies and payment follow-ups.

Based on our conversation, I’ll put together a short plan focused on automating payment reminders and reducing repetitive customer communication, while keeping safeguards in place so customer-facing messages and prices can be reviewed before anything goes out. We can also explore how to make wholesale-customer follow-up more consistent.

As agreed, I’ll share the plan by Monday. The next step would be a 45-minute workflow-mapping session next week. Thursday afternoon works for you; please use the link below to choose a suitable time, or let me know if you’d prefer to confirm the time by email:

[CAL.COM BOOKING LINK]

In the session, we can map the current process, identify the tools involved, and agree on where automation should require human approval.

Best regards,
[YOUR NAME]
"""

WHATSAPP_TEXT = "Hi Riya, I’ll share the short workflow-automation plan by Monday. Thursday afternoon works for the 45-minute mapping session—please book a suitable time here: [CAL.COM LINK]. We’ll cover payment reminders and safe customer-message approvals."


def authenticate():
    if not CLIENT_SECRET_FILE.exists():
        raise FileNotFoundError(
            "credentials.json not found. Download an OAuth Desktop app client JSON from Google Cloud and save it beside agent.py as credentials.json."
        )
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    return creds


def summary_text() -> str:
    lines = [
        f"CLIENT: {CLIENT_NAME}", f"COMPANY: {COMPANY}", f"CALL DATE: {CALL_DATE}",
        "SOURCE: Fictional discovery-call transcript supplied with the assignment.", "",
    ]
    for heading, value in SUMMARY.items():
        lines.append(heading.upper())
        if isinstance(value, list):
            lines.extend([f"• {item}" for item in value])
        else:
            lines.append(value)
        lines.append("")
    lines.extend([
        "PRIVACY / CONTENT HANDLING", 
        "• Client's personal phone number omitted; it was explicitly restricted from sharing with Arjun.",
        "• Off-record speculation about a wholesale customer's financial condition excluded entirely from all artifacts.",
        "• No email is sent. Follow-up is saved as a Gmail draft for human review.",
        "",
        "WHATSAPP-LENGTH REMINDER (TEXT ONLY)", WHATSAPP_TEXT,
    ])
    return "\n".join(lines)


def create_drive_folder_and_doc(drive, docs):
    folder = drive.files().create(
        body={"name": DOC_TITLE, "mimeType": "application/vnd.google-apps.folder"},
        fields="id,name,webViewLink",
    ).execute()
    doc = docs.documents().create(body={"title": DOC_TITLE}).execute()
    doc_id = doc["documentId"]
    docs.documents().batchUpdate(
        documentId=doc_id,
        body={"requests": [{"insertText": {"location": {"index": 1}, "text": summary_text()}}]},
    ).execute()
    drive.files().update(
        fileId=doc_id,
        addParents=folder["id"],
        fields="id,name,parents,webViewLink",
    ).execute()
    return folder, {"id": doc_id, "name": DOC_TITLE, "url": f"https://docs.google.com/document/d/{doc_id}/edit"}


def create_gmail_draft(gmail):
    # No To address is invented. User must add/confirm the recipient before sending.
    raw_message = (
        f"Subject: {EMAIL_SUBJECT}\r\n"
        "Content-Type: text/plain; charset=UTF-8\r\n\r\n"
        + EMAIL_BODY
    )
    import base64
    encoded = base64.urlsafe_b64encode(raw_message.encode("utf-8")).decode("ascii")
    draft = gmail.users().drafts().create(userId="me", body={"message": {"raw": encoded}}).execute()
    return draft


def main():
    print("After the Discovery Call agent — dry-run preview before Google changes")
    print("Client: Riya Mehta / Mehta Organics | Call date: 2026-10-26")
    print("Safety: creates a Drive folder + Doc and Gmail DRAFT only; never sends email.\n")
    print("WhatsApp reminder (", len(WHATSAPP_TEXT), "characters):", sep="")
    print(WHATSAPP_TEXT, "\n")
    confirm = input("Create the Google Drive folder/Doc and Gmail draft in the signed-in account? Type CREATE to continue: ").strip()
    if confirm != "CREATE":
        print("Cancelled. No Google files or drafts were created.")
        return
    creds = authenticate()
    drive = build("drive", "v3", credentials=creds)
    docs = build("docs", "v1", credentials=creds)
    gmail = build("gmail", "v1", credentials=creds)
    folder, doc = create_drive_folder_and_doc(drive, docs)
    draft = create_gmail_draft(gmail)
    print("\nDone. The email was saved as a DRAFT and was NOT sent.")
    print(f"Drive folder: https://drive.google.com/drive/folders/{folder['id']}")
    print(f"Google Doc: {doc['url']}")
    print(f"Gmail draft ID: {draft.get('id', '[not returned]')} — open Gmail > Drafts to review.")
    print("Before approval, add the correct recipient, replace the Cal.com placeholder, verify the Monday/Thursday dates, and review all content.")

if __name__ == "__main__":
    try:
        main()
    except HttpError as exc:
        print(f"Google API error: {exc}")
        print("Check that Drive API, Docs API, and Gmail API are enabled and OAuth scopes were approved.")
    except Exception as exc:
        print(f"Agent stopped safely: {exc}")
        print("No email is sent by this script. Fix the issue and rerun; review Drive/Drafts before retrying to avoid duplicates.")
