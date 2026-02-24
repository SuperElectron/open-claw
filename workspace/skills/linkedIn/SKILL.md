---
name: linkedin
description: LinkedIn automation via browser relay or cookies for messaging, profile viewing, and network actions.
homepage: https://linkedin.com
metadata: {"clawdbot":{"emoji":"💼"}}
---

# LinkedIn (Standard / Basic)

**Purpose:** Basic LinkedIn interactions. Use this for general messaging, checking notifications, viewing individual profiles, and non-Sales Navigator searches.

**Distinction:** This is **NOT** `linkedinSalesNavigator`. Do not use this for "Leads", "Accounts", or advanced filtering. Use `linkedinSalesNavigator` for those "Hunter" tasks. This skill is for "Farmer" / Relationship Management tasks.

## Connection Methods

### Option 1: Chrome Extension Relay (Recommended)
1. Open LinkedIn in Chrome and log in
2. Click the Clawdbot Browser Relay toolbar icon to attach the tab
3. Use `browser` tool with `profile="chrome"`

### Option 2: Isolated Browser
1. Use `browser` tool with `profile="clawd"` 
2. Navigate to linkedin.com
3. Log in manually (one-time setup)
4. Session persists for future use

## Common Operations

### Scrape Message Contacts (Discovery & Enrichment)
Use this procedure to extract a list of people messaged within a date range and their direct thread URLs. This method is robust against LinkedIn's DOM structure.

**Phase 1: Discovery**
1. Navigate to `https://www.linkedin.com/messaging/` (`profile="chrome"`).
2. Scroll the conversation sidebar to load history back to the target date.
3. Extract names and dates from the list items.
4. Save the initial list (e.g., to `generated/linkedin_conversations.md`).

**Phase 2: Enrichment (Get URLs)**
Iterate through the names in the list:
1. Find the person's name in the sidebar.
2. Click the conversation item.
3. **Wait 2-3 seconds** for the URL bar to update (it changes to `.../messaging/thread/...`).
4. Read the current URL (`window.location.href`).
5. Update the markdown file with the format: `- Name: [URL]`. the markdown file is stored in `workspace/generated/` and you can give it a name that does not conflict with any existing files in that directory (unless the user specifies a name)
6. Process in batches of 5-10 to ensure stability.

### Check Connection Status
```
browser action=snapshot profile=chrome targetUrl="https://www.linkedin.com/feed/"
```

### View Notifications/Messages
```
browser action=navigate profile=chrome targetUrl="https://www.linkedin.com/messaging/"
browser action=snapshot profile=chrome
```

### Search People
```
browser action=navigate profile=chrome targetUrl="https://www.linkedin.com/search/results/people/?keywords=QUERY"
browser action=snapshot profile=chrome
```

### View Profile
```
browser action=navigate profile=chrome targetUrl="https://www.linkedin.com/in/USERNAME/"
browser action=snapshot profile=chrome
```

### Send Message (confirm with user first!)
1. Navigate to messaging or profile
2. Use `browser action=act` with click/type actions
3. Always confirm message content before sending

## Safety Rules
- **Never send messages without explicit user approval**
- **Never accept/send connection requests without confirmation**
- **Avoid rapid automated actions** - LinkedIn is aggressive about detecting automation
- Rate limit: ~30 actions per hour max recommended

## Session Cookie Method (Advanced)
If browser relay isn't available, extract the `li_at` cookie from browser:
1. Open LinkedIn in browser, log in
2. DevTools → Application → Cookies → linkedin.com
3. Copy `li_at` value
4. Store securely for API requests

## Troubleshooting
- If logged out: Re-authenticate in browser
- If rate limited: Wait 24 hours, reduce action frequency
- If CAPTCHA: Complete manually in browser, then resume