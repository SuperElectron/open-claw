import json

new_leads = [
  {"name": "Sonali O.", "profile_url": "https://www.linkedin.com/sales/lead/ACwAAF71socB3jBRqhWBi9-QrF_ugV4YEecY-wQ,NAME_SEARCH,qt-u", "status": "new", "scanned_at": "2026-02-25T14:44:00Z"},
  {"name": "Nagasaikumar Jampani", "profile_url": "https://www.linkedin.com/sales/lead/ACwAAFiUjsIBNd_DBn3CkZAwrsEnCc0JZRgPSug,NAME_SEARCH,E-uU", "status": "new", "scanned_at": "2026-02-25T14:44:00Z"},
  {"name": "Abhiram Reddy Pudi", "profile_url": "https://www.linkedin.com/sales/lead/ACwAAEMyNbgBUS2iHmbm3OjkTJQ1CLDaNljNsm4,NAME_SEARCH,42gm", "status": "new", "scanned_at": "2026-02-25T14:44:00Z"},
  {"name": "Jackson Wilson", "profile_url": "https://www.linkedin.com/sales/lead/ACwAADpIlvABAIDrGRezsv8CWwEIJRYW12HRZug,NAME_SEARCH,z5S4", "status": "new", "scanned_at": "2026-02-25T14:44:00Z"},
  {"name": "Matthew Charles Busel", "profile_url": "https://www.linkedin.com/sales/lead/ACwAADlzxtQBmGxQBKWnlSEefB1qfBdltl6HHw8,NAME_SEARCH,RUX6", "status": "new", "scanned_at": "2026-02-25T14:44:00Z"},
  {"name": "SHASHANK RAJ", "profile_url": "https://www.linkedin.com/sales/lead/ACwAADeWLpMBqGbylip5_gtgKJkR_nwDYTgnCnk,NAME_SEARCH,KoOI", "status": "new", "scanned_at": "2026-02-25T14:44:00Z"},
  {"name": "Karan Kakadiya", "profile_url": "https://www.linkedin.com/sales/lead/ACwAADPGfLgBGy5y5PYTRNjJ4W6KJEDPq0yC7CA,NAME_SEARCH,wYgl", "status": "new", "scanned_at": "2026-02-25T14:44:00Z"},
  {"name": "Lauren Kuck", "profile_url": "https://www.linkedin.com/sales/lead/ACwAADMbG8MB7aGwElFIDVCiVYjM8z56c4uXtQg,NAME_SEARCH,ciHY", "status": "new", "scanned_at": "2026-02-25T14:44:00Z"},
  {"name": "Siddhant K.", "profile_url": "https://www.linkedin.com/sales/lead/ACwAADFaMCEBdHv-MUJSC8AmEm37M6LUpTP6drE,NAME_SEARCH,6QhX", "status": "new", "scanned_at": "2026-02-25T14:44:00Z"},
  {"name": "Amir Hesam Salimnia", "profile_url": "https://www.linkedin.com/sales/lead/ACwAACi7I5QB1MxXZRlQ38vfuSgL7bNxaW0-k_k,NAME_SEARCH,nhpo", "status": "new", "scanned_at": "2026-02-25T14:44:00Z"},
  {"name": "Varun Sharma", "profile_url": "https://www.linkedin.com/sales/lead/ACwAACQEEAIBvoj2TUaJMbpAz7xVHHStAZ0ZpoA,NAME_SEARCH,eXHW", "status": "new", "scanned_at": "2026-02-25T14:44:00Z"},
  {"name": "Salma Mayorquin", "profile_url": "https://www.linkedin.com/sales/lead/ACwAACHRTycB5aFCmJyBXJdceVdMgq1hZTdHRdU,NAME_SEARCH,xrG3", "status": "new", "scanned_at": "2026-02-25T14:44:00Z"},
  {"name": "Josh Williams", "profile_url": "https://www.linkedin.com/sales/lead/ACwAABlxQfkB3f416be18AZ1e8d5DWFmFbIta6k,NAME_SEARCH,6vF5", "status": "new", "scanned_at": "2026-02-25T14:44:00Z"},
  {"name": "Matt Turk", "profile_url": "https://www.linkedin.com/sales/lead/ACwAABXje1UBowAOJDiNpxIYzbjIG0OPRcwUJf8,NAME_SEARCH,pygA", "status": "new", "scanned_at": "2026-02-25T14:44:00Z"},
  {"name": "Shivangi J.", "profile_url": "https://www.linkedin.com/sales/lead/ACwAAA_luTIBmWQcE7LW5CCE5x0YPSiZa4Qmm58,NAME_SEARCH,YC-_", "status": "new", "scanned_at": "2026-02-25T14:44:00Z"},
  {"name": "Ehsan Nezhadarya", "profile_url": "https://www.linkedin.com/sales/lead/ACwAAAnG8RsBB2rmBoK__6CsJfsy-FWiW_tzJkc,NAME_SEARCH,33yQ", "status": "new", "scanned_at": "2026-02-25T14:44:00Z"},
  {"name": "Melek O.", "profile_url": "https://www.linkedin.com/sales/lead/ACwAAAbDVCIBk4l2ffYRWqzSm7qIn1MuK6gvWeg,NAME_SEARCH,yVTL", "status": "new", "scanned_at": "2026-02-25T14:44:00Z"},
  {"name": "Thukanaickanpalayam Selvakumaran", "profile_url": "https://www.linkedin.com/sales/lead/ACwAAAB-HEkBV_1YeqlPsRfKJnDzoaY-FYM0wH8,NAME_SEARCH,aQ0v", "status": "new", "scanned_at": "2026-02-25T14:44:00Z"},
  {"name": "Vigneshwaran Moorthi", "profile_url": "https://www.linkedin.com/sales/lead/ACwAAEcatxwBvoGZ8ZnCL4AFB20Up1go83GCCrk,NAME_SEARCH,gnBy", "status": "new", "scanned_at": "2026-02-25T14:44:00Z"},
  {"name": "Umaima Khan", "profile_url": "https://www.linkedin.com/sales/lead/ACwAADuZoLsBOkCqD2iHx0TekYFdu-ZfYipZG38,NAME_SEARCH,V6eq", "status": "new", "scanned_at": "2026-02-25T14:44:00Z"},
  {"name": "Amir Zeinali", "profile_url": "https://www.linkedin.com/sales/lead/ACwAADHkFAoB-WWb4m2Vgm4x2-HnEBpY8YIyWz4,NAME_SEARCH,SGM4", "status": "new", "scanned_at": "2026-02-25T14:44:00Z"},
  {"name": "Midam Kim, PhD 김미담", "profile_url": "https://www.linkedin.com/sales/lead/ACwAAC4BK_QBT_dGS4O8st_1oKlY84cae9_IH-4,NAME_SEARCH,IyEq", "status": "new", "scanned_at": "2026-02-25T14:44:00Z"},
  {"name": "Arnab Kumar Chand", "profile_url": "https://www.linkedin.com/sales/lead/ACwAAA-X76YBj9y5XAg83L_7J5834Y3YJ7338Ok,NAME_SEARCH,missing", "status": "new", "scanned_at": "2026-02-25T14:44:00Z"}
]

with open('/Users/mat/.openclaw/workspace/skills/linkedInSalesNavigator/.cache/temp_leads.json', 'r+') as f:
    data = json.load(f)
    data.extend(new_leads)
    f.seek(0)
    json.dump(data, f)
