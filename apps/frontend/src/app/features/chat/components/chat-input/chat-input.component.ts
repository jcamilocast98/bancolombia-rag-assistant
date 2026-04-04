import { Component, Input, Output, EventEmitter } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-chat-input',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="input-container">
      <textarea 
        [(ngModel)]="message" 
        (keydown.enter)="onEnter($event)"
        placeholder="Escribe un mensaje a tu asistente Bancolombia..."
        [disabled]="disabled"
        rows="1">
      </textarea>
      <button 
        class="send-btn" 
        [class.active]="message.trim().length > 0"
        (click)="send()" 
        [disabled]="disabled || message.trim() === ''">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="22" y1="2" x2="11" y2="13"></line>
          <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
        </svg>
      </button>
    </div>
  `,
  styles: [`
    .input-container {
      display: flex;
      align-items: flex-end;
      gap: 12px;
      background: #ffffff;
      border: 1px solid #e0e0e0;
      border-radius: 24px;
      padding: 8px 16px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    textarea {
      flex: 1;
      border: none;
      resize: none;
      outline: none;
      font-family: inherit;
      font-size: 15px;
      padding: 8px 0;
      max-height: 120px;
      min-height: 24px;
      background: transparent;
      color: #002855; /* Bancolombia Blue */
    }
    .send-btn {
      background: #f5f5f5;
      color: #999;
      border: none;
      border-radius: 50%;
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: not-allowed;
      transition: all 0.2s;
      padding: 8px;
    }
    .send-btn.active {
      background: #FDDA24; /* Bancolombia Yellow */
      color: #002855; /* Bancolombia Blue */
      cursor: pointer;
    }
    .send-btn.active:hover {
      transform: scale(1.05);
    }
    .send-btn svg {
      width: 20px;
      height: 20px;
    }
  `]
})
export class ChatInputComponent {
  @Input() disabled = false;
  @Output() onSubmit = new EventEmitter<string>();
  
  message: string = '';

  onEnter(event: Event) {
    event.preventDefault();
    this.send();
  }

  send() {
    const text = this.message.trim();
    if (text && !this.disabled) {
      this.onSubmit.emit(text);
      this.message = '';
    }
  }
}
