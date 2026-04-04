import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, BehaviorSubject, tap } from 'rxjs';
import { ChatPort } from '../../domain/ports/chat.port';
import { ChatRequest, ChatResponse, Message } from '../../domain/models/chat.models';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiClientService implements ChatPort {
  private http = inject(HttpClient);
  
  // Mantenemos el estado de la conversación local en un BehaviorSubject
  private historySubject = new BehaviorSubject<Message[]>([]);

  sendMessage(request: ChatRequest): Observable<ChatResponse> {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      'X-API-Key': environment.apiKey // Cabecera requerida por el Agente
    });

    // Agregamos el mensaje del usuario al historial local
    this.addMessageToHistory({
      role: 'user',
      content: request.message,
      timestamp: new Date().toISOString()
    });

    return this.http.post<ChatResponse>(`${environment.apiUrl}/chat`, request, { headers }).pipe(
      tap((response) => {
        // Al recibir la respuesta exitosa, agregamos al historial
        this.addMessageToHistory({
          role: 'assistant',
          content: response.reply,
          timestamp: new Date().toISOString(),
          sources: response.sources
        });
      })
    );
  }

  getHistory(): Observable<Message[]> {
    return this.historySubject.asObservable();
  }
  
  clearHistory(): void {
    this.historySubject.next([]);
  }

  private addMessageToHistory(msg: Message) {
    const current = this.historySubject.value;
    this.historySubject.next([...current, msg]);
  }
}
