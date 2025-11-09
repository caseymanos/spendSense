import { NextResponse } from 'next/server'
import { cookies } from 'next/headers'

export async function POST() {
  // Clear authentication cookie
  cookies().delete('demo-auth')

  return NextResponse.json({ success: true })
}
