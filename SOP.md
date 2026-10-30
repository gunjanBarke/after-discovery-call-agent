# One-page SOP: After the Discovery Call Agent

## Before you run it
1. Use only the approved transcript and fictional/sample data for this assignment.
2. Confirm Python is installed and the project dependencies are installed.
3. Check that `credentials.json` is your own Google OAuth Desktop app file. Never share or upload it. The first run opens Google sign-in.

## Run it
1. Open PowerShell in the project folder.
2. Run ` .\.venv\Scripts\python.exe agent.py `.
3. Read the preview. Type `CREATE` only if you want the script to create a Drive folder, Doc, and Gmail draft.
4. Complete Google authorization in the browser if asked.
5. Open the printed Drive folder/Doc link. Open Gmail → Drafts to find the email. The script does not send email.

## Check before approving the draft
- Confirm the recipient's email address yourself; it is deliberately left as a placeholder.
- Replace `[CAL.COM BOOKING LINK]` with the correct booking URL.
- Confirm the exact Thursday date/time. “Thursday afternoon” is not a precise appointment.
- Check the summary against the transcript, especially goals, objections, budget status, and agreed next steps.
- Make sure the personal phone number is absent and the off-record speculation about a wholesale customer is not included.
- Keep the email as a draft until you personally approve it. Do not send automatically.

## If something fails
- **Missing credentials.json:** download your Google OAuth Desktop app JSON and save it beside `agent.py` under that exact name.
- **Permission/API error:** enable Google Drive API, Google Docs API, and Gmail API in the same Google Cloud project; check OAuth consent/test-user setup.
- **Browser authorization problem:** rerun the script and complete consent. If scopes changed, remove local `token.json` and authorize again.
- **Partial run:** check Drive and Gmail Drafts before retrying. A partial failure can leave a folder/Doc behind and a rerun may create duplicates.
- **Never send an email to fix a failed run.** This script only creates a draft; diagnose the error first.

## Privacy rules
Never put real client transcripts into this fictional demo. Keep `credentials.json` and `token.json` private. The personal number is excluded, and the expressly off-record speculation is excluded from every output.
