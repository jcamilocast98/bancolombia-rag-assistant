import { Component } from '@angular/core';

@Component({
  selector: 'app-typing-indicator',
  standalone: true,
  template: `
    <div class="typing-indicator">
      <span></span>
      <span></span>
      <span></span>
    </div>
  `,
  styles: [`
    .typing-indicator {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 12px 16px;
      background-color: #f0f0f0;
      border-radius: 12px;
      margin-bottom: 12px;
      width: fit-content;
    }
    
    .typing-indicator span {
      display: block;
      width: 6px;
      height: 6px;
      background-color: #999;
      border-radius: 50%;
      animation: typing 1.4s infinite ease-in-out both;
    }
    
    .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
    .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes typing {
      0%, 80%, 100% { transform: scale(0); }
      40% { transform: scale(1); }
    }
  `]
})
export class TypingIndicatorComponent {}
