---
name: linkedinSalesNavigator
description: LinkedIn Sales Navigator automation via browser relay or cookies for messaging, profile viewing, and network actions.
homepage: https://www.linkedin.com/sales/home
metadata: {"clawdbot":{"emoji":"💼"}}
---

# LinkedIn Sales Navigator

**Purpose:** Advanced LinkedIn Sales Navigator interactions. Use to interact with leads and accounts in the Sales Navigator interface.

**Distinction:** This is `linkedinSalesNavigator` (Hunter/Outbound). Use `linkedin` (Standard) for "Farmer" / Relationship Management tasks.

**Data Store:** `/Users/mat/.openclaw/workspace/skills/linkedInSalesNavigator/.cache/sales_nav_data.json`

## Connection Instructions

1. Use `browser` tool with `profile="openclaw"` 
2. Navigate to [linkedin.com/sales/home](https://www.linkedin.com/sales/home)
3. Log in manually (one-time setup)
4. Session persists for future use

## Core Workflows

### 1. Register Lead List
**Goal:** specific lists to track (ignore auto-generated ones unless explicitly added).
1.  **Input:** List Name and URL.
2.  **Action:** Load `sales_nav_data.json`.
3.  **Extract ID:** Parse the List ID from the URL (e.g., `/sales/lists/people/7420...`).
4.  **Update Registry:** Add entry to `lists_registry`:
    ```json
    "7420...": { "name": "My List", "url": "...", "last_scanned": null }
    ```
5.  **Save:** Write back to JSON.

### 2. Scan Lead List (Discovery)
**Goal:** Scrape leads from a registered list and update their status.
1.  **Navigate** to the List URL.
2.  **Snapshot** the page.
3.  **Parse:** Identify lead rows. For each lead:
    *   **Name:** (e.g., "Scott Brindamour")
    *   **Profile URL:** (e.g., `/sales/lead/ACw...`)
    *   **Status:** specific text detection ("Invitation sent", "Connected", "1st", "Pending" -> "pending"; else "new").
4.  **Update JSON:**
    *   Load `sales_nav_data.json`.
    *   Locate/Create the array in `leads_data[ListID]`.
    *   Upsert leads (match by Profile URL). Update `status` and `scanned_at`.
    *   Update `lists_registry[ListID].last_scanned`.
5.  **Save:** Write back to JSON.

### 3. Process Lead Batch (Execution)
**Goal:** Connect with "new" leads in a reliable, one-by-one manner.
1.  **Read** `sales_nav_data.json`.
2.  **Target:** Select a List ID to process.
3.  **Filter:** Get leads from `leads_data[ListID]` where `status` == "new".
4.  **Iterate:**
    *   **Navigate** directly to the `profile_url`.
    *   **Snapshot** to confirm page load.
    *   **Connect:** Click "Connect" (primary) or "Actions" -> "Connect".
    *   **Confirm:** Click "Send Invitation" in the modal.
    *   **Update JSON:** *Immediately* mark status as "pending" in the file.
    *   **Wait:** **3 seconds** safety pause.

## Common Operations

### Scrape Message Contacts (Inbox)
**Phase 1: Discovery**
1. Navigate to `https://www.linkedin.com/sales/inbox`.
2. Scroll sidebar, extract names/dates.
3. Save to `generated/sales_nav_conversations.md`.

**Phase 2: Enrichment**
1. Click conversation -> Wait -> Read URL.
2. Update markdown file.

### Check Home/Feed Status
```
browser action=snapshot profile=openclaw targetUrl="https://www.linkedin.com/sales/home"
```

### View Inbox
```
browser action=navigate profile=openclaw targetUrl="https://www.linkedin.com/sales/inbox"
```

### Search Leads
```
browser action=navigate profile=openclaw targetUrl="https://www.linkedin.com/sales/search/people?keywords=QUERY"
```

## Data Structure Reference
```json
{
  "lists_registry": {
    "LIST_ID": { 
      "name": "List Name",
      "url": "https://...",
      "last_scanned": "ISO_DATE"
    }
  },
  "leads_data": {
    "LIST_ID": [ 
      {
        "name": "Lead Name",
        "profile_url": "https://...",
        "status": "new", 
        "scanned_at": "ISO_DATE"
      }
    ]
  }
}
```

## Safety Rules
- **Never send messages without explicit user approval**
- **Never accept/send connection requests without confirmation**
- **Avoid rapid automated actions** - LinkedIn is aggressive about detecting automation
- Rate limit: ~30 actions per hour max recommended
