import { Asset, Position, CompletedPosition } from './types';

const API_BASE = 'https://your-backend.com/api'; // Замени на реальный адрес

// Вспомогательная функция для добавления заголовка авторизации (Telegram)
function getHeaders(): HeadersInit {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
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