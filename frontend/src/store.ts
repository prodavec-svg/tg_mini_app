import { Asset, Position, CompletedPosition } from './types';

type Listener = () => void;

class AppStore {
  private _balance: number = 5000;
  private _assets: Asset[] = [];
  private _activePositions: Position[] = [];
  private _completedPositions: CompletedPosition[] = [];

  private listeners: { [key: string]: Listener[] } = {};


  get balance() { return this._balance; }
  get assets() { return this._assets; }
  get activePositions() { return this._activePositions; }
  get completedPositions() { return this._completedPositions; }


  setBalance(newBalance: number) {
    this._balance = newBalance;
    this.notify('balance');
  }

  setAssets(assets: Asset[]) {
    this._assets = assets;
    this.notify('assets');
    this.notify('activePositions'); 
  }

  setActivePositions(positions: Position[]) {
    this._activePositions = positions;
    this.notify('activePositions');
  }

  setCompletedPositions(positions: CompletedPosition[]) {
    this._completedPositions = positions;
    this.notify('completedPositions');
  }

  subscribe(key: string, callback: Listener) {
    if (!this.listeners[key]) this.listeners[key] = [];
    this.listeners[key].push(callback);
  }

  private notify(key: string) {
    this.listeners[key]?.forEach(fn => fn());
  }
}

export const store = new AppStore();