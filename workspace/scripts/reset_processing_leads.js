const fs = require('fs');
const DATA_FILE = '/Users/mat/.openclaw/workspace/skills/linkedInSalesNavigator/.cache/sales_nav_data.json';

try {
  const data = JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
  let resetCount = 0;

  for (const listId in data.leads_data) {
    data.leads_data[listId].forEach(lead => {
      if (lead.status === 'processing') {
        lead.status = 'new';
        resetCount++;
      }
    });
  }

  fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2));
  console.log(`Reset ${resetCount} leads from 'processing' to 'new'.`);
} catch (err) {
  console.error(err);
}
