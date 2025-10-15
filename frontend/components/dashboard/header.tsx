'use client'

import { Activity, Zap, Target, Menu, X, LogOut, User } from 'lucide-react'
import { usePathname, useRouter } from 'next/navigation'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import Image from 'next/image'
import { useState } from 'react'
import { useAuth } from '@/lib/auth-context'

export function Header() {
  const pathname = usePathname()
  const router = useRouter()
  const { user, signOut } = useAuth()
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  const handleSignOut = async () => {
    try {
      await signOut()
      router.push('/login')
    } catch (error) {
      console.error('Erreur de déconnexion:', error)
    }
  }

  const navItems = [
    { href: '/', label: 'Home', icon: Activity },
    { href: '/strategies', label: 'Stratégies Ninja', icon: Target },
    { href: '/backtesting', label: 'Backtesting Live', icon: Zap, badge: 'Beta' },
    //{ href: '/ia-analyst', label: 'IA Analyst', icon: Sparkles },
  ]

  return (
    <header className="sticky top-0 z-50 px-4 py-4">
      <div className="max-w-7xl mx-auto bg-black/40 backdrop-blur-xl border border-violet-400/30 rounded-2xl shadow-lg shadow-violet-500/10 px-6 h-16 flex items-center justify-between">
        {/* Logo & Brand */}
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center group">
            <img 
              src="/logo.png" 
              alt="NQ Backtest" 
              className="h-10 w-auto transition-all duration-300 group-hover:scale-105"
            />
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              const isIAAnalyst = item.href === '/ia-analyst'
              const hasBadge = 'badge' in item
              
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`relative flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isIAAnalyst
                      ? isActive
                        ? 'bg-gradient-to-r from-violet-500/30 to-purple-500/30 text-white border border-violet-400/60 shadow-lg shadow-violet-500/40'
                        : 'bg-gradient-to-r from-violet-500/10 to-purple-500/10 text-violet-300 border border-violet-400/30 hover:border-violet-400/60 hover:shadow-lg hover:shadow-violet-500/30 hover:from-violet-500/20 hover:to-purple-500/20'
                      : isActive
                      ? 'bg-violet-500/20 text-violet-400 border border-violet-500/50 shadow-lg shadow-violet-500/20'
                      : 'text-gray-400 hover:text-white hover:bg-white/5 border border-transparent'
                  }`}
                >
                  {isIAAnalyst && (
                    <>
                      <div className="absolute -top-1 -right-1 w-2 h-2 bg-violet-400 rounded-full animate-pulse shadow-lg shadow-violet-400/50"></div>
                      <Icon className="w-4 h-4 animate-pulse" />
                    </>
                  )}
                  {!isIAAnalyst && <Icon className="w-4 h-4" />}
                  <span className={isIAAnalyst ? 'font-bold' : ''}>{item.label}</span>
                  {isIAAnalyst && (
                    <span className="ml-1 px-1.5 py-0.5 bg-violet-400/20 text-violet-300 text-[10px] font-bold rounded uppercase tracking-wider">
                      New
                    </span>
                  )}
                  {hasBadge && !isIAAnalyst && (
                    <span className="ml-1 px-1.5 py-0.5 bg-orange-400/20 text-orange-300 text-[10px] font-bold rounded uppercase tracking-wider">
                      {item.badge}
                    </span>
                  )}
                </Link>
              )
            })}
          </nav>
        </div>

        {/* Right Side */}
        <div className="flex items-center gap-3">
          {/* User Info */}
          {user && (
            <Link
              href="/profile"
              className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-violet-500/10 hover:bg-violet-500/20 border border-violet-400/30 hover:border-violet-400/50 rounded-full backdrop-blur-sm transition-all cursor-pointer"
              title="Voir mon profil"
            >
              <User className="w-3 h-3 text-violet-400" />
              <span className="text-xs font-medium text-violet-300">{user.email}</span>
            </Link>
          )}

          {/* Status Indicator */}
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-[#00ff88]/10 border border-[#00ff88]/30 rounded-full backdrop-blur-sm">
            <div className="w-2 h-2 bg-[#00ff88] rounded-full animate-pulse shadow-lg shadow-[#00ff88]/50"></div>
            <span className="text-xs font-bold text-[#00ff88] tracking-wider">LIVE</span>
          </div>

          {/* Logout Button */}
          {user && (
            <button
              onClick={handleSignOut}
              className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-red-500/10 hover:bg-red-500/20 border border-red-400/30 hover:border-red-400/50 rounded-full backdrop-blur-sm transition-all text-red-400 hover:text-red-300"
              title="Déconnexion"
            >
              <LogOut className="w-4 h-4" />
              <span className="text-xs font-medium">Déconnexion</span>
            </button>
          )}

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="md:hidden p-2 text-violet-400 hover:text-violet-300 hover:bg-violet-500/10 rounded-lg transition-all"
            aria-label="Toggle menu"
          >
            {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="md:hidden overflow-hidden"
          >
            <div className="max-w-7xl mx-auto mt-2 bg-black/40 backdrop-blur-xl border border-violet-400/30 rounded-2xl shadow-lg shadow-violet-500/10 p-4">
              <nav className="flex flex-col gap-2">
                {navItems.map((item) => {
                  const Icon = item.icon
                  const isActive = pathname === item.href
                  const isIAAnalyst = item.href === '/ia-analyst'
                  const hasBadge = 'badge' in item
                  
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={() => setIsMenuOpen(false)}
                      className={`relative flex items-center gap-3 px-4 py-3 rounded-lg text-base font-medium transition-all duration-200 ${
                        isIAAnalyst
                          ? isActive
                            ? 'bg-gradient-to-r from-violet-500/30 to-purple-500/30 text-white border border-violet-400/60 shadow-lg shadow-violet-500/40'
                            : 'bg-gradient-to-r from-violet-500/10 to-purple-500/10 text-violet-300 border border-violet-400/30 hover:border-violet-400/60 hover:shadow-lg hover:shadow-violet-500/30 hover:from-violet-500/20 hover:to-purple-500/20'
                          : isActive
                          ? 'bg-violet-500/20 text-violet-400 border border-violet-500/50 shadow-lg shadow-violet-500/20'
                          : 'text-gray-400 hover:text-white hover:bg-white/5 border border-transparent'
                      }`}
                    >
                      {isIAAnalyst && (
                        <>
                          <div className="absolute -top-1 -right-1 w-2 h-2 bg-violet-400 rounded-full animate-pulse shadow-lg shadow-violet-400/50"></div>
                          <Icon className="w-5 h-5 animate-pulse" />
                        </>
                      )}
                      {!isIAAnalyst && <Icon className="w-5 h-5" />}
                      <span className={isIAAnalyst ? 'font-bold' : ''}>{item.label}</span>
                      {isIAAnalyst && (
                        <span className="ml-auto px-2 py-1 bg-violet-400/20 text-violet-300 text-xs font-bold rounded uppercase tracking-wider">
                          New
                        </span>
                      )}
                      {hasBadge && !isIAAnalyst && (
                        <span className="ml-auto px-2 py-1 bg-orange-400/20 text-orange-300 text-xs font-bold rounded uppercase tracking-wider">
                          {item.badge}
                        </span>
                      )}
                    </Link>
                  )
                })}
              </nav>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  )
}
