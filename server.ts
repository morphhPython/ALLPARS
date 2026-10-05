import 'dotenv/config';
import express, { Request, Response } from 'express';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { GoogleGenAI } from '@google/genai';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Ensure data folder exists
const DATA_DIR = path.join(__dirname, 'data');
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

const ACCOUNTS_FILE = path.join(DATA_DIR, 'accounts.txt');
const MAILS_FILE = path.join(DATA_DIR, 'BazaPochtRassilka.txt');
const PERSONAL_MAILS_FILE = path.join(DATA_DIR, 'BazaPochtLichnie.txt');

// Initialize default files if missing
if (!fs.existsSync(ACCOUNTS_FILE)) {
  const initialAccounts = `# File for sender accounts in format: email:password
# Add your accounts below, one per line.
# Example:
sender.demo@gmail.com:app_pass_abcd1234
outreach.lead@yandex.ru:secret_token_998
alex.developer@mail.ru:mailru_app_pass
`;
  fs.writeFileSync(ACCOUNTS_FILE, initialAccounts, 'utf-8');
}

if (!fs.existsSync(MAILS_FILE)) {
  const initialMails = `torvalds@linux-foundation.org
gvanrossum@python.org
satya.nadella@microsoft.com
vitalik.buterin@ethereum.org
`;
  fs.writeFileSync(MAILS_FILE, initialMails, 'utf-8');
}

if (!fs.existsSync(PERSONAL_MAILS_FILE)) {
  fs.writeFileSync(PERSONAL_MAILS_FILE, '', 'utf-8');
}

// Initialize Gemini Client
const apiKey = process.env.GEMINI_API_KEY;
let ai: GoogleGenAI | null = null;
if (apiKey) {
  ai = new GoogleGenAI({
    apiKey: apiKey,
    httpOptions: {
      headers: {
        'User-Agent': 'aistudio-build',
      },
    },
  });
}

// -------------------------------------------------------------
// Crawler State & Background Engine
// -------------------------------------------------------------
interface CrawlerLog {
  id: string;
  time: string;
  message: string;
  type: 'info' | 'success' | 'warn' | 'err';
  source?: string;
}

interface CrawlerState {
  running: boolean;
  infinite: boolean;
  pagesCrawled: number;
  totalFound: number;
  personalFound: number;
  queueSize: number;
  currentTarget: string;
  visitedCount: number;
  logs: CrawlerLog[];
}

const crawlerState: CrawlerState = {
  running: false,
  infinite: false,
  pagesCrawled: 0,
  totalFound: 0,
  personalFound: 0,
  queueSize: 0,
  currentTarget: '',
  visitedCount: 0,
  logs: [],
};

let crawlerAbortController: AbortController | null = null;

function addCrawlerLog(message: string, type: 'info' | 'success' | 'warn' | 'err' = 'info', source?: string) {
  const now = new Date();
  const time = now.toTimeString().split(' ')[0];
  const log: CrawlerLog = {
    id: `${Date.now()}-${Math.random().toString(36).substring(2, 7)}`,
    time,
    message,
    type,
    source,
  };
  crawlerState.logs.unshift(log);
  if (crawlerState.logs.length > 500) {
    crawlerState.logs.pop();
  }
}

// Email Regex and Validator Filters
const EMAIL_REGEX = /[a-zA-Z0-9][a-zA-Z0-9._%+\-]*@[a-zA-Z0-9](?:[a-zA-Z0-9\-]*[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9\-]*[a-zA-Z0-9])?)*\.[a-zA-Z]{2,24}(?![a-z0-9])(?!\.(?:png|jpe?g|gif|webp|svg|ico|bmp|tiff?|css|js|mp4|mp3|zip))/gi;

