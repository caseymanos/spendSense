'use client'

import React, { useEffect, useState } from 'react'

interface Transaction {
  date: string
  merchant_name: string
  personal_finance_category: string
  amount: number
  account_name: string
  mask: string
  account_subtype?: string
}

interface PersonaTransactionsTableProps {
  userId: string
  persona?: string
  personaColor?: string
  personaIcon?: string
  limit?: number
}

const PERSONA_INFO: Record<string, { icon: string; color: string }> = {
  'High Utilization': { icon: '💳', color: '#E63946' },
  'Variable Income Budgeter': { icon: '📊', color: '#F77F00' },
  'Subscription-Heavy': { icon: '🔄', color: '#06AED5' },
  'Savings Builder': { icon: '🌱', color: '#2A9D8F' },
  'Cash Flow Optimizer': { icon: '💰', color: '#457B9D' },
  'General': { icon: '👤', color: '#A8DADC' }
}

const PERSONA_CONTEXT: Record<string, { title: string; description: string }> = {
  'High Utilization': {
    title: 'Credit Card Activity',
    description: 'Recent credit card transactions affecting your utilization'
  },
  'Variable Income Budgeter': {
    title: 'Income Deposits',
    description: 'Your recent income and payroll deposits'
  },
  'Subscription-Heavy': {
    title: 'Recurring Subscriptions',
    description: 'Your active subscription services and recurring payments'
  },
  'Savings Builder': {
    title: 'Savings Activity',
    description: 'Recent transfers and activity in your savings accounts'
  },
  'Cash Flow Optimizer': {
    title: 'Spending Overview',
    description: 'Recent purchases and spending patterns'
  },
  'General': {
    title: 'Recent Transactions',
    description: 'Your latest account activity'
  }
}

export function PersonaTransactionsTable({
  userId,
  persona = 'General',
  personaColor,
  personaIcon,
  limit = 10
}: PersonaTransactionsTableProps) {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const info = PERSONA_INFO[persona] || PERSONA_INFO['General']
  const context = PERSONA_CONTEXT[persona] || PERSONA_CONTEXT['General']
  const color = personaColor || info.color
  const icon = personaIcon || info.icon

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        setLoading(true)
        setError(null)
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        const response = await fetch(`${apiUrl}/transactions/${userId}?limit=${limit}`)

        if (!response.ok) {
          throw new Error(`Failed to fetch transactions: ${response.statusText}`)
        }

        const data = await response.json()
        setTransactions(data.transactions || [])
      } catch (err) {
        console.error('Error fetching transactions:', err)
        setError(err instanceof Error ? err.message : 'Failed to load transactions')
      } finally {
        setLoading(false)
      }
    }

    if (userId) {
      fetchTransactions()
    }
  }, [userId, limit])

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  }

  const formatCategory = (category: string) => {
    return category.replace(/_/g, ' ').split(' ').map(word =>
      word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
    ).join(' ')
  }

  const formatAmount = (amount: number) => {
    // In the data model, negative amounts are income/deposits
    if (amount < 0) {
      return { display: `+$${Math.abs(amount).toFixed(2)}`, className: 'text-green-600' }
    } else {
      return { display: `-$${amount.toFixed(2)}`, className: 'text-red-600' }
    }
  }

  if (loading) {
    return (
      <div className="rounded-2xl p-6 text-center text-gray-500"
           style={{
             background: `linear-gradient(135deg, ${color}15 0%, ${color}08 100%)`,
             backdropFilter: 'blur(16px)',
             border: `1px solid ${color}40`,
             boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.15)'
           }}>
        Loading transactions...
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-2xl p-6 text-center text-red-600"
           style={{
             background: `linear-gradient(135deg, ${color}15 0%, ${color}08 100%)`,
             backdropFilter: 'blur(16px)',
             border: `1px solid ${color}40`,
             boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.15)'
           }}>
        {error}
      </div>
    )
  }

  if (transactions.length === 0) {
    return (
      <div className="rounded-2xl p-6 text-center text-gray-500"
           style={{
             background: `linear-gradient(135deg, ${color}15 0%, ${color}08 100%)`,
             backdropFilter: 'blur(16px)',
             border: `1px solid ${color}40`,
             boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.15)'
           }}>
        No transactions found
      </div>
    )
  }

  return (
    <div className="rounded-2xl p-6 my-5"
         style={{
           background: `linear-gradient(135deg, ${color}15 0%, ${color}08 100%)`,
           backdropFilter: 'blur(16px)',
           WebkitBackdropFilter: 'blur(16px)',
           border: `1px solid ${color}40`,
           boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.15)'
         }}>
      {/* Header */}
      <div className="flex items-center gap-3 mb-2">
        <div className="text-3xl" style={{ filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.1))' }}>
          {icon}
        </div>
        <h3 className="text-2xl font-bold text-gray-800">
          {context.title}
        </h3>
      </div>
      <p className="text-gray-600 text-sm font-medium mb-5">
        {context.description}
      </p>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full border-separate border-spacing-0 text-sm">
          <thead>
            <tr className="rounded-lg"
                style={{
                  background: `linear-gradient(135deg, ${color}25, ${color}15)`
                }}>
              <th className="px-4 py-3.5 text-left font-bold text-gray-700 uppercase text-xs tracking-wide first:rounded-tl-lg"
                  style={{ borderBottom: `2px solid ${color}50` }}>
                Date
              </th>
              <th className="px-4 py-3.5 text-left font-bold text-gray-700 uppercase text-xs tracking-wide"
                  style={{ borderBottom: `2px solid ${color}50` }}>
                Merchant
              </th>
              <th className="px-4 py-3.5 text-left font-bold text-gray-700 uppercase text-xs tracking-wide"
                  style={{ borderBottom: `2px solid ${color}50` }}>
                Category
              </th>
              <th className="px-4 py-3.5 text-right font-bold text-gray-700 uppercase text-xs tracking-wide"
                  style={{ borderBottom: `2px solid ${color}50` }}>
                Amount
              </th>
              <th className="px-4 py-3.5 text-left font-bold text-gray-700 uppercase text-xs tracking-wide last:rounded-tr-lg"
                  style={{ borderBottom: `2px solid ${color}50` }}>
                Account
              </th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((txn, idx) => {
              const amountInfo = formatAmount(txn.amount)
              return (
                <tr key={idx}
                    className="transition-all duration-200 hover:translate-x-1"
                    style={{
                      background: 'rgba(255, 255, 255, 0.6)',
                      borderBottom: `1px solid ${color}20`
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = `${color}20`
                      e.currentTarget.style.boxShadow = `-4px 0 0 0 ${color}`
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = 'rgba(255, 255, 255, 0.6)'
                      e.currentTarget.style.boxShadow = 'none'
                    }}>
                  <td className="px-4 py-3.5">
                    <span className="font-semibold text-gray-600 tabular-nums">
                      {formatDate(txn.date)}
                    </span>
                  </td>
                  <td className="px-4 py-3.5">
                    <span className="font-semibold text-gray-800">
                      {txn.merchant_name}
                    </span>
                  </td>
                  <td className="px-4 py-3.5">
                    <span className="text-xs font-medium px-2.5 py-1 rounded-xl inline-block"
                          style={{
                            background: `${color}20`,
                            color: '#718096'
                          }}>
                      {formatCategory(txn.personal_finance_category)}
                    </span>
                  </td>
                  <td className="px-4 py-3.5 text-right">
                    <span className={`font-bold tabular-nums ${amountInfo.className}`}>
                      {amountInfo.display}
                    </span>
                  </td>
                  <td className="px-4 py-3.5">
                    <span className="text-sm text-gray-500 font-mono">
                      {txn.account_name} (••{txn.mask})
                    </span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
