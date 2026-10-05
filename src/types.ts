export interface EmailAccount {
  email: string;
  password: string;
  provider: string;
}

export interface CrawlerLog {
  id: string;
  time: string;
  message: string;
  type: 'info' | 'success' | 'warn' | 'err';
  source?: string;
}

export interface CrawlerStatus {
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

export interface ValidationItem {
  email: string;
  status: 'SAFE' | 'RISKY' | 'TRAP' | 'INVALID';
  score: number;
  detail: string;
  isDisposable?: boolean;
  isRoleBased?: boolean;
  aiAnalysis?: string;
}

export interface PreflightResult {
  canSend: boolean;
  verdict: 'PASS' | 'WARN' | 'BLOCKED';
  spamScore: number;
  summary: string;
  warnings?: string[];
  improvements?: string[];
  spamTriggers?: string[];
}
