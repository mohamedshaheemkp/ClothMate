import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Garment {
  id: string;
  gender: string | null;
  category: string | null;
}

@Injectable({ providedIn: 'root' })
export class GarmentService {
  private http = inject(HttpClient);

  list(): Observable<Garment[]> {
    return this.http.get<Garment[]>('/api/garments');
  }
}

