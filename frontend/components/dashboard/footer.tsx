import Image from 'next/image'
import Link from 'next/link'
import { Linkedin, Mail } from 'lucide-react'

export function Footer() {
  return (
    <footer className="px-4 py-8 mt-16">
      <div className="max-w-7xl mx-auto bg-black/40 backdrop-blur-xl border border-violet-400/30 rounded-2xl shadow-lg shadow-violet-500/10 px-8 py-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Logo & Description */}
          <div className="md:col-span-2">
            <div className="flex items-center gap-3 mb-4">
              <Image 
                src="/logo_footer.png" 
                alt="Find Your Edge" 
                width={50}
                height={50}
                className="rounded-lg"
              />
              <div>
                <h3 className="text-xl font-bold text-white">Find Your Edge</h3>
                <p className="text-sm text-violet-400">Backtest Platform</p>
              </div>
            </div>
            <p className="text-sm text-gray-400 max-w-md">
              Plateforme de backtesting haute performance pour stratégies de trading. 
              Analysez, optimisez et perfectionnez vos stratégies avec nos outils avancés.
            </p>
          </div>
          
          {/* Quick Links */}
          <div>
            <h4 className="text-white font-semibold mb-4">Navigation</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/" className="text-gray-400 hover:text-violet-400 transition-colors">
                  Accueil
                </Link>
              </li>
              <li>
                <Link href="/strategies" className="text-gray-400 hover:text-violet-400 transition-colors">
                  Stratégies Ninja
                </Link>
              </li>
              <li>
                <Link href="/backtesting" className="text-gray-400 hover:text-violet-400 transition-colors">
                  Backtesting Live
                </Link>
              </li>
            </ul>
          </div>
          
          {/* Contact */}
          <div>
            <h4 className="text-white font-semibold mb-4">Contact</h4>
            <div className="flex gap-3">
              <a href="https://www.linkedin.com/company/findyouredge-app/about/" target="_blank" rel="noopener noreferrer" className="w-9 h-9 flex items-center justify-center bg-violet-500/10 hover:bg-violet-500/20 border border-violet-400/30 hover:border-violet-400/60 rounded-lg transition-all">
                <Linkedin className="w-4 h-4 text-violet-400" />
              </a>
              <a href="#" className="w-9 h-9 flex items-center justify-center bg-violet-500/10 hover:bg-violet-500/20 border border-violet-400/30 hover:border-violet-400/60 rounded-lg transition-all">
                <Mail className="w-4 h-4 text-violet-400" />
              </a>
            </div>
          </div>
        </div>
        
        {/* Bottom Bar */}
        <div className="pt-6 border-t border-violet-400/20">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="text-sm text-gray-400">
              © 2025 <span className="text-violet-400 font-semibold">FindYourEdge</span>. Tous droits réservés.
            </div>
            
            <div className="flex items-center gap-2 text-sm text-gray-400">
              <span>Fait avec</span>
              <span className="text-red-400 animate-pulse">❤</span>
              <span>pour les traders</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}
