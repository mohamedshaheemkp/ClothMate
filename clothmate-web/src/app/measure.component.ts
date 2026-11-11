import { Component, ElementRef, ViewChild, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

interface GarmentInfo {
  id: string;
  gender?: string | null;
  category?: string | null;
  display_name?: string;
}

interface PointSpec {
  name: string;
  instruction: string;
  required?: boolean;
}

interface Step {
  key: string;
  label: string;
  required: boolean;
}

interface XY {
  x: number;
  y: number;
}

interface MeasurementRow {
  name: string;
  tailor_measure?: string;
  flat_cm: number;
  garment_circumference_cm?: number | null;
  ease_cm?: number | null;
  estimated_body_cm?: number | null;
}

interface MeasureResult {
  garment_id: string;
  fit: string;
  method?: string;
  session_id: string;
  measurements: MeasurementRow[];
  warnings?: string[];
  ease_status?: string;
}

const CARD_STEPS: Step[] = [
  { key: 'card:top_left', label: 'Reference corner 1 of 4: TOP-LEFT (card long edge is "top")', required: true },
  { key: 'card:top_right', label: 'Reference corner 2 of 4: TOP-RIGHT', required: true },
  { key: 'card:bottom_right', label: 'Reference corner 3 of 4: BOTTOM-RIGHT', required: true },
  { key: 'card:bottom_left', label: 'Reference corner 4 of 4: BOTTOM-LEFT', required: true },
];

@Component({
  selector: 'app-measure',
  standalone: true,
  imports: [FormsModule],
  template: `
    <div class="measure-container">
      <h2>ClothMate - Garment Measurement</h2>

      <div class="control-panel">
        <label>
          <b>Garment:</b>
          <select [ngModel]="garmentId()" (ngModelChange)="selectGarment($event)">
            <option value="">-- Choose a Garment --</option>
            @for (g of garments(); track g.id) {
              <option [value]="g.id">{{ g.display_name ?? g.id }} ({{ g.gender }}, {{ g.category }})</option>
            }
          </select>
        </label>

        <label>
          <b>Fit Preference:</b>
          <select [(ngModel)]="fit">
            <option value="slim">Slim</option>
            <option value="regular">Regular</option>
            <option value="loose">Loose</option>
          </select>
        </label>

        <label>
          <b>Photo (Kept 100% in your browser):</b>
          <input type="file" accept="image/jpeg,image/png,image/webp" (change)="onFile($event)" />
        </label>
      </div>

      @if (error()) {
        <p class="error-box">{{ error() }}</p>
      }

      @if (steps().length && hasImage()) {
        <div class="instruction-box">
          @if (currentStep(); as s) {
            <span class="step-indicator">Step {{ stepIndex() + 1 }} of {{ steps().length }}:</span>
            <span class="step-label">{{ s.label }}</span>
            @if (!s.required) {
              <button class="btn-skip" (click)="skip()">Skip</button>
            }
          } @else {
            <span class="step-indicator">All points placed!</span>
            <button class="btn-calculate" (click)="submit()" [disabled]="busy()">
              {{ busy() ? 'Calculating...' : 'Calculate Measurements' }}
            </button>
          }
          <button class="btn-undo" (click)="undo()" [disabled]="stepIndex() === 0">Undo Last Click</button>
        </div>
      }

      <div class="canvas-wrapper" [style.display]="hasImage() ? 'block' : 'none'">
        <canvas #canvas (click)="onCanvasClick($event)"></canvas>
      </div>

      @if (result(); as r) {
        <div class="results-card">
          <h3>Calculated Measurements</h3>
          <p class="session-badge">Saved Session ID: <code>{{ r.session_id }}</code></p>

          <table class="results-table">
            <thead>
              <tr>
                <th>Measurement</th>
                <th>Flat Garment (cm)</th>
                <th>Circumference (cm)</th>
                <th>Estimated Body (cm)</th>
              </tr>
            </thead>
            <tbody>
              @for (m of r.measurements; track m.name) {
                <tr>
                  <td>{{ m.tailor_measure ?? m.name }}</td>
                  <td>{{ m.flat_cm }} cm</td>
                  <td>{{ m.garment_circumference_cm != null ? m.garment_circumference_cm + ' cm' : '-' }}</td>
                  <td>{{ m.estimated_body_cm != null ? m.estimated_body_cm + ' cm' : '-' }}</td>
                </tr>
              }
            </tbody>
          </table>

          @if (r.warnings && r.warnings.length) {
            @for (w of r.warnings; track w) {
              <p class="warn-text">{{ w }}</p>
            }
          }
        </div>
      }
    </div>
  `,
  styles: [`
    .measure-container {
      max-width: 1000px;
      margin: 0 auto;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      color: #222;
    }
    h2 {
      margin-top: 0;
      color: #1a237e;
    }
    .control-panel {
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
      margin-bottom: 16px;
      padding: 12px;
      background: #f7f9fa;
      border: 1px solid #e0e0e0;
      border-radius: 6px;
    }
    label {
      display: flex;
      flex-direction: column;
      font-size: 13px;
      gap: 4px;
    }
    select, input[type="file"] {
      padding: 6px 8px;
      border: 1px solid #ccc;
      border-radius: 4px;
      font-size: 13px;
    }
    .instruction-box {
      margin: 12px 0;
      padding: 10px 14px;
      background: #e8f0fe;
      border-left: 4px solid #1976d2;
      border-radius: 4px;
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }
    .step-indicator {
      font-weight: bold;
      color: #1565c0;
    }
    .step-label {
      flex: 1;
      font-size: 14px;
    }
    button {
      padding: 6px 14px;
      font-size: 13px;
      font-weight: 500;
      border-radius: 4px;
      border: 1px solid transparent;
      cursor: pointer;
    }
    .btn-calculate {
      background: #2e7d32;
      color: white;
    }
    .btn-calculate:disabled {
      background: #a5d6a7;
      cursor: not-allowed;
    }
    .btn-undo {
      background: #ffffff;
      border: 1px solid #ccc;
      color: #333;
    }
    .btn-undo:disabled {
      color: #aaa;
      cursor: not-allowed;
    }
    .btn-skip {
      background: #fff8e1;
      border: 1px solid #ffe082;
      color: #8d6e63;
    }
    .canvas-wrapper {
      margin-top: 12px;
      border: 1px solid #ccc;
      border-radius: 6px;
      overflow: hidden;
      background: #fafafa;
    }
    canvas {
      width: 100%;
      display: block;
      cursor: crosshair;
    }
    .results-card {
      margin-top: 24px;
      padding: 16px;
      background: #ffffff;
      border: 1px solid #e0e0e0;
      border-radius: 6px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    .session-badge {
      font-size: 13px;
      color: #555;
    }
    .results-table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 10px;
    }
    .results-table th, .results-table td {
      border: 1px solid #e0e0e0;
      padding: 8px 12px;
      text-align: right;
    }
    .results-table th:first-child, .results-table td:first-child {
      text-align: left;
    }
    .results-table th {
      background: #f5f5f5;
      font-weight: 600;
    }
    .error-box {
      color: #d32f2f;
      background: #ffebee;
      padding: 8px 12px;
      border-radius: 4px;
      border: 1px solid #ffcdd2;
    }
    .warn-text {
      color: #f57c00;
      margin-top: 8px;
    }
  `],
})
export class MeasureComponent {
  private http = inject(HttpClient);
  @ViewChild('canvas', { static: false }) canvasRef!: ElementRef<HTMLCanvasElement>;

  garments = signal<GarmentInfo[]>([]);
  garmentId = signal('');
  steps = signal<Step[]>([]);
  clicks = signal<Record<string, XY>>({});
  stepIndex = signal(0);
  hasImage = signal(false);
  busy = signal(false);
  error = signal('');
  result = signal<MeasureResult | null>(null);

  fit = 'regular';
  private img: HTMLImageElement | null = null;

  constructor() {
    this.http.get<GarmentInfo[]>('/api/garments').subscribe({
      next: (list) => this.garments.set(list),
      error: () => this.error.set('Cannot reach backend. Make sure Spring Boot and Python FastAPI are running.'),
    });
  }

  currentStep(): Step | null {
    return this.steps()[this.stepIndex()] ?? null;
  }

  selectGarment(id: string) {
    this.garmentId.set(id);
    this.result.set(null);
    this.resetClicks();
    if (!id) {
      this.steps.set([]);
      return;
    }
    this.http.get<{ id: string; points: PointSpec[] }>(`/api/garments/${id}`).subscribe({
      next: (spec) => {
        const garmentSteps = spec.points.map((p) => ({
          key: p.name,
          label: p.instruction,
          required: p.required ?? true,
        }));
        this.steps.set([...CARD_STEPS, ...garmentSteps]);
        this.redraw();
      },
      error: () => this.error.set(`Could not load spec for garment: ${id}`),
    });
  }

  onFile(evt: Event) {
    const file = (evt.target as HTMLInputElement).files?.[0];
    if (!file) {
      return;
    }
    if (!/^image\/(jpeg|png|webp)$/.test(file.type) || file.size > 25_000_000) {
      this.error.set('Please choose a valid JPG, PNG, or WebP photo under 25 MB.');
      return;
    }
    this.error.set('');
    const img = new Image();
    img.onload = () => {
      this.img = img;
      this.hasImage.set(true);
      this.result.set(null);
      this.resetClicks();
      // Allow DOM to update before drawing
      setTimeout(() => this.redraw(), 50);
    };
    img.src = URL.createObjectURL(file);
  }

  onCanvasClick(evt: MouseEvent) {
    const step = this.currentStep();
    if (!step || !this.img || !this.canvasRef) {
      return;
    }
    const canvas = this.canvasRef.nativeElement;
    const rect = canvas.getBoundingClientRect();
    // Transform screen click back into original image pixel coordinates
    const scaleX = this.img.naturalWidth / rect.width;
    const scaleY = this.img.naturalHeight / rect.height;
    const x = Math.round((evt.clientX - rect.left) * scaleX);
    const y = Math.round((evt.clientY - rect.top) * scaleY);

    this.clicks.update((c) => ({ ...c, [step.key]: { x, y } }));
    this.stepIndex.update((i) => i + 1);
    this.redraw();
  }

  skip() {
    this.stepIndex.update((i) => i + 1);
  }

  undo() {
    const i = this.stepIndex() - 1;
    if (i < 0) {
      return;
    }
    this.stepIndex.set(i);
    const key = this.steps()[i]?.key;
    if (key) {
      this.clicks.update((c) => {
        const copy = { ...c };
        delete copy[key];
        return copy;
      });
    }
    this.redraw();
  }

  submit() {
    const c = this.clicks();
    const body = {
      garment_id: this.garmentId(),
      fit: this.fit,
      card: {
        top_left: c['card:top_left'],
        top_right: c['card:top_right'],
        bottom_right: c['card:bottom_right'],
        bottom_left: c['card:bottom_left'],
      },
      points: Object.fromEntries(
        Object.entries(c).filter(([k]) => !k.startsWith('card:'))
      ),
    };

    this.busy.set(true);
    this.error.set('');
    this.http.post<MeasureResult>('/api/measure', body).subscribe({
      next: (res) => {
        this.result.set(res);
        this.busy.set(false);
      },
      error: (err) => {
        this.busy.set(false);
        const detail = err?.error?.detail;
        this.error.set(typeof detail === 'string' ? detail : 'Measurement failed. Please check corner placements.');
      },
    });
  }

  private resetClicks() {
    this.clicks.set({});
    this.stepIndex.set(0);
  }

  private redraw() {
    if (!this.canvasRef || !this.img) {
      return;
    }
    const canvas = this.canvasRef.nativeElement;
    const ctx = canvas.getContext('2d');
    if (!ctx) {
      return;
    }

    canvas.width = this.img.naturalWidth;
    canvas.height = this.img.naturalHeight;
    ctx.drawImage(this.img, 0, 0);

    const r = Math.max(6, Math.round(canvas.width / 180));
    ctx.lineWidth = Math.max(2, Math.round(r / 3));
    ctx.font = `bold ${Math.round(r * 2.5)}px sans-serif`;

    for (const [key, p] of Object.entries(this.clicks())) {
      const isCard = key.startsWith('card:');
      ctx.strokeStyle = isCard ? '#e53935' : '#1e88e5';
      ctx.fillStyle = ctx.strokeStyle;

      ctx.beginPath();
      ctx.arc(p.x, p.y, r, 0, 2 * Math.PI);
      ctx.stroke();

      const label = key.replace('card:', '');
      ctx.fillText(label, p.x + r * 1.5, p.y - r);
    }
  }
}

