import { Observable } from 'rxjs';
import { ChatRequest, ChatResponse, Message } from '../models/chat.models';

/**
 * Puerto Hexagonal que define el contrato de comunicación 
 * para el servicio de Chat. Independiente de Angular HttpClient o LocalStorage.
 */
export interface ChatPort {
  /**
   * Envía un mensaje al agente y recibe la respuesta asincrónica.
   */
  sendMessage(request: ChatRequest): Observable<ChatResponse>;
  
  /**
   * Obtiene el historial local de la conversación actual.
   */
  getHistory(): Observable<Message[]>;
}
