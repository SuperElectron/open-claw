---
name: linkedin
description: LinkedIn automation via browser relay or cookies for messaging, profile viewing, and network actions.
homepage: https://linkedin.com
metadata: {"clawdbot":{"emoji":"💼"}, "model": "flash"}
---

# LinkedIn (Standard / Basic)

**Purpose:** Basic LinkedIn interactions. Use this for general messaging, checking notifications, viewing individual profiles, and non-Sales Navigator searches.

**Distinction:** This is **NOT** `linkedinSalesNavigator`. Do not use this for "Leads", "Accounts", or advanced filtering. Use `linkedinSalesNavigator` for those "Hunter" tasks. This skill is for "Farmer" / Relationship Management tasks.

## Connection Methods

### Option 1: Isolated Browser (Recommended)
1. Use `browser` tool with `profile="openclaw"` 
2. Navigate to linkedin.com
3. Log in manually (one-time setup)
4. Session persists for future use

## Common Operations

### Sync Conversation from URL (Preferred)
**Use this whenever a direct `LinkedIn Message URL` is available (e.g., from Notion).**
1.  **Navigate Direct:** `browser action=navigate targetUrl="<THE_URL_FROM_NOTION>"`
2.  **Verify:** `browser action=evaluate script="document.URL"`
3.  **Scrape History:** Follow the "Scrape Full Conversation History" procedure below.

### Scrape Full Conversation History

**CRITICAL:** Do NOT use `snapshot` for this. Use `evaluate` to extract data directly to save tokens.

1. **Load History (Repeat until done):** `browser action=evaluate script="const loader = document.querySelector('.msg-s-message-list-content__loader'); if(loader) { loader.click(); return 'loading'; } return 'finished';"`
2. **Extract Data:** Use `browser action=evaluate` with the following script:
```javascript
Array.from(document.querySelectorAll('.msg-s-message-list__event')).map(msg => {
  const sender = msg.querySelector('.msg-s-message-group__name')?.innerText.trim();
  const time = msg.querySelector('time')?.innerText.trim();
  const content = msg.querySelector('.msg-s-event-listitem__body')?.innerText.trim();
  return { sender: sender || "Inherited", timestamp: time, content: content };
});
```
3. **Format Output:** Return a JSON array of objects: `{ "sender": "Name", "timestamp": "YYYY-MM-DD HH:MM", "content": "Text" }`.

### Sync to Notion (Formatting Rule)
When updating the "Interaction" card in Notion:
1.  **Do NOT append blindly.** Check if history exists and overwrite or merge intelligently to avoid duplicates.
2.  **Format Rule:** Use a distinct block for metadata, followed by the message.
    *   **Block 1 (Metadata):** `[YYYY-MM-DD HH:MM] SENDER NAME` (Format: **Bold**, Color: **Gray**)
    *   **Block 2 (Content):** The message text.

### Scrape Message Contacts (Discovery & Enrichment)
Use this procedure to extract a list of people messaged within a date range and their direct thread URLs.

**Phase 1: Discovery**

1. Navigate to `https://www.linkedin.com/messaging/` (`profile="openclaw"`).
2. Scroll the conversation sidebar.
3. **Extract names via Evaluate:**
```javascript
Array.from(document.querySelectorAll('.msg-conversations-listitem')).map(item => ({
  name: item.querySelector('.msg-conversations-listitem__participant-names')?.innerText.trim(),
  date: item.querySelector('time')?.innerText.trim()
}));
```

**Phase 2: Enrichment (Get URLs)**
Iterate through the names in the list:

1. Find the person's name in the sidebar and click.
2. **Wait 2-3 seconds.**
3. **Read URL via Evaluate:** `browser action=evaluate script="window.location.href"`
4. Update the markdown file with the format: `- Name: [URL]`.

### Search People

1. `browser action=navigate profile=openclaw targetUrl="https://www.linkedin.com/search/results/people/?keywords=QUERY"`
2. **Extract via Evaluate:**
```javascript
Array.from(document.querySelectorAll('.reusable-search__result-container')).map(el => ({
  name: el.querySelector('.entity-result__title-text')?.innerText.trim(),
  link: el.querySelector('.app-aware-link')?.href
}));
```

### Send Message (confirm with user first!)
1. Navigate to messaging or profile
2. Use `browser action=act` with click/type actions
3. Always confirm message content before sending

## Safety Rules

* **Never use `snapshot` for large data extraction.** Always use `evaluate` to target specific text.
* **Never send messages without explicit user approval.**
* **Avoid rapid automated actions.** LinkedIn detects automation easily.
* Rate limit: ~30 actions per hour max recommended.
