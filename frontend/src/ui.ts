import { store } from './store';
import { formatMoney, getSelectedDuration, clearAllQuantities } from './utils';
import { createHypothesis, refreshPrices, fetchUserData, fetchAssets } from './api';

const balanceSpan = document.getElementById('balanceDisplay')!;
const totalSumSpan = document.getElementById('totalSum')!;
const remainingSpan = document.getElementById('remainingBalance')!;
const warningMsg = document.getElementById('warningMessage')!;
const applyBtn = document.getElementById('applyBtn')!;
const refreshBtn = document.getElementById('refreshBtn')!;
const marketCards = document.querySelectorAll('#market .asset-card');
const durationOptions = document.querySelectorAll('.duration-option');
const navItems = document.querySelectorAll('.nav-item');
const pages = document.querySelectorAll('.page');
const activePositionsDiv = document.getElementById('active-positions')!;
const completedPositionsDiv = document.getElementById('completed-positions')!;
const historyListDiv = document.getElementById('history-list')!;

export function updateBalanceUI() {
  balanceSpan.innerHTML = store.balance.toFixed(0) + ' <small>₽</small>';
}

export function updateMarketPrices() {
  marketCards.forEach(card => {
    const assetId = card.getAttribute('data-asset-id');
    const asset = store.assets.find(a => a.id === assetId);
    if (asset) {
      const priceElem = card.querySelector('.asset-price') as HTMLElement;
      priceElem.textContent = asset.price.toFixed(1).replace('.', ',') + ' ₽';
      card.setAttribute('data-price', asset.price.toString());

      const qtyInput = card.querySelector('.quantity-input') as HTMLInputElement;
      const qty = parseInt(qtyInput.value, 10) || 0;
      const costSpan = card.querySelector('.position-cost') as HTMLElement;
      costSpan.textContent = formatMoney(qty * asset.price);
    }
  });
  updateTotalUI();
}

export function updateTotalUI() {
  let total = 0;
  marketCards.forEach(card => {
    const price = parseFloat(card.getAttribute('data-price') || '0');
    const qtyInput = card.querySelector('.quantity-input') as HTMLInputElement;
    const qty = parseInt(qtyInput.value, 10) || 0;
    total += price * qty;
  });
  totalSumSpan.textContent = formatMoney(total);
  const remaining = store.balance - total;
  remainingSpan.textContent = formatMoney(remaining);

  if (remaining < 0) {
    warningMsg.textContent = '⚠️ Недостаточно средств';
    applyBtn.classList.add('disabled');
  } else {
    warningMsg.textContent = '';
    applyBtn.classList.remove('disabled');
  }
}

export function renderPortfolio() {
  if (store.activePositions.length === 0) {
    activePositionsDiv.innerHTML = '<div class="position-item" style="justify-content:center; color:#647b9b;">Нет активных гипотез</div>';
  } else {
    let html = '';
    const now = Date.now();
    store.activePositions.forEach(pos => {
      const asset = store.assets.find(a => a.id === pos.assetId);
      const currentPrice = asset ? asset.price : pos.openPrice;
      const currentResult = (pos.direction === 'up' ? currentPrice - pos.openPrice : pos.openPrice - currentPrice) * pos.quantity;
      const resultClass = currentResult >= 0 ? 'positive' : 'negative';
      const totalDuration = pos.endTime - pos.openTime;
      const elapsed = now - pos.openTime;
      const progress = Math.min((elapsed / totalDuration) * 100, 100);
      const remainingDays = Math.max(0, Math.ceil((pos.endTime - now) / (1000 * 60 * 60 * 24)));
      const borderColor = pos.direction === 'up' ? '#1f2b3f' : '#b85a3a';

      html += `
        <div class="position-item" style="border-left-color: ${borderColor};">
          <div class="position-header">
            <span class="position-name">${pos.assetName} · ${pos.direction === 'up' ? 'Вверх' : 'Вниз'}</span>
            <span class="position-badge badge-active">Осталось ${remainingDays} дн.</span>
          </div>
          <div class="position-details">
            <span>${pos.quantity} шт. × ${pos.openPrice.toFixed(1).replace('.',',')} ₽</span>
            <span>Прогноз: ${pos.direction === 'up' ? 'вверх' : 'вниз'}</span>
          </div>
          <div class="progress-bar"><div class="progress-fill" style="width: ${progress}%;"></div></div>
          <div class="position-footer">
            <span>Текущий результат:</span>
            <span class="result ${resultClass}">${formatMoney(currentResult)}</span>
          </div>
        </div>
      `;
    });
    activePositionsDiv.innerHTML = html;
  }

  if (store.completedPositions.length === 0) {
    completedPositionsDiv.innerHTML = '<div class="position-item" style="justify-content:center; color:#647b9b;">Нет завершённых гипотез</div>';
  } else {
    let html = '';
    store.completedPositions.slice().reverse().forEach(pos => {
      const resultClass = pos.result >= 0 ? 'positive' : 'negative';
      const borderColor = pos.result >= 0 ? '#1e824c' : '#c43c2f';
      const badgeClass = pos.status === 'confirmed' ? 'badge-confirmed' : 'badge-rejected';
      const badgeText = pos.status === 'confirmed' ? 'Подтвердилась' : 'Опроверглась';

      html += `
        <div class="position-item" style="border-left-color: ${borderColor};">
          <div class="position-header">
            <span class="position-name">${pos.assetName} · ${pos.direction === 'up' ? 'Вверх' : 'Вниз'}</span>
            <span class="position-badge ${badgeClass}">${badgeText}</span>
          </div>
          <div class="position-details">
            <span>${pos.quantity} шт. × ${pos.openPrice.toFixed(1).replace('.',',')} ₽</span>
            <span>Прогноз: ${pos.direction === 'up' ? 'вверх' : 'вниз'}</span>
          </div>
          <div class="position-footer">
            <span>Итог:</span>
            <span class="result ${resultClass}">${formatMoney(pos.result)}</span>
          </div>
        </div>
      `;
    });
    completedPositionsDiv.innerHTML = html;
  }
}

