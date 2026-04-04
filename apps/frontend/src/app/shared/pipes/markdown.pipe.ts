import { Pipe, PipeTransform } from '@angular/core';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

@Pipe({
  name: 'markdown',
  standalone: true
})
export class MarkdownPipe implements PipeTransform {

  constructor(private sanitizer: DomSanitizer) {}

  transform(value: string | undefined | null): SafeHtml {
    if (!value) {
      return '';
    }

    // 1. Convertir Markdown a HTML
    const rawHtml = marked.parse(value) as string;

    // 2. Limpiar el HTML para prevenir ataques XSS
    const cleanHtml = DOMPurify.sanitize(rawHtml, {
      ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'ul', 'ol', 'li', 'br', 'code', 'pre', 'h1', 'h2', 'h3', 'h4', 'blockquote', 'table', 'thead', 'tbody', 'tr', 'th', 'td'],
      ALLOWED_ATTR: ['href', 'target', 'class']
    });

    // 3. Marcar el HTML como seguro para Angular (ya que lo limpiamos nosotros con DOMPurify)
    return this.sanitizer.bypassSecurityTrustHtml(cleanHtml);
  }
}
