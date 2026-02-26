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

Manage the CRM system in Notion using the `notion` tool (API).

**CRITICAL CONSTRAINT:** Do NOT use the `browser` tool to access Notion. All CRM operations must be performed via the `notion` CLI/API tool. Browser access is slow, requires login, and is strictly forbidden for CRM tasks.

The CRM is structured as a "Deals" catalog, where each Deal page contains its own inline "pipeline" database for specific opportunities.

## Guidelines

1.  **Structure:**
    - **Deals (Database):** Acts as a catalog of Pipelines (e.g., "persona: engineer").
    - **Pipeline (Child Database):** Located inside each Deal page. Contains the actual opportunities.
    - **Contacts/Companies:** Global databases linked to pipeline items.

2.  **Interactions:**
    - Append to open interactions in the Interactions database.

## Database IDs

- **Deals (Pipelines Catalog):** `3112ef1b-d057-8187-b012-fd3c60f99341`
- **Companies:** `3112ef1b-d057-8198-988b-f2cbc91851a9`
- **Contacts:** `3112ef1b-d057-8151-85b3-dabd10c687d1`
- **Interactions:** `3112ef1b-d057-81e0-8690-ecf365c277b3`

## Functions

### `list_deals()`

List all active Pipelines from the Deals database.

```bash
# Returns list of active pipelines (e.g., "persona: engineer") and their Page IDs
notion query_db "3112ef1b-d057-8187-b012-fd3c60f99341" --filter '{"property": "Status", "select": {"equals": "Active"}}'
```

### `get_pipeline_items(deal_page_id)`

Get opportunities from a specific pipeline.
1. List children of the Deal Page to find the `child_database` (the pipeline).
2. Query that child database ID.

```bash
# Step 1: Find the child database ID
notion get_children <deal_page_id>

# Step 2: Query the child database found
notion query_db <child_database_id>
```

### `add_opportunity(deal_page_id, name, contact_id, status="todo")`

Add an opportunity to a specific pipeline.
1. Find the child database ID inside `deal_page_id`.
2. Create a page in that database.

```bash
notion create_page --db <child_database_id> --title "New Opp" --props '{"Status": {"status": {"name": "todo"}}, "contact": {"relation": [{"id": "..."}]}}'
```

### `add_contact(name, company_name)`

Create a new contact.

```bash
# Pseudocode - see Notion skill for exact syntax
notion create_page --db "3112ef1b-d057-8151-85b3-dabd10c687d1" ...
```
