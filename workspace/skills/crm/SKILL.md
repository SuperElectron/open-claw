---
name: crm
description: Manage the custom CRM in Notion (create contacts, companies, opportunities, and pipelines).
homepage: https://www.notion.so/matmccann/CRM-3112ef1bd057800393e0e3b9ac69b580
metadata:
  {
    "openclaw":
      { "emoji": "📇", "requires": { "env": ["NOTION_API_KEY"] }, "primaryEnv": "NOTION_API_KEY" },
  }
---

# crm

Manage the CRM system in Notion. This skill provides high-level functions to ensure data consistency, proper linking, and AI-ready logging.

## Guidelines

1.  **Interactions are Threads:**
    - An "Interaction" represents a conversation thread or event.
    - **Do not** create new pages for every message. Append to open interactions.
    - **Format:** `**[YYYY-MM-DD HH:MM] Speaker Name:** Message content...`

2.  **Pipeline Creation (Human-in-the-Loop):**
    - **To create a new pipeline:** Create a new page (row) in the **Deals** database.
    - **Do NOT** attempt to build the database structure via API.
    - **User Action:** The user must open the new page and click the desired **Database Template** (e.g., `dealPerson`) to apply the correct structure, views, and filters.

3.  **Relationships are Mandatory:**
    - **Contacts** -> **Company**.
    - **Opportunities** -> **Main Contact** or **Company**.
    - **Interactions** -> **Participants**.

## Database IDs

- **Deals (Pipelines Catalog):** `3112ef1b-d057-8187-b012-fd3c60f99341`
- **Companies:** `3112ef1b-d057-8198-988b-f2cbc91851a9`
- **Contacts:** `3112ef1b-d057-8151-85b3-dabd10c687d1`
- **People Opportunities (Legacy):** `3112ef1b-d057-81d7-8446-dd6266c7da37`
- **Company Opportunities (Legacy):** `3112ef1b-d057-8199-a7b8-d7b97afbd303`
- **Interactions:** `3112ef1b-d057-81e0-8690-ecf365c277b3`
- **Prompts:** `3112ef1b-d057-81d1-904e-eb03faac7c84`

## Functions

### `create_pipeline(name, description="New pipeline")`

Create a new deal/pipeline entry in the Deals database.
- **Outcome:** A new page in "Deals" with status "Active".
- **User Action:** Open the page and apply a template (e.g., `dealPerson`).

```bash
# Example
crm create_pipeline --name "Persona: Engineers"
```

### `add_company(name, website?, industry?, size?)`

Create a new company or return existing ID if name matches.

```bash
crm add_company --name "Acme Corp"
```

### `add_contact(name, company_name, email?, linkedin?, role?)`

Create a new contact linked to a company. Will find/create the company automatically.

```bash
crm add_contact --name "Alice Smith" --company "Acme Corp"
```

### `log_interaction(contact_name, text, speaker, type="LinkedIn", status="Open")`

Log a message or note.
- Finds/Creates active interaction.
- Appends text with timestamp/speaker.

```bash
crm log_interaction --contact "Alice Smith" --speaker "Mat" --text "Update..."
```