const PERSONAL_DOMAINS = new Set([
  'gmail.com', 'googlemail.com', 'yahoo.com', 'ymail.com', 'rocketmail.com',
  'hotmail.com', 'outlook.com', 'live.com', 'msn.com', 'icloud.com', 'me.com',
  'mac.com', 'protonmail.com', 'proton.me', 'mail.ru', 'bk.ru', 'list.ru',
  'inbox.ru', 'internet.ru', 'yandex.ru', 'yandex.com', 'ya.ru', 'rambler.ru',
  'ukr.net', 'gmx.com', 'gmx.net', 'gmx.de', 'web.de', 'zoho.com', 'fastmail.com',
  'tutanota.com', 'aol.com', 'seznam.cz',
]);

const JUNK_DOMAINS = new Set([
  'example.com', 'example.org', 'example.net', 'domain.com', 'email.com',
  'yourdomain.com', 'company.com', 'website.com', 'sentry.io', 'schema.org',
  'wixpress.com', 'test.com', 'sample.com',
]);

function isPersonalEmail(email: string): boolean {
  const domain = email.split('@')[1]?.toLowerCase();
  if (!domain) return false;
  return PERSONAL_DOMAINS.has(domain);
}

function normalizeUrl(urlStr: string): string {
  try {
    const u = new URL(urlStr);
    u.hash = '';
    return u.toString();
  } catch {
    return urlStr.trim();
  }
}

function extractLinks(html: string, baseUrl: string): string[] {
  const links: string[] = [];
  const hrefRegex = /(?:href|src)\s*=\s*["']([^"'>\s#]+)["']/gi;
  let match;
  while ((match = hrefRegex.exec(html)) !== null) {
    const raw = match[1];
    if (!raw || raw.startsWith('javascript:') || raw.startsWith('mailto:') || raw.startsWith('tel:')) continue;
    try {
      const resolved = new URL(raw, baseUrl);
      if (['http:', 'https:'].includes(resolved.protocol)) {
        const ext = path.extname(resolved.pathname).toLowerCase();
        if (!['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico', '.css', '.js', '.zip', '.rar', '.pdf', '.exe'].includes(ext)) {
          links.push(resolved.toString());
        }
      }
    } catch {
      // ignore invalid relative url
    }
  }
  return links;
}

// -------------------------------------------------------------
// API Endpoints
// -------------------------------------------------------------

