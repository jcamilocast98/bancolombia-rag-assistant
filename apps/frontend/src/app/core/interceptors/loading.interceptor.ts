import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { finalize } from 'rxjs/operators';
import { LoadingService } from '../services/loading.service';

export const loadingInterceptor: HttpInterceptorFn = (req, next) => {
  const loadingService = inject(LoadingService);
  
  // Omitimos ciertas peticiones si tuviéramos un header 'X-Skip-Loading'
  if (req.headers.has('X-Skip-Loading')) {
    const newReq = req.clone({ headers: req.headers.delete('X-Skip-Loading') });
    return next(newReq);
  }

  loadingService.show();
  return next(req).pipe(
    finalize(() => loadingService.hide())
  );
};
