const https = require('https');

const API_KEY = process.env.NOTION_API_KEY;
const DATABASE_ID = process.argv[2] || '3102ef1b-d057-8006-8ae6-cf9c44279754';
const STATUS = process.argv[3] || 'start';

if (!API_KEY) {
  console.error('Error: NOTION_API_KEY env var is missing.');
  process.exit(1);
}

const data = JSON.stringify({
  filter: {
    property: "Status",
    status: {
      equals: STATUS
    }
  },
  page_size: 100 // Default max page size
});

const options = {
  hostname: 'api.notion.com',
  path: `/v1/databases/${DATABASE_ID}/query`,
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${API_KEY}`,
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json',
    'Content-Length': data.length
  }
};

const req = https.request(options, (res) => {
  let body = '';
  res.on('data', (chunk) => body += chunk);
  res.on('end', () => {
    if (res.statusCode >= 200 && res.statusCode < 300) {
      const response = JSON.parse(body);
      console.log(JSON.stringify({
        count: response.results.length,
        has_more: response.has_more,
        next_cursor: response.next_cursor,
        status: STATUS
      }, null, 2));
    } else {
      console.error(`Error: Status ${res.statusCode} - ${body}`);
      process.exit(1);
    }
  });
});

req.on('error', (e) => {
  console.error(`Problem with request: ${e.message}`);
  process.exit(1);
});

req.write(data);
req.end();
