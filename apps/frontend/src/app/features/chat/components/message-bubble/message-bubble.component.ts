import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Message } from '../../../../domain/models/chat.models';
import { MarkdownPipe } from '../../../../shared/pipes/markdown.pipe';
import { SourceCardComponent } from '../source-card/source-card.component';

@Component({
  selector: 'app-message-bubble',
  standalone: true,
  imports: [CommonModule, MarkdownPipe, SourceCardComponent],
  template: `
    <div class="message-wrapper" [class.user]="isUser">
      
      <div class="avatar" *ngIf="!isUser">
        <img src="assets/bot-avatar.svg" alt="Bot" onerror="this.src='data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjZmZmZmZmIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBhdGggZD0iTTEyIDJhNCA0IDAgMCAwLTQgNGg4YTQgNCAwIDAgMC00LTR6Ii8+PHBhdGggZD0iTTggNmEyIDIgMCAwIDAtMiAydjhhMiAyIDAgMCAwIDIgMmgydjRoYTIgMiAwIDAgMCAyIDJ2LTRoMmEyIDIgMCAwIDAgMi0ydi04YTIgMiAwIDAgMC0yLTJoLTh6Ii8+PC9zdmc+'" />
      </div>

      <div class="message-content">
        <!-- Contenido textual parseado con Markdown -->
        <div class="bubble" [class.user-bubble]="isUser" [class.assistant-bubble]="!isUser">
          <div class="markdown-content" [innerHTML]="message.content | markdown"></div>
        </div>

        <!-- Tarjetas de fuentes (si existen) -->
        <div class="sources-container" *ngIf="!isUser && message.sources && message.sources.length > 0">
          <div class="sources-title">Fuentes de consulta:</div>
          <div class="sources-grid">
            <app-source-card *ngFor="let source of message.sources" [source]="source"></app-source-card>
          </div>
        </div>
      </div>
      
    </div>
  `,
  styles: [`
    .message-wrapper {
      display: flex;
      gap: 16px;
      margin-bottom: 24px;
      max-width: 100%;
    }
    
    .message-wrapper.user {
      flex-direction: row-reverse;
    }
    
    .avatar {
      flex-shrink: 0;
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: #002855; /* Bancolombia Blue */
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
    }
    
    .avatar img {
      width: 20px;
      height: 20px;
    }
    
    .message-content {
      display: flex;
      flex-direction: column;
      gap: 8px;
      max-width: 80%;
      min-width: 0;
    }
    
    .bubble {
      padding: 12px 18px;
      border-radius: 16px;
      font-size: 15px;
      line-height: 1.5;
      word-break: break-word;
    }
    
    .user-bubble {
      background: #002855; /* Bancolombia Blue */
      color: #ffffff;
      border-bottom-right-radius: 4px;
    }
    
    .assistant-bubble {
      background: #ffffff;
      color: #333333;
      border: 1px solid #e0e0e0;
      border-bottom-left-radius: 4px;
    }
    
    ::ng-deep .markdown-content p {
      margin-top: 0;
      margin-bottom: 12px;
    }
    ::ng-deep .markdown-content p:last-child {
      margin-bottom: 0;
    }
    ::ng-deep .markdown-content a {
      color: #002855;
      text-decoration: underline;
    }
    ::ng-deep .user-bubble .markdown-content a {
      color: #FDDA24;
    }
    ::ng-deep .markdown-content strong {
      font-weight: 600;
    }
    ::ng-deep .markdown-content ul, ::ng-deep .markdown-content ol {
      margin-top: 0;
      padding-left: 20px;
    }
    
    .sources-container {
      margin-top: 4px;
    }
    
    .sources-title {
      font-size: 12px;
      color: #6c757d;
      margin-bottom: 8px;
      font-weight: 500;
    }
    
    .sources-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
      gap: 12px;
    }
  `]
})
export class MessageBubbleComponent {
  @Input({ required: true }) message!: Message;
  
  get isUser(): boolean {
    return this.message.role === 'user';
  }
}