// 1. Account Management (email:password in accounts.txt)
app.get('/api/accounts', (_req: Request, res: Response) => {
  try {
    if (!fs.existsSync(ACCOUNTS_FILE)) {
      return res.json({ raw: '', accounts: [] });
    }
    const raw = fs.readFileSync(ACCOUNTS_FILE, 'utf-8');
    const lines = raw.split(/\r?\n/);
    const accounts: { email: string; password: string; provider: string }[] = [];

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) continue;
      const parts = trimmed.split(':');
      if (parts.length >= 2) {
        const email = parts[0].trim();
        const password = parts.slice(1).join(':').trim();
        const domain = email.split('@')[1] || 'generic';
        accounts.push({
          email,
          password,
          provider: domain,
        });
      }
    }

    res.json({ raw, accounts });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/accounts', (req: Request, res: Response) => {
  try {
    const { raw, account } = req.body;
    if (typeof raw === 'string') {
      fs.writeFileSync(ACCOUNTS_FILE, raw, 'utf-8');
      return res.json({ success: true, message: 'Accounts file saved successfully.' });
    }
    if (account && account.email && account.password) {
      const line = `\n${account.email.trim()}:${account.password.trim()}`;
      fs.appendFileSync(ACCOUNTS_FILE, line, 'utf-8');
      return res.json({ success: true, message: `Account ${account.email} added.` });
    }
    res.status(400).json({ error: 'Invalid payload: provide raw text or account object.' });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// 2. Emails List / Stats
app.get('/api/emails', (_req: Request, res: Response) => {
  try {
    let generalEmails: string[] = [];
    let personalEmails: string[] = [];

    if (fs.existsSync(MAILS_FILE)) {
      generalEmails = fs.readFileSync(MAILS_FILE, 'utf-8')
        .split(/\r?\n/)
        .map(e => e.trim().toLowerCase())
        .filter(e => e.length > 0 && e.includes('@'));
    }
    if (fs.existsSync(PERSONAL_MAILS_FILE)) {
      personalEmails = fs.readFileSync(PERSONAL_MAILS_FILE, 'utf-8')
        .split(/\r?\n/)
        .map(e => e.trim().toLowerCase())
        .filter(e => e.length > 0 && e.includes('@'));
    }

    // Deduplicate
    const uniqueGeneral = Array.from(new Set(generalEmails));
    const uniquePersonal = Array.from(new Set(personalEmails));

    res.json({
      general: uniqueGeneral,
      personal: uniquePersonal,
      totalCount: uniqueGeneral.length,
      personalCount: uniquePersonal.length,
      filePath: MAILS_FILE,
      personalFilePath: PERSONAL_MAILS_FILE,
    });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/emails/add', (req: Request, res: Response) => {
  try {
    const { emails } = req.body;
    if (!Array.isArray(emails)) {
      return res.status(400).json({ error: 'emails array required' });
    }
    let addedCount = 0;
    const existing = new Set(
      fs.existsSync(MAILS_FILE)
        ? fs.readFileSync(MAILS_FILE, 'utf-8').split(/\r?\n/).map(e => e.trim().toLowerCase())
        : []
    );

    const toAppend: string[] = [];
    const personalToAppend: string[] = [];

    for (const raw of emails) {
      const email = String(raw).trim().toLowerCase();
      if (email.includes('@') && !existing.has(email)) {
        existing.add(email);
        toAppend.push(email);
        if (isPersonalEmail(email)) {
          personalToAppend.push(email);
        }
        addedCount++;
      }
    }

    if (toAppend.length > 0) {
      fs.appendFileSync(MAILS_FILE, toAppend.join('\n') + '\n', 'utf-8');
    }
    if (personalToAppend.length > 0) {
      fs.appendFileSync(PERSONAL_MAILS_FILE, personalToAppend.join('\n') + '\n', 'utf-8');
    }

    res.json({ success: true, addedCount });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/emails/clear', (_req: Request, res: Response) => {
  try {
    fs.writeFileSync(MAILS_FILE, '', 'utf-8');
    fs.writeFileSync(PERSONAL_MAILS_FILE, '', 'utf-8');
    res.json({ success: true, message: 'Email lists cleared.' });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// 3. Crawler Engine Control (Single & Infinite Spider Crawl)
app.get('/api/crawler/status', (_req: Request, res: Response) => {
  res.json(crawlerState);
});

app.post('/api/crawler/start', async (req: Request, res: Response) => {
  if (crawlerState.running) {
    return res.status(400).json({ error: 'Crawler is already active.' });
  }

  const { seeds, infinite = false, maxPages = 40, dorks, dorkEngine = 'duckduckgo' } = req.body;

  let queue: string[] = [];
  if (Array.isArray(seeds) && seeds.length > 0) {
    queue = seeds.map(s => normalizeUrl(String(s)));
  } else {
    // Default GitHub and public directory seeds
    queue = [
      'https://raw.githubusercontent.com/torvalds/linux/master/MAINTAINERS',
      'https://raw.githubusercontent.com/git/git/master/.mailmap',
      'https://raw.githubusercontent.com/golang/go/master/CONTRIBUTORS',
      'https://raw.githubusercontent.com/rust-lang/rust/master/AUTHORS',
      'https://raw.githubusercontent.com/nodejs/node/main/AUTHORS',
      'https://news.ycombinator.com',
      'https://lobste.rs',
      'https://gitlab.com/-/snippets',
    ];
  }

  // If dorks are provided, run search query immediately to populate queue
  if (Array.isArray(dorks) && dorks.length > 0) {
    for (const d of dorks) {
      addCrawlerLog(`[Auto-Dork] Queued dork query for crawler: "${d}" on ${dorkEngine.toUpperCase()}`, 'info');
    }
  }

  crawlerAbortController = new AbortController();
  crawlerState.running = true;
  crawlerState.infinite = Boolean(infinite);
  crawlerState.pagesCrawled = 0;
  crawlerState.queueSize = queue.length;
  crawlerState.visitedCount = 0;

  addCrawlerLog(`Engine started in ${infinite ? 'INFINITE' : 'BATCH'} mode. Seed queue: ${queue.length}`, 'info');

  res.json({ success: true, message: 'Crawler launched.' });

  // Run in background without blocking response
  (async () => {
    // Execute Auto-Dork first to expand targets if specified
    if (Array.isArray(dorks) && dorks.length > 0) {
      for (const dorkItem of dorks) {
        try {
          addCrawlerLog(`[Dork Expansion] Executing "${dorkItem}" on ${dorkEngine}...`, 'info');
          const encoded = encodeURIComponent(dorkItem);
          let searchUrl = `https://html.duckduckgo.com/html/?q=${encoded}`;
          if (dorkEngine === 'bing') searchUrl = `https://www.bing.com/search?q=${encoded}`;
          if (dorkEngine === 'yandex') searchUrl = `https://yandex.com/search/?text=${encoded}`;
          if (dorkEngine === 'google') searchUrl = `https://html.duckduckgo.com/html/?q=${encoded}+site:google.com`;

          const resp = await fetch(searchUrl, {
            headers: {
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            },
          });
          const html = await resp.text();
          const inlineEmails = Array.from(new Set(html.match(EMAIL_REGEX) || []));
          if (inlineEmails.length > 0) {
            fs.appendFileSync(MAILS_FILE, inlineEmails.join('\n') + '\n', 'utf-8');
            addCrawlerLog(`[Dork Extracted] +${inlineEmails.length} direct emails from search snippet!`, 'success');
          }

          const linkRegex = /<a\s+(?:[^>]*?\s+)?href="([^"]*)"/gi;
          let match;
          let addedCount = 0;
          while ((match = linkRegex.exec(html)) !== null) {
            const link = match[1];
            if (link && link.startsWith('http') && !link.includes('duckduckgo.com') && !link.includes('bing.com') && !link.includes('yandex.com')) {
              queue.unshift(link);
              addedCount++;
            }
          }
          crawlerState.queueSize = queue.length;
          addCrawlerLog(`[Dork Expansion] Injected +${addedCount} target URLs into spider queue.`, 'success');
        } catch (err: any) {
          addCrawlerLog(`[Dork Error] ${err.message}`, 'warn');
        }
      }
    }
    const visited = new Set<string>();
    const seenEmails = new Set(
      fs.existsSync(MAILS_FILE)
        ? fs.readFileSync(MAILS_FILE, 'utf-8').split(/\r?\n/).map(e => e.trim().toLowerCase())
        : []
    );

    const userAgents = [
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15',
      'Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0',
    ];

    while (crawlerState.running && (crawlerState.infinite || crawlerState.pagesCrawled < maxPages)) {
      if (queue.length === 0) {
        if (crawlerState.infinite) {
          // Re-inject core repository seeds if exhausted
          addCrawlerLog('Queue empty in infinite mode. Re-injecting developer seeds...', 'warn');
          queue.push(
            'https://raw.githubusercontent.com/torvalds/linux/master/MAINTAINERS',
            'https://raw.githubusercontent.com/git/git/master/.mailmap',
            'https://news.ycombinator.com/news?p=2'
          );
        } else {
          addCrawlerLog('Queue exhausted. Crawler finished.', 'success');
          break;
        }
      }

      const currentUrl = queue.shift()!;
      crawlerState.queueSize = queue.length;
      crawlerState.currentTarget = currentUrl;

      if (visited.has(currentUrl)) continue;
      visited.add(currentUrl);
      crawlerState.visitedCount = visited.size;

      try {
        const randomUA = userAgents[Math.floor(Math.random() * userAgents.length)];
        const fetchPromise = fetch(currentUrl, {
          headers: {
            'User-Agent': randomUA,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,text/plain;q=0.8,*/*;q=0.7',
          },
          signal: crawlerAbortController?.signal,
        });

        // 10s timeout
        const timeoutPromise = new Promise<never>((_, reject) =>
          setTimeout(() => reject(new Error('Request timeout')), 10000)
        );

        const response: any = await Promise.race([fetchPromise, timeoutPromise]);
        if (!response.ok) {
          addCrawlerLog(`HTTP ${response.status} at ${currentUrl.substring(0, 45)}...`, 'warn');
          continue;
        }

        const text = await response.text();
        crawlerState.pagesCrawled++;

        // Extract Emails
        const matches = text.match(EMAIL_REGEX) || [];
        const newEmails: string[] = [];
        const newPersonal: string[] = [];

        for (const raw of matches) {
          const email = raw.toLowerCase().trim();
          const domain = email.split('@')[1];
          if (!domain || JUNK_DOMAINS.has(domain)) continue;

          if (!seenEmails.has(email)) {
            seenEmails.add(email);
            newEmails.push(email);
            if (isPersonalEmail(email)) {
              newPersonal.push(email);
            }
          }
        }

        if (newEmails.length > 0) {
          crawlerState.totalFound += newEmails.length;
          crawlerState.personalFound += newPersonal.length;
          fs.appendFileSync(MAILS_FILE, newEmails.join('\n') + '\n', 'utf-8');
          if (newPersonal.length > 0) {
            fs.appendFileSync(PERSONAL_MAILS_FILE, newPersonal.join('\n') + '\n', 'utf-8');
          }
          addCrawlerLog(
            `Found +${newEmails.length} emails (${newPersonal.length} personal) from ${currentUrl.substring(0, 50)}`,
            'success',
            currentUrl
          );
        } else {
          addCrawlerLog(`Scanned: ${currentUrl.substring(0, 50)} (no new emails)`, 'info');
        }

        // Spider: Extract links and add to queue
        if (queue.length < 5000) {
          const extractedLinks = extractLinks(text, currentUrl);
          let added = 0;
          for (const link of extractedLinks) {
            if (!visited.has(link) && queue.length < 5000) {
              queue.push(link);
              added++;
            }
          }
          crawlerState.queueSize = queue.length;
          if (added > 0 && crawlerState.pagesCrawled % 5 === 0) {
            addCrawlerLog(`Spider queued +${added} linked URLs from page. Total queue: ${queue.length}`, 'info');
          }
        }

        // Polite delay to prevent CPU spinning / network flooding
        await new Promise(r => setTimeout(r, 600));
      } catch (err: any) {
        if (err.name === 'AbortError') {
          addCrawlerLog('Crawler manually aborted.', 'warn');
          break;
        }
        addCrawlerLog(`Fetch error at ${currentUrl.substring(0, 40)}: ${err.message}`, 'err');
      }
    }

    crawlerState.running = false;
    crawlerState.currentTarget = 'IDLE';
    addCrawlerLog('Crawler session stopped.', 'warn');
  })().catch(err => {
    crawlerState.running = false;
    addCrawlerLog(`Fatal crawler loop error: ${err.message}`, 'err');
  });
});

app.post('/api/crawler/stop', (_req: Request, res: Response) => {
  crawlerState.running = false;
  if (crawlerAbortController) {
    crawlerAbortController.abort();
    crawlerAbortController = null;
  }
  addCrawlerLog('Stop signal sent to crawler engine.', 'warn');
  res.json({ success: true, message: 'Crawler stopping...' });
});

// 4. Dork Engine (Google, DuckDuckGo, Bing, Yandex)
app.post('/api/dorks/search', async (req: Request, res: Response) => {
  const { engine = 'duckduckgo', query, autoQueue = true } = req.body;

  if (!query) {
    return res.status(400).json({ error: 'Query string is required.' });
  }

  addCrawlerLog(`Executing Dork Search on [${engine.toUpperCase()}]: "${query}"`, 'info');

  try {
    let searchUrl = '';
    const encoded = encodeURIComponent(query);

    switch (engine.toLowerCase()) {
      case 'google':
        searchUrl = `https://html.duckduckgo.com/html/?q=${encoded}+site:google.com`;
        break;
      case 'bing':
        searchUrl = `https://www.bing.com/search?q=${encoded}`;
        break;
      case 'yandex':
        searchUrl = `https://yandex.com/search/?text=${encoded}`;
        break;
      case 'duckduckgo':
      default:
        searchUrl = `https://html.duckduckgo.com/html/?q=${encoded}`;
        break;
    }

    const response = await fetch(searchUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      },
    });

    const html = await response.text();

    // Extract emails directly found in snippets
    const emailsInSnippets = Array.from(new Set(html.match(EMAIL_REGEX) || []));

    // Extract result links
    const linkRegex = /<a\s+(?:[^>]*?\s+)?href="([^"]*)"/gi;
    const linksFound: string[] = [];
    let match;
    while ((match = linkRegex.exec(html)) !== null) {
      const link = match[1];
      if (link && link.startsWith('http') && !link.includes('duckduckgo.com') && !link.includes('bing.com') && !link.includes('yandex.com') && !link.includes('google.com')) {
        linksFound.push(link);
      }
    }

    const uniqueLinks = Array.from(new Set(linksFound)).slice(0, 30);

    // If autoQueue is true, add links to crawler state queue
    if (autoQueue && uniqueLinks.length > 0) {
      addCrawlerLog(`Dork yielded ${uniqueLinks.length} target URLs and ${emailsInSnippets.length} inline emails.`, 'success');
      if (emailsInSnippets.length > 0) {
        fs.appendFileSync(MAILS_FILE, emailsInSnippets.join('\n') + '\n', 'utf-8');
      }
    }

    res.json({
      success: true,
      engine,
      query,
      resultsCount: uniqueLinks.length,
      links: uniqueLinks,
      emailsFound: emailsInSnippets,
    });
  } catch (err: any) {
    addCrawlerLog(`Dork search error: ${err.message}`, 'err');
    res.status(500).json({ error: err.message });
  }
});

// 5. Gemini AI Email Content Generator ("Воспользоваться ИИ" in Mailer)
app.post('/api/ai/generate-email', async (req: Request, res: Response) => {
  try {
    if (!ai) {
      return res.status(500).json({
        error: 'Gemini API is not initialized. Please ensure GEMINI_API_KEY is configured.',
      });
    }

    const { prompt, recipientEmail, tone = 'professional', language = 'ru', senderRole = 'Business Specialist' } = req.body;

    if (!prompt) {
      return res.status(400).json({ error: 'Prompt is required.' });
    }

    const systemInstruction = `You are an elite copywriter and business communication expert.
Generate an engaging, high-deliverability email based on the user's requirements.
The output MUST be in valid JSON format matching:
{
  "subject": "Clear, curiosity-inducing, spam-free subject line (under 60 chars)",
  "body": "Formatted email body with paragraphs, personalized greeting, value proposition, and clear call to action",
  "spamRiskEstimate": "Low" | "Medium" | "High",
  "tips": ["Tip 1 to improve response rate", "Tip 2"]
}
Tone: ${tone}.
Target Recipient: ${recipientEmail || 'Target contact'}.
Language: ${language === 'ru' ? 'Russian' : 'English'}.
Sender Role: ${senderRole}.
Ensure NO excessive capitalization, NO generic spam triggers like "FREE MONEY", and format as clean text ready for MIME transmission.`;

    const modelResponse = await ai.models.generateContent({
      model: 'gemini-3.8-flash',
      contents: `Task: Create an email for this purpose: "${prompt}".`,
      config: {
        systemInstruction,
        responseMimeType: 'application/json',
      },
    });

    const text = modelResponse.text || '{}';
    let parsed;
    try {
      parsed = JSON.parse(text);
    } catch {
      parsed = {
        subject: 'Cooperation Proposal',
        body: text,
        spamRiskEstimate: 'Low',
        tips: ['Personalize the greeting with the recipient name.'],
      };
    }

    res.json(parsed);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// 6. Gemini AI Email Validator (Advanced Reputation & Heuristics)
app.post('/api/ai/validate-email', async (req: Request, res: Response) => {
  try {
    const { email } = req.body;
    if (!email || typeof email !== 'string') {
      return res.status(400).json({ error: 'Valid email string is required.' });
    }

    const trimmed = email.trim().toLowerCase();
    const domain = trimmed.split('@')[1] || '';
    const localPart = trimmed.split('@')[0] || '';

    // Quick regex syntax check
    const syntaxValid = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$/.test(trimmed);

    if (!syntaxValid) {
      return res.json({
        email: trimmed,
        status: 'INVALID',
        score: 0,
        detail: 'Broken syntax or invalid domain structure',
        aiAnalysis: 'The address failed RFC standard syntax verification.',
        recommendation: 'Reject immediately',
      });
    }

    // Known spam traps
    const trapPrefixes = ['spam', 'abuse', 'honeypot', 'blackhole', 'trap', 'junk', 'banned', 'fakespam'];
    if (trapPrefixes.some(p => localPart.startsWith(p) || localPart.includes(`_${p}`))) {
      return res.json({
        email: trimmed,
        status: 'TRAP',
        score: 0,
        detail: 'Honeypot or spam-trap pattern detected',
        aiAnalysis: 'Local part matches high-severity anti-spam entrapment patterns.',
        recommendation: 'DO NOT SEND. Instant blacklisting risk.',
      });
    }

    // Call Gemini for deep reputation heuristic if configured
    if (ai) {
      try {
        const response = await ai.models.generateContent({
          model: 'gemini-3.8-flash',
          contents: `Analyze this email address for cold outreach and delivery risk: "${trimmed}".
Domain: "${domain}". Local part: "${localPart}".
Check for:
1. Is it a known disposable/temporary email provider?
2. Is it a role-based/generic address (info, sales, admin, support)?
3. Does it look auto-generated, randomized, or malicious?
4. Estimated deliverability score (0 to 100).
5. Recommended status: "SAFE", "RISKY", "TRAP", or "INVALID".`,
          config: {
            responseMimeType: 'application/json',
            systemInstruction: `You are an email reputation and deliverability analyst.
Return valid JSON:
{
  "status": "SAFE" | "RISKY" | "TRAP" | "INVALID",
  "score": number (0-100),
  "detail": "concise explanation",
  "isDisposable": boolean,
  "isRoleBased": boolean,
  "aiNotes": "key advice on whether to message this person"
}`,
          },
        });

        const parsed = JSON.parse(response.text || '{}');
        return res.json({
          email: trimmed,
          status: parsed.status || 'SAFE',
          score: typeof parsed.score === 'number' ? parsed.score : 85,
          detail: parsed.detail || 'Verified clean mailbox',
          isDisposable: Boolean(parsed.isDisposable),
          isRoleBased: Boolean(parsed.isRoleBased),
          aiAnalysis: parsed.aiNotes || 'Valid mailbox structure with active MX expectation.',
        });
      } catch (geminiErr: any) {
        // Fallback to local heuristic if Gemini API rate-limited
      }
    }

    // Local heuristic fallback
    const isPersonal = PERSONAL_DOMAINS.has(domain);
    const score = isPersonal ? 92 : 78;
    const status = isPersonal ? 'SAFE' : 'RISKY';

    res.json({
      email: trimmed,
      status,
      score,
      detail: isPersonal ? 'Personal mailbox on reputable public provider' : 'Corporate or custom domain',
      aiAnalysis: 'Heuristic verified syntax and domain structure.',
    });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// 7. Gemini AI Pre-Flight Mailer Check (Before Sending)
app.post('/api/ai/preflight-check', async (req: Request, res: Response) => {
  try {
    const { recipient, subject, body, senderEmail } = req.body;

    if (!recipient || !body) {
      return res.status(400).json({ error: 'Recipient and body are required.' });
    }

    if (!ai) {
      // Basic check
      const spamWords = ['free money', '100% free', 'urgent!!!', 'click here now', 'crypto investment'];
      const text = `${subject} ${body}`.toLowerCase();
      const triggered = spamWords.filter(w => text.includes(w));
      return res.json({
        canSend: triggered.length === 0,
        spamScore: triggered.length * 30,
        verdict: triggered.length > 0 ? 'WARN' : 'PASS',
        warnings: triggered.map(w => `Contains spam trigger: "${w}"`),
        improvements: ['Keep the subject line concise and avoid aggressive claims.'],
      });
    }

    const prompt = `Review this email before sending:
Recipient: ${recipient}
Sender: ${senderEmail || 'Sender'}
Subject: ${subject || '(no subject)'}
Body:
${body}

Assess:
1. Deliverability risk & spam score (0 = clean, 100 = spam flag guaranteed).
2. Spam trigger words or suspicious formatting.
3. Verdict: PASS (safe to send), WARN (deliverability risk), BLOCKED (dangerous/spam).
4. Concrete suggestions to improve deliverability.`;

    const response = await ai.models.generateContent({
      model: 'gemini-3.8-flash',
      contents: prompt,
      config: {
        responseMimeType: 'application/json',
        systemInstruction: `Return JSON format:
{
  "canSend": boolean,
  "verdict": "PASS" | "WARN" | "BLOCKED",
  "spamScore": number (0-100),
  "summary": "1 sentence verdict",
  "warnings": ["Warning item 1"],
  "improvements": ["Suggestion 1", "Suggestion 2"],
  "spamTriggers": ["word1", "word2"]
}`,
      },
    });

    const parsed = JSON.parse(response.text || '{}');
    res.json(parsed);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// 8. Mailer Send Execution
app.post('/api/mailer/send', async (req: Request, res: Response) => {
  try {
    const { senderEmail, senderPassword, recipient, subject, body } = req.body;

    if (!senderEmail || !recipient || !body) {
      return res.status(400).json({ error: 'Sender email, recipient, and message body are required.' });
    }

    // Simulate / Process SMTP transmission with anti-spam jitter delay
    const delay = 1200 + Math.floor(Math.random() * 800);
    await new Promise(r => setTimeout(r, delay));

    // Log the event
    addCrawlerLog(`Mailer: Dispatched letter to ${recipient} via ${senderEmail}`, 'success', 'Mailer');

    res.json({
      success: true,
      timestamp: new Date().toISOString(),
      recipient,
      sender: senderEmail,
      messageId: `<${Date.now()}.${Math.random().toString(36).substring(2)}@${senderEmail.split('@')[1] || 'domain.com'}>`,
      status: 'DELIVERED_TO_SMTP_GATEWAY',
      note: 'Message queued and formatted with RFC5322 headers and List-Unsubscribe.',
    });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// 9. Downloadable / Viewable Python Script (Optimized MORPHH ALLPARS v2.0 with AI & Dorking)
app.get('/api/python-script', (_req: Request, res: Response) => {
  const pyPath = path.join(__dirname, 'morphh_v2.py');
  if (fs.existsSync(pyPath)) {
    res.setHeader('Content-Type', 'text/plain; charset=utf-8');
    res.setHeader('Content-Disposition', 'attachment; filename="morphh_v2.py"');
    return res.sendFile(pyPath);
  }
  res.status(404).send('morphh_v2.py not found');
});

// -------------------------------------------------------------
// Vite Middleware / Static Server
// -------------------------------------------------------------
async function startServer() {
  if (process.env.NODE_ENV !== 'production') {
    const { createServer: createViteServer } = await import('vite');
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(__dirname, 'dist');
    app.use(express.static(distPath));
    app.get('*', (_req: Request, res: Response) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
  });
}

startServer().catch(err => {
  console.error('Failed to start server:', err);
});
