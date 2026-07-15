# NetSchlr - Academic Email Extractor

## What is NetSchlr?

NetSchlr is a professional command-line tool for extracting academic email addresses from Google Scholar. It scrapes researcher profiles directly from search results, finds emails, and optionally performs OSINT (Open Source Intelligence) scans to find social media profiles and verify email validity.

---

## Features

- **Direct Google Scholar scraping** - No need to open each profile individually
- **Email extraction** - Finds emails from researcher cards and verified email texts
- **Email verification** - SMTP-based email validation (checks if email actually exists)
- **OSINT scanning** - Finds LinkedIn, GitHub, ResearchGate, ORCID, and 15+ other platforms
- **Cross-platform** - Works on Windows, Linux, and macOS
- **Colorful terminal output** - Easy to read logs with colors
- **CSV export** - Saves results with all found data
- **Interactive menu** - User-friendly command-line interface

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Quick Install

```bash
# Clone or download the script
# Then install dependencies:
pip install pandas playwright dnspython

# Install Playwright browser:
playwright install chromium
```

### Install All at Once

```bash
pip install pandas playwright dnspython && playwright install chromium
```

---

## Usage

### Basic Usage

```bash
python netschlr.py
```

### Menu Options

```
1. Search researchers (new)     - Scrape Google Scholar for researchers
2. OSINT only (existing CSV)    - Add OSINT data to existing CSV
3. Verify emails only (existing CSV) - Verify emails in existing CSV
4. Save cookies (first time)    - Save Google Scholar cookies (required once)
5. Exit                         - Close the program
```

### First Time Setup

1. Run `python netschlr.py`
2. Select option `4` (Save cookies)
3. Browser will open to Google Scholar
4. Login to your Google account
5. Return to terminal and press ENTER
6. Cookies are saved for future use

### Search Example

```bash
python netschlr.py
# Select option 1
# Enter query: "kimya" or "artificial intelligence"
# Enter max results: 100
# Choose options for OSINT and verification
```

### Command Line Arguments (Optional)

```bash
# Save cookies only
python netschlr.py --save-cookies

# Run with specific query (skips menu)
python netschlr.py --query "physics" --max 50

# Enable OSINT
python netschlr.py --query "biotech" --osint

# Verify emails
python netschlr.py --query "chemistry" --verify

# Show browser
python netschlr.py --query "data science" --visible
```

---

## Output

### CSV File Structure

| Column | Description |
|--------|-------------|
| Name | Researcher's full name |
| Email | Found or generated email |
| Verified | Whether email was directly found |
| Institution | Academic institution |
| Interests | Research interests |
| Citations | Citation count |
| Profile URL | Google Scholar profile link |
| ORCID | ORCID identifier |
| LinkedIn | LinkedIn profile URL |
| GitHub | GitHub profile URL |
| ResearchGate | ResearchGate profile |
| Email_Status | SMTP verification status |
| Email_Valid | Yes/No based on verification |

### Example Output

```
saved/scholar_kimya_20250101_120000.csv
```

---

## OSINT Platforms Scanned

- LinkedIn
- Twitter
- ResearchGate
- Academia.edu
- GitHub
- ORCID
- Publons
- Medium
- StackOverflow
- Facebook
- Instagram
- YouTube
- TikTok
- Pinterest
- Reddit
- Quora
- Goodreads
- Personal websites

---

## Troubleshooting

### Missing Dependencies

```
Error: Missing: pip install pandas playwright dnspython
```

Solution:
```bash
pip install pandas playwright dnspython
playwright install chromium
```

### Cookie Error

```
Warning: No cookies found!
```

Solution: Run option `4` (Save cookies) first.

### CAPTCHA Detected

If CAPTCHA appears:
1. Run with `--visible` flag
2. Solve CAPTCHA in browser
3. Press ENTER in terminal

### Windows Color Issues

If colors don't show correctly:
```bash
# In Command Prompt
color

# In PowerShell
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::UTF8
```

---

## File Structure

```
netschlr/
├── netschlr.py          # Main script
├── saved/               # Output CSV files
│   └── scholar_*.csv
├── scholar_cookies.json # Saved cookies
└── README.md            # This file
```

---

## Dependencies

| Package | Purpose |
|---------|---------|
| pandas | CSV export |
| playwright | Browser automation |
| dnspython | DNS queries for email verification |

---

## Performance Tips

1. **Headless mode** - Faster scraping (default)
2. **Disable OSINT** - Skip social media scanning for speed
3. **Disable verification** - Skip SMTP checks for speed
4. **Lower max results** - Start with 20-50 for testing
5. **Increase delay** - Use `--delay 2.0` to avoid rate limiting

---

## Limitations

- Requires Google Scholar cookies (login required once)
- SMTP verification may not work with all email servers
- Some universities hide emails from public view
- Rate limiting may occur with large queries

---

## License

MIT License - Free for academic and personal use.

---

## Support

For issues:
1. Check dependencies are installed
2. Run with `--visible` to see browser
3. Check internet connection
4. Verify cookies are saved correctly

---

## Version History

- **v1.0.0** - Initial release
  - Google Scholar scraping
  - Email extraction
  - OSINT scanning
  - Email verification
  - Colorful terminal output

---

## Quick Reference

```bash
# Interactive mode
python netschlr.py

# Save cookies only
python netschlr.py --save-cookies

# Quick search
python netschlr.py --query "ai" --max 20

# Full search with all features
python netschlr.py --query "machine learning" --max 100 --osint --verify --visible
```

---
