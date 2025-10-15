import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // Cette fonction s'exécute côté serveur
  // Pour une vraie protection, vous devriez vérifier un token dans les cookies
  
  const publicPaths = ['/login'];
  const isPublicPath = publicPaths.some(path => request.nextUrl.pathname.startsWith(path));
  
  // Pour l'instant, on laisse passer toutes les requêtes
  // La vraie protection se fait côté client avec le AuthProvider
  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
