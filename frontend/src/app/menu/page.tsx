'use client'

import React from 'react'
import IndianMenu from '@/components/menu/indian-menu'
import { DashboardHeader } from '@/components/layout/dashboard-header'

export default function MenuPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-red-50">
      <DashboardHeader />
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Authentic Indian Menu
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Discover the rich flavors and traditional recipes of Indian cuisine, 
            from stuffed parathas to street food favorites.
          </p>
        </div>
        <IndianMenu />
      </div>
    </div>
  )
}