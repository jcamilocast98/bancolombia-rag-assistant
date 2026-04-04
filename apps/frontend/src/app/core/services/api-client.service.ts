import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, BehaviorSubject, tap } from 'rxjs';
import { ChatPort } from '../../domain/ports/chat.port';
import { ChatRequest, ChatResponse, Message, SourceCitation } from '../../domain/models/chat.models';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiClientService implements ChatPort {
  private http = inject(HttpClient);
  
  // Mantenemos el historial inicializado con el mensaje de bienvenida
  private historySubject = new BehaviorSubject<Message[]>([
    {
      role: 'assistant',
      content: '¡Hola! Soy tu Asistente Virtual Bancolombia. Estoy aquí para ayudarte a resolver tus dudas sobre cuentas, tarjetas, seguridad, créditos y mucho más. ¿En qué te puedo ayudar hoy?',
      timestamp: new Date().toISOString()
    }
  ]);

  sendMessage(request: ChatRequest): Observable<ChatResponse> {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      'X-API-Key': environment.apiKey
    });

    // Agregamos el mensaje del usuario al historial local
    this.addMessageToHistory({
      role: 'user',
      content: request.message,
      timestamp: new Date().toISOString()
    });

    return this.http.post<ChatResponse>(`${environment.apiUrl}/chat`, request, { headers }).pipe(
      tap((response: ChatResponse) => {
        // Mapear fuentes si vienen como strings hacia el modelo SourceCitation del frontend
        const mappedSources: SourceCitation[] = (response.sources || []).map((s: any) => {
          if (typeof s === 'string') {
            return { title: 'Ver fuente', url: s, snippet: '' };
          }
          return s;
        });

        this.addMessageToHistory({
          role: 'assistant',
          content: response.reply,
          timestamp: new Date().toISOString(),
          sources: mappedSources
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
