import { NextResponse } from 'next/server'
import { cookies } from 'next/headers'

const DEMO_PASSWORD = 'gauntletai'

export async function POST(request: Request) {
  try {
    const { password } = await request.json()

    if (password === DEMO_PASSWORD) {
      // Set authentication cookie
      cookies().set('demo-auth', DEMO_PASSWORD, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 60 * 60 * 24 * 7, // 7 days
        path: '/',
      })

      return NextResponse.json({ success: true })
    } else {
      return NextResponse.json(
        { error: 'Invalid password' },
        { status: 401 }
      )
    }
  } catch (error) {
    console.error('Login error:', error)
    return NextResponse.json(
      { error: 'Login failed' },
      { status: 500 }
    )
  }
}
