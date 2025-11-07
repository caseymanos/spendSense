'use client'

import React from 'react'
import { CreditUtilizationMotion } from './CreditUtilizationMotion'

interface PaymentScenario {
  months: number
  monthlyPayment: number
  totalInterest: number
  totalPaid: number
}

interface CreditUtilizationData {
  utilization: number
  cardMask?: string
  currentBalance?: number
  creditLimit?: number
  availableCredit?: number
  apr?: number
  monthlyInterest?: number
  recommendedBalance?: number
  amountOverTarget?: number
  minimumPayment?: number
  paymentScenarios?: PaymentScenario[]
}

interface CreditUtilizationGaugeProps {
  utilization: number
  cardMask?: string
  data?: CreditUtilizationData
  className?: string
}

export function CreditUtilizationGauge(props: CreditUtilizationGaugeProps) {
  // Wrapper component that renders the Motion version
  return <CreditUtilizationMotion {...props} />
}
