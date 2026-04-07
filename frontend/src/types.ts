export interface Asset {
  id: string;        
  name: string;      
  ticker: string;    
  price: number;
}

export interface Position {
  id: number;
  assetId: string;
  assetName: string;
  direction: 'up' | 'down';
  quantity: number;
  openPrice: number;
  openTime: number;     
  duration: number;     
  endTime: number;
}

export interface CompletedPosition extends Position {
  closePrice: number;
  result: number;
  status: 'confirmed' | 'rejected';
  closeTime: number;
}

export interface UserData {
  balance: number;
  activePositions: Position[];
  completedPositions: CompletedPosition[];
}

export interface ApiResponse<T> {
  data: T;
  error?: string;
}