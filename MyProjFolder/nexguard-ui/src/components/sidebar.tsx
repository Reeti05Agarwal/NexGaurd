'use client'
import { Link, useLocation } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { BarChart3, Shield, TrendingDown, Settings, User, LayoutDashboard } from 'lucide-react'

const navItems = [
  { href: '/', label: 'Dashboard', icon: LayoutDashboard },        // Changed from '/dashboard'
  { href: '/fraud', label: 'Fraud Detection', icon: Shield },
  { href: '/churn', label: 'Churn Analysis', icon: TrendingDown },
  { href: '/analytics', label: 'Analytics', icon: BarChart3 },
]

export function Sidebar() {
  const location = useLocation()
  const pathname = location.pathname

  return (
    <aside className="w-64 bg-sidebar text-sidebar-foreground border-r border-sidebar-border h-screen flex flex-col backdrop-blur-xl bg-gradient-to-b from-sidebar to-sidebar/80">
      {/* Logo */}
      <div className="p-6 border-b border-sidebar-border/30 bg-gradient-to-r from-sidebar-primary/10 to-sidebar-accent/10">
        <div className="flex items-center gap-2 mb-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-sidebar-primary to-sidebar-accent flex items-center justify-center">
            <BarChart3 size={18} className="text-sidebar-primary-foreground" />
          </div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-sidebar-primary to-sidebar-accent bg-clip-text text-transparent">CloudAI</h1>
        </div>
        <p className="text-xs text-sidebar-foreground/50">Analytics Intelligence</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href
          return (
            <Link
              key={item.href}
              to={item.href}  // Changed from href={item.href}
              className={cn(
                'flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200',
                isActive
                  ? 'bg-gradient-to-r from-sidebar-primary to-sidebar-accent text-sidebar-primary-foreground shadow-lg shadow-sidebar-primary/20'
                  : 'text-sidebar-foreground hover:bg-sidebar-accent/20 hover:text-sidebar-accent-foreground',
              )}
            >
              <Icon size={20} />
              <span className="text-sm font-medium">{item.label}</span>
            </Link>
          )
        })}
      </nav>

      {/* Settings Section */}
      <div className="border-t border-sidebar-border/30 p-4 space-y-3 bg-gradient-to-t from-sidebar/50 to-transparent">
        <Link
          to="/profile"  // Changed from href
          className={cn(
            'flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200',
            pathname === '/profile'
              ? 'bg-gradient-to-r from-sidebar-primary to-sidebar-accent text-sidebar-primary-foreground shadow-lg shadow-sidebar-primary/20'
              : 'text-sidebar-foreground hover:bg-sidebar-accent/20 hover:text-sidebar-accent-foreground',
          )}
        >
          <User size={20} />
          <span className="text-sm font-medium">Profile</span>
        </Link>

        <Link
          to="/settings"  // Changed from href
          className={cn(
            'flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200',
            pathname === '/settings'
              ? 'bg-gradient-to-r from-sidebar-primary to-sidebar-accent text-sidebar-primary-foreground shadow-lg shadow-sidebar-primary/20'
              : 'text-sidebar-foreground hover:bg-sidebar-accent/20 hover:text-sidebar-accent-foreground',
          )}
        >
          <Settings size={20} />
          <span className="text-sm font-medium">Settings</span>
        </Link>
      </div>
    </aside>
  )
}