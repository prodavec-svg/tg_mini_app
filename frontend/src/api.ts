import { Asset, Position, CompletedPosition } from './types';
// import WebApp from '@twa-dev/sdk';

// const API_BASE = process.env.VITE_API_URL ?? 'http://localhost:8000/api'; 
const API_BASE = 'https://tg-mini-app-ggy5.onrender.com/api';

// Вспомогательная функция для добавления заголовка авторизации (Telegram)
function getHeaders(): HeadersInit {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  
  const userId = (window as any).Telegram?.WebApp?.initDataUnsafe?.user?.id;
  console.log('userId:', userId);

  if (userId) {
    headers['X-Telegram-User-Id'] = String(userId);
  }

  return headers;
}

export async function fetchAssets(): Promise<Asset[]> {
  const response = await fetch(`${API_BASE}/assets`, { headers: getHeaders() });
  if (!response.ok) throw new Error('Ошибка загрузки активов');
  return response.json();
}

export async function fetchUserData(): Promise<{ balance: number; active: Position[]; completed: CompletedPosition[] }> {
  const response = await fetch(`${API_BASE}/user`, { headers: getHeaders() });
  if (!response.ok) throw new Error('Ошибка загрузки данных пользователя');
  return response.json();
}

export async function createHypothesis(
  positions: { assetId: string; direction: 'up' | 'down'; quantity: number; duration: number }[]
): Promise<{ newBalance: number }> {
  const response = await fetch(`${API_BASE}/hypotheses`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ positions }),
  });
  if (!response.ok) throw new Error('Ошибка отправки гипотезы');
  return response.json();
}

export async function refreshPrices(): Promise<Asset[]> {
  const response = await fetch(`${API_BASE}/prices/refresh`, {
    method: 'POST',
    headers: getHeaders(),
  });
  if (!response.ok) throw new Error('Ошибка обновления цен');
  return response.json();
}