export function renderHistory() {
  if (store.completedPositions.length === 0) {
    historyListDiv.innerHTML = '<div class="history-item" style="justify-content:center; color:#647b9b;">История пуста</div>';
    return;
  }

  let html = '';
  store.completedPositions.slice().reverse().forEach(pos => {
    const resultClass = pos.result >= 0 ? 'positive' : 'negative';
    const statusClass = pos.status === 'confirmed' ? 'status-confirmed' : 'status-rejected';
    const statusText = pos.status === 'confirmed' ? 'Подтвердилась' : 'Опроверглась';
    const date = new Date(pos.closeTime).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' });

    html += `
      <div class="history-item">
        <div class="history-info">
          <span class="history-asset">${pos.assetName} · ${pos.direction === 'up' ? 'Вверх' : 'Вниз'}</span>
          <div class="history-meta">
            <span>${date}</span>
            <span class="history-status ${statusClass}">${statusText}</span>
          </div>
        </div>
        <div class="history-amount ${resultClass}">${formatMoney(pos.result)}</div>
      </div>
    `;
  });
  historyListDiv.innerHTML = html;
}

export async function applyHypothesis() {
  const positionsToSend: { assetId: string; direction: 'up' | 'down'; quantity: number; duration: number }[] = [];
  let total = 0;

  marketCards.forEach(card => {
    const assetId = card.getAttribute('data-asset-id')!;
    const qtyInput = card.querySelector('.quantity-input') as HTMLInputElement;
    const qty = parseInt(qtyInput.value, 10) || 0;
    if (qty <= 0) return;

    const price = parseFloat(card.getAttribute('data-price') || '0');
    total += price * qty;

    const direction = card.querySelector('.up.active') ? 'up' : 'down';
    const duration = getSelectedDuration();

    positionsToSend.push({
      assetId,
      direction,
      quantity: qty,
      duration,
    });
  });

  if (positionsToSend.length === 0) {
    alert('Выберите хотя бы один актив и укажите количество');
    return;
  }

  if (total > store.balance) {
    alert('Недостаточно средств для открытия гипотез');
    return;
  }

  if (!confirm(`Вы уверены, что хотите применить гипотезу на сумму ${formatMoney(total)}?`)) {
    return;
  }

  try {
    const result = await createHypothesis(positionsToSend);
    await refreshAllData();
    clearAllQuantities();
    updateTotalUI(); 
  } catch (err) {
    alert('Ошибка при создании гипотезы');
    console.error(err);
  }
}

export async function refreshPricesAndData() {
  refreshBtn.classList.add('refreshing');
  try {
    const assets = await refreshPrices();
    store.setAssets(assets);
    await refreshAllData();
  } catch (err) {
    console.error('Ошибка при обновлении цен', err);
  } finally {
    refreshBtn.classList.remove('refreshing');
  }
}

export async function refreshAllData() {
  try {
    const [assets, userData] = await Promise.all([
      fetchAssets(),
      fetchUserData(),
    ]);
    store.setAssets(assets);
    store.setBalance(userData.balance);
    store.setActivePositions(userData.active);
    store.setCompletedPositions(userData.completed);
  } catch (err) {
    console.error('Не удалось загрузить данные', err);
  }
}