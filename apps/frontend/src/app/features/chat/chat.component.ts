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
  sessionId: string = crypto.randomUUID(); // Generar ID único para la sesión
  
  ngOnInit() {
    // Suscribirse al historial local
    this.chatService.getHistory().subscribe((history: Message[]) => {
      this.messages = history;
    });

    // Mensaje inicial del sistema si está vacío
    if (this.messages.length === 0) {
      this.messages = [
        {
          role: 'assistant',
          content: '¡Hola! Soy tu Asistente Virtual Bancolombia. Estoy aquí para ayudarte a resolver tus dudas sobre cuentas, tarjetas, seguridad, créditos y mucho más. ¿En qué te puedo ayudar hoy?',
          timestamp: new Date().toISOString()
        }
      ];
    }
  }

  handleNewMessage(content: string) {
    if (!content.trim()) return;

    // La interfaz se actualiza automáticamente por la suscripción a getHistory()
    // en cuanto el ApiClientService despacha la petición POST.

    this.chatService.sendMessage({
      session_id: this.sessionId,
      message: content
    }).subscribe({
      next: () => {
        // La respuesta ya se añadió al history y UI se actualizó
      },
      error: (err: any) => {
        // En caso de error, mostramos un mensaje de sistema temporal si lo deseamos
        // El ErrorInterceptor ya muestra un SnackBar.
      }
    });
  }
}
