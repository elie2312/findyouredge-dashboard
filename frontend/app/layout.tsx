'use client'

import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'
import { ThemeProvider } from '@/components/theme-provider'
import { Footer } from '@/components/dashboard/footer'
import { AuthProvider } from '@/lib/auth-context'

const inter = Inter({ subsets: ['latin'] })

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fr" suppressHydrationWarning className="dark">
      <body className={`${inter.className} bg-[#0a0a0f] bg-gradient-to-br from-[#0a0a0f] via-[#0f1419] to-[#0a0a0f] flex flex-col min-h-screen`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem={false}
          disableTransitionOnChange
        >
          <AuthProvider>
            <Providers>
              {children}
            </Providers>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
