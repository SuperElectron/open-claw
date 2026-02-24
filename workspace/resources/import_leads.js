const fs = require('fs');
const https = require('https');

const CSV_PATH = '/Users/mat/.openclaw/workspace/linkedin_leads.csv';
const DATABASE_ID = '3102ef1b-d057-816d-89f3-da63ac3c05fa';
const API_KEY = process.env.NOTION_API_KEY;

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

async function createPage(row) {
  const data = JSON.stringify({
    parent: { database_id: DATABASE_ID },
    properties: {
      "Name": { title: [{ text: { content: row.Name || '' } }] },
      "URL": { url: row.URL || null },
      "Account": { rich_text: [{ text: { content: row.Account || '' } }] },
      "Geography": { rich_text: [{ text: { content: row.Geography || '' } }] },
      // Profile URL isn't in CSV yet, but we'll add it if it exists, otherwise leave blank
      "Profile URL": { url: null } 
    }
  });

  const options = {
    hostname: 'api.notion.com',
    path: '/v1/pages',
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Notion-Version': '2022-06-28',
      'Content-Type': 'application/json',
      'Content-Length': data.length
    }
  };

  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => body += chunk);
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(JSON.parse(body));
        } else {
          reject(new Error(`Status ${res.statusCode}: ${body}`));
        }
      });
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

// Simple CSV parser that handles quoted fields
function parseCSV(text) {
  const lines = text.trim().split('\n');
  const headers = lines[0].match(/(".*?"|[^",\s]+)(?=\s*,|\s*$)/g).map(h => h.replace(/^"|"$/g, ''));
  // This regex is a simple approximation; robust CSV parsing is complex but this covers standard quotes
  const data = [];
  
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i];
    const row = {};
    // Split by comma, respecting quotes
    const values = [];
    let current = '';
    let inQuote = false;
    for (let j = 0; j < line.length; j++) {
      const char = line[j];
      if (char === '"') {
        inQuote = !inQuote;
      } else if (char === ',' && !inQuote) {
        values.push(current.replace(/^"|"$/g, ''));
        current = '';
      } else {
        current += char;
      }
    }
    values.push(current.replace(/^"|"$/g, '')); // Last value

    headers.forEach((h, index) => {
      row[h] = values[index];
    });
    data.push(row);
  }
  return data;
}

async function main() {
  const fileContent = fs.readFileSync(CSV_PATH, 'utf8');
  const rows = parseCSV(fileContent);
  
  console.log(`Found ${rows.length} rows to import.`);

  for (let i = 0; i < rows.length; i++) {
    try {
      await createPage(rows[i]);
      console.log(`[${i+1}/${rows.length}] Added: ${rows[i].Name}`);
      await delay(350); // Rate limit respect (3 req/s safe zone)
    } catch (err) {
      console.error(`Failed to add ${rows[i].Name}:`, err.message);
    }
  }
  console.log('Import complete.');
}

main();
