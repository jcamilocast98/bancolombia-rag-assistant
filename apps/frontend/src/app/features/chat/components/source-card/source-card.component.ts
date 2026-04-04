import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-source-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <a [href]="source.url" target="_blank" rel="noopener noreferrer" class="source-card">
      <div class="source-icon">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
          <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
        </svg>
      </div>
      <div class="source-content">
        <h4 class="source-title">{{ source.title || extractDomain(source.url) }}</h4>
        <p class="source-url">{{ source.url }}</p>
      </div>
    </a>
  `,
  styles: [`
    .source-card {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 14px;
      background: #f8f9fa;
      border: 1px solid #e9ecef;
      border-radius: 8px;
      text-decoration: none;
      color: inherit;
      transition: all 0.2s ease;
      margin-bottom: 8px;
    }
    
    .source-card:hover {
      background: #eef2f5;
      border-color: #cdd4da;
      transform: translateY(-1px);
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    .source-icon {
      flex-shrink: 0;
      width: 32px;
      height: 32px;
      background: #e3ebf3;
      color: #002855; /* Bancolombia Blue */
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    .source-icon svg {
      width: 16px;
      height: 16px;
    }
    
    .source-content {
      overflow: hidden;
    }
    
    .source-title {
      margin: 0 0 2px 0;
      font-size: 13px;
      font-weight: 600;
      color: #343a40;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    
    .source-url {
      margin: 0;
      font-size: 11px;
      color: #6c757d;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  `]
})
export class SourceCardComponent {
  @Input({ required: true }) source!: any; // SourceCitation

  extractDomain(url: string): string {
    try {
      const { hostname } = new URL(url);
      return hostname;
    } catch {
      return url;
    }
  }
}
