import { store } from './store';
import * as ui from './ui';
import { formatMoney, getSelectedDuration } from './utils';
import { refreshAllData } from './ui';
import WebApp from '@twa-dev/sdk'; 

WebApp.ready();

const marketCards = document.querySelectorAll('#market .asset-card');
const durationOptions = document.querySelectorAll('.duration-option');
const navItems = document.querySelectorAll('.nav-item');
const applyBtn = document.getElementById('applyBtn')!;
const refreshBtn = document.getElementById('refreshBtn')!;

function setupCardListeners() {
  marketCards.forEach(card => {
    const price = parseFloat(card.getAttribute('data-price') || '0');
    const input = card.querySelector('.quantity-input') as HTMLInputElement;
    const slider = card.querySelector('.quantity-slider') as HTMLInputElement;
    const costSpan = card.querySelector('.position-cost') as HTMLElement;
    const upBtn = card.querySelector('.up') as HTMLElement;
    const downBtn = card.querySelector('.down') as HTMLElement;

    upBtn.addEventListener('click', () => {
      upBtn.classList.add('active');
      downBtn.classList.remove('active');
    });
    downBtn.addEventListener('click', () => {
      downBtn.classList.add('active');
      upBtn.classList.remove('active');
    });

    const syncValue = (value: string) => {
      let qty = Math.min(1000, Math.max(0, parseInt(value, 10) || 0));
      input.value = qty.toString();
      slider.value = qty.toString();
      costSpan.textContent = formatMoney(qty * price);
      ui.updateTotalUI();
    };

    slider.addEventListener('input', (e) => syncValue((e.target as HTMLInputElement).value));
    input.addEventListener('input', (e) => syncValue((e.target as HTMLInputElement).value));
  });
}

function setupNavigation() {
  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const targetId = item.getAttribute('data-page')!;
      navItems.forEach(n => n.classList.remove('active'));
      item.classList.add('active');
      document.querySelectorAll('.page').forEach(p => p.classList.remove('active-page'));
      document.getElementById(targetId)!.classList.add('active-page');

      if (targetId === 'portfolio') ui.renderPortfolio();
      if (targetId === 'history') ui.renderHistory();
    });
  });
}

function subscribeToStore() {
  store.subscribe('balance', ui.updateBalanceUI);
  store.subscribe('assets', () => {
    ui.updateMarketPrices();
    ui.renderPortfolio();
  });
  store.subscribe('activePositions', ui.renderPortfolio);
  store.subscribe('completedPositions', () => {
    ui.renderPortfolio();
    ui.renderHistory();
  });
}

async function initApp() {
  await ui.refreshAllData();

  setupCardListeners();
  setupNavigation();
  subscribeToStore();

  applyBtn.addEventListener('click', ui.applyHypothesis);
  refreshBtn.addEventListener('click', ui.refreshPricesAndData);

  durationOptions.forEach(opt => {
    opt.addEventListener('click', () => {
      durationOptions.forEach(o => o.classList.remove('active'));
      opt.classList.add('active');
    });
  });

  ui.updateMarketPrices();
  ui.renderPortfolio();
  ui.renderHistory();
}

initApp().catch(console.error);