---
name: crm
description: Manage the custom CRM in Notion (create contacts, companies, opportunities, and log interactions).
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
    - An "Interaction" represents a conversation thread (e.g., "LinkedIn Chat", "Email Chain") or a discrete event (e.g., "Discovery Call").
    - Do **not** create a new page for every single message in a thread. Append to the existing open interaction.
    - Use the `log_interaction` function to handle appending vs. creating.
    - **Format:** Always timestamp and label speakers in the body:
      `**[YYYY-MM-DD HH:MM] Speaker Name:** Message content...`

2.  **Relationships are Mandatory:**
    - **Contacts** must link to a **Company**.
    - **Opportunities** must link to a **Main Contact** (PeopleOp) or **Company** (CompanyOp).
    - **Interactions** must link to **Participants** (Contacts).

3.  **Deduplication:**
    - Always search for existing Companies/Contacts by name/email before creating new ones.

## Database IDs

- **Companies:** `3112ef1b-d057-8198-988b-f2cbc91851a9`
- **Contacts:** `3112ef1b-d057-8151-85b3-dabd10c687d1`
- **People Opportunities:** `3112ef1b-d057-81d7-8446-dd6266c7da37`
- **Company Opportunities:** `3112ef1b-d057-8199-a7b8-d7b97afbd303`
- **Interactions:** `3112ef1b-d057-81e0-8690-ecf365c277b3`
- **Prompts:** `3112ef1b-d057-81d1-904e-eb03faac7c84`

## Functions

### `add_company(name, website?, industry?, size?)`

Create a new company or return existing ID if name matches.

```bash
# Example
crm add_company --name "Acme Corp" --website "https://acme.com"
```

### `add_contact(name, company_name, email?, linkedin?, role?)`

Create a new contact linked to a company. Will find/create the company automatically.

```bash
# Example
crm add_contact --name "Alice Smith" --company "Acme Corp" --email "alice@acme.com"
```

### `log_interaction(contact_name, text, speaker, type="LinkedIn", status="Open")`

Log a message or note.
- Finds the most recent **Open** interaction of `type` for this contact.
- If found: Appends the text with timestamp/speaker to the page body.
- If not found (or closed): Creates a new Interaction page and adds the text.

```bash
# Example
crm log_interaction --contact "Alice Smith" --speaker "Mat" --text "Sent the proposal PDF." --type "Email"
```

### `create_opportunity(contact_name, type="people", status="New")`

Create a new deal in the pipeline.
- `type`: "people" (PeopleOp) or "company" (CompanyOp).

```bash
# Example
crm create_opportunity --contact "Alice Smith" --type "people" --status "Discovery"
```

## Implementation Notes (for Agent)

When executing these logical "functions", use the standard `notion` skill (curl commands).

1.  **Search First:** Always `POST /v1/databases/{id}/query` to find existing records.
2.  **Append Content:** Use `PATCH /v1/blocks/{page_id}/children` to add paragraphs to interaction pages.
3.  **Rich Text:** When creating pages, structure the `properties` JSON carefully matching the schema in `Database IDs`.
