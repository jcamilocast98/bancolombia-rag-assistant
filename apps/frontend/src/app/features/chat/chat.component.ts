import { Component, inject, OnInit, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiClientService } from '../../core/services/api-client.service';
import { LoadingService } from '../../core/services/loading.service';
import { MessageBubbleComponent } from './components/message-bubble/message-bubble.component';
import { ChatInputComponent } from './components/chat-input/chat-input.component';
import { TypingIndicatorComponent } from './components/typing-indicator/typing-indicator.component';
import { Message } from '../../domain/models/chat.models';
import { AutoScrollDirective } from '../../shared/directives/auto-scroll.directive';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [
    CommonModule,
    MessageBubbleComponent,
    ChatInputComponent,
    TypingIndicatorComponent,
    AutoScrollDirective
  ],
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss']
})
export class ChatComponent implements OnInit {
  private chatService = inject(ApiClientService);
  loadingService = inject(LoadingService);
  
  messages: Message[] = [];
  sessionId: string = this.generateUUID(); // Generar ID único para la sesión que funcione en HTTP
  isLoading: boolean = false;
  
  private generateUUID(): string {
    // crypto.randomUUID solo está disponible en contextos seguros (HTTPS o localhost)
    if (typeof crypto !== 'undefined' && (crypto as any).randomUUID) {
      return (crypto as any).randomUUID();
    }
    // Fallback para contextos no seguros (HTTP)
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0;
      const v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }
  
  ngOnInit() {
    // Suscribirse al historial local (ya incluye el mensaje de bienvenida)
    this.chatService.getHistory().subscribe((history: Message[]) => {
      this.messages = history;
    });
  }

  handleNewMessage(content: string) {
    if (!content.trim() || this.isLoading) return;

    this.isLoading = true;
    this.chatService.sendMessage({
      session_id: this.sessionId,
      message: content
    }).subscribe({
      next: () => {
        this.isLoading = false;
      },
      error: (err: any) => {
        this.isLoading = false;
      }
    });
  }
}
