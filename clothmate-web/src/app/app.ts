import { Component } from '@angular/core';
import { MeasureComponent } from './measure.component';

@Component({
  selector: 'app-root',
  imports: [MeasureComponent],
  template: `
    <app-measure></app-measure>
  `,
  styles: [`
    :host {
      display: block;
      padding: 24px;
      background-color: #fcfcfc;
      min-height: 100vh;
    }
  `],
})
export class App {}
