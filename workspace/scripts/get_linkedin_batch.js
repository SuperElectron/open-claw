const fs = require('fs');
const path = require('path');

const DATA_FILE = '/Users/mat/.openclaw/workspace/skills/linkedInSalesNavigator/.cache/sales_nav_data.json';

try {
  // 1. Load Data
  if (!fs.existsSync(DATA_FILE)) {
    console.error(JSON.stringify({ error: "Data file not found" }));
    process.exit(1);
  }
  const data = JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));

  // 2. Find eligible lists (lists with at least 5 'new' leads)
  const eligibleLists = [];
  for (const [listId, leads] of Object.entries(data.leads_data || {})) {
    const newLeads = leads.filter(l => l.status === 'new');
    if (newLeads.length >= 5) {
      eligibleLists.push({ listId, count: newLeads.length });
    }
  }

  if (eligibleLists.length === 0) {
    console.log(JSON.stringify({ leads: [], message: "No lists have 5+ new leads." }));
    process.exit(0);
  }

  // 3. Randomly select a list
  const selectedListMeta = eligibleLists[Math.floor(Math.random() * eligibleLists.length)];
  const listId = selectedListMeta.listId;
  const allLeads = data.leads_data[listId];
  
  // 4. Grab top 5 'new' leads
  const batch = [];
  let found = 0;
  for (let i = 0; i < allLeads.length && found < 5; i++) {
    if (allLeads[i].status === 'new') {
      // Mark as 'processing' so next run doesn't grab them immediately
      // The Agent will verify connection and flip them to 'invited' or 'pending' later,
      // or revert them if it fails. For now, we lock them.
      allLeads[i].status = 'processing'; 
      batch.push(allLeads[i]);
      found++;
    }
  }

  // 5. Save updated status back to file
  fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2));

  // 6. Output the batch for the Agent
  console.log(JSON.stringify({ 
    listId, 
    leads: batch 
  }, null, 2));

} catch (err) {
  console.error(JSON.stringify({ error: err.message }));
  process.exit(1);
}
