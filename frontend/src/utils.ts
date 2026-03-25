export function formatMoney(amount: number): string {
  return amount.toFixed(2).replace('.', ',') + ' ₽';
}

export function getSelectedDuration(): number {
  const activeDur = document.querySelector('.duration-option.active');
  return activeDur ? parseInt(activeDur.getAttribute('data-days') || '1', 10) : 1;
}

export function clearAllQuantities() {
  document.querySelectorAll('#market .asset-card').forEach(card => {
    const input = card.querySelector('.quantity-input') as HTMLInputElement;
    const slider = card.querySelector('.quantity-slider') as HTMLInputElement;
    const costSpan = card.querySelector('.position-cost') as HTMLElement;
    if (input && slider && costSpan) {
      input.value = '0';
      slider.value = '0';
      costSpan.textContent = formatMoney(0);
    }
  });
}