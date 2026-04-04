import { Directive, ElementRef, AfterViewChecked, Input } from '@angular/core';

@Directive({
  selector: '[appAutoScroll]',
  standalone: true
})
export class AutoScrollDirective implements AfterViewChecked {
  @Input() appAutoScroll: any; // Se evalúa si debe escrollear en los cambios
  
  private isNearBottom = true;

  constructor(private el: ElementRef) {}

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  private scrollToBottom(): void {
    try {
      const element = this.el.nativeElement;
      // Scrollear si el usuario no ha subido manualmente mucho
      if (this.isNearBottom) {
        element.scrollTop = element.scrollHeight;
      }
    } catch (err) { }
  }

  // Opcional: Escuchar eventos de scroll para permitirle al usuario 
  // leer arriba sin que baje automáticamente si entra otro mensaje.
}
