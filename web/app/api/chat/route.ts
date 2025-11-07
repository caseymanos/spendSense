import { openai } from '@ai-sdk/openai'
import { streamText } from 'ai'

// Allow streaming responses up to 30 seconds
export const maxDuration = 30

export async function POST(req: Request) {
  try {
    const { messages, recommendationId, recommendationTitle, recommendationRationale } = await req.json()

    // Create system message with recommendation context
    const systemMessage = {
      role: 'system' as const,
      content: `You are a helpful financial education assistant for SpendSense, an educational financial behavior analysis tool. You are helping a user understand a specific recommendation.

RECOMMENDATION CONTEXT:
- Title: ${recommendationTitle}
- Rationale: ${recommendationRationale}
- ID: ${recommendationId}

YOUR ROLE:
- Provide clear, educational explanations about this recommendation
- Help users understand WHY this recommendation was made based on their spending patterns
- Suggest practical next steps for implementing the advice
- Answer questions about financial concepts in simple terms
- Stay focused on this specific recommendation

IMPORTANT CONSTRAINTS:
- This is EDUCATIONAL content, NOT financial advice
- Always include a disclaimer when appropriate: "This is educational content, not financial advice."
- Use encouraging, supportive language (never shame or judge)
- Avoid phrases like "overspending", "bad habits", "lack discipline"
- Use alternatives like "consider reducing", "optimize your spending"
- Keep responses concise and actionable
- If asked about topics unrelated to this recommendation, politely redirect to the recommendation topic

TONE:
- Supportive and educational
- Clear and concise
- Encouraging without being condescending
- Professional but friendly`
    }

    const result = streamText({
      model: openai('gpt-4-turbo'),
      messages: [systemMessage, ...messages],
      temperature: 0.7,
    })

    return result.toTextStreamResponse()
  } catch (error) {
    console.error('Chat API error:', error)
    return new Response(
      JSON.stringify({ error: 'Failed to process chat request' }),
      {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      }
    )
  }
}
