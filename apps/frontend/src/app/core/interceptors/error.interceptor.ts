import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { catchError } from 'rxjs/operators';
import { throwError } from 'rxjs';
import { inject } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const snackBar = inject(MatSnackBar);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      let errorMsg = 'Ocurrió un error desconocido.';
      
      if (error.error instanceof ErrorEvent) {
        // Error de cliente
        errorMsg = `Error de red: ${error.error.message}`;
      } else {
        // Error de backend
        if (error.status === 401) {
          errorMsg = 'No autorizado. Verifica tu API Key.';
        } else if (error.status === 500) {
          errorMsg = 'El agente experimentó un problema interno.';
        } else if (error.status === 429) {
          errorMsg = 'Límite de mensajes alcanzado. Por favor, espera un momento antes de enviar otro mensaje.';
        } else if (error.status === 504 || error.status === 408 || error.status === 0) {
          errorMsg = 'El agente no responde. Por favor intenta de nuevo.';
        } else {
          errorMsg = `Error ${error.status}: ${error.message}`;
        }
      }

      // Mostrar toast
      snackBar.open(errorMsg, 'Cerrar', {
        duration: 5000,
        panelClass: ['error-snackbar'],
        horizontalPosition: 'center',
        verticalPosition: 'bottom'
      });

      return throwError(() => new Error(errorMsg));
    })
  );
};
