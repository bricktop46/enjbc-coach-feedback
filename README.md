# ENJBC End of Season Coach Feedback App

A Streamlit app for coaches to submit end-of-season player feedback.

## Features
- Coach login (name-based)
- Admin login for president/operations to view all feedback
- Per-team player roster auto-populated from CSV
- 1-5 ratings for: Teamwork, Coachability, Shooting, Dribbling, Defence
- Grade Level assessment
- Open comments field
- Digital signature certification
- One submission per team (final)
- Mobile-friendly layout

## Local Development

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Community Cloud

1. Push this folder to a GitHub repository
2. Go to https://share.streamlit.io
3. Connect your GitHub account
4. Select the repo, branch, and `app.py` as the main file
5. Deploy

## Files
- `app.py` - Main application
- `participants.csv` - Season roster (Team, Player names, Roles)
- `feedback/` - Submitted feedback CSVs (one per team)
- `submitted_teams.json` - Tracks which teams have submitted
