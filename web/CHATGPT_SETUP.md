# ChatGPT Recommendation Q&A Setup

This document explains how to set up and use the ChatGPT-powered Q&A feature for recommendations.

## Overview

Each recommendation card now includes an "Ask Questions" button that opens a ChatGPT-powered dialog where users can:
- Ask questions about the recommendation
- Get explanations about why the recommendation was made
- Learn about next steps for implementing the advice
- Understand financial concepts in simple terms

## Prerequisites

- OpenAI API account
- OpenAI API key

## Setup Instructions

### 1. Get an OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to [API Keys](https://platform.openai.com/api-keys)
4. Click "Create new secret key"
5. Copy the API key (you won't be able to see it again)

### 2. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cd web
   cp .env.example .env.local
   ```

2. Edit `.env.local` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

3. (Optional) Configure your backend API URL if it's not on localhost:8000:
   ```
   NEXT_PUBLIC_API_URL=http://your-backend-url:port
   ```

### 3. Install Dependencies

If you haven't already, install the required dependencies:

```bash
cd web
npm install
```

This installs:
- `ai` - Vercel AI SDK for streaming responses
- `@ai-sdk/openai` - OpenAI provider for AI SDK
- `framer-motion` - Animation library
- `@radix-ui/react-dialog` - Dialog component
- `@radix-ui/react-scroll-area` - Scroll area component

### 4. Start the Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Usage

### For End Users

1. Navigate to the Learning Feed page (`/learn`)
2. Each recommendation card displays a title and rationale
3. Click the "Ask Questions" button at the bottom of any card
4. A dialog opens with a chat interface
5. Type your question in the input field
6. Press Enter or click the send button
7. ChatGPT will respond with educational information about the recommendation

### Example Questions

Users might ask:
- "Why did I get this recommendation?"
- "How can I implement this advice?"
- "What does [financial term] mean?"
- "What are the next steps?"
- "How will this help my financial situation?"

## Features

### Educational Focus

The ChatGPT assistant is configured to:
- Provide educational content (NOT financial advice)
- Use supportive, encouraging language
- Avoid shaming or judgmental phrases
- Focus on the specific recommendation context
- Include disclaimers when appropriate

### Smart Context

Each chat session includes:
- The recommendation title
- The recommendation rationale
- The recommendation ID
- User's spending patterns (via the rationale)

### UI/UX Features

- **Streaming responses**: Messages appear in real-time as ChatGPT generates them
- **Auto-scroll**: Chat automatically scrolls to show new messages
- **Loading indicators**: Visual feedback while waiting for responses
- **Responsive design**: Works on mobile and desktop
- **Dark mode support**: Respects system theme preference
- **Keyboard shortcuts**: Press Enter to send, Shift+Enter for new line

## Architecture

### Components

1. **RecommendationCard** (`/components/RecommendationCard.tsx`)
   - Displays recommendation information
   - Includes the chat dialog trigger button

2. **RecommendationChatDialog** (`/components/RecommendationChatDialog.tsx`)
   - Main dialog component
   - Manages chat state with `useChat` hook
   - Handles message display and input

3. **PromptInput** (`/components/ui/prompt-input.tsx`)
   - Custom input component based on shadcn/ai design
   - Auto-resizing textarea
   - Keyboard shortcuts
   - Submit button with loading state

4. **Dialog, ScrollArea** (`/components/ui/`)
   - Reusable UI primitives from shadcn/ui
   - Based on Radix UI components

### API Route

**Endpoint**: `POST /api/chat`

**Request Body**:
```json
{
  "messages": [
    { "role": "user", "content": "Why did I get this recommendation?" }
  ],
  "recommendationId": "rec_123",
  "recommendationTitle": "Consider reducing subscription spending",
  "recommendationRationale": "You have 5 active subscriptions totaling $87/month..."
}
```

**Response**: Server-Sent Events (SSE) stream with chat completion chunks

**Model**: GPT-4 Turbo

**Configuration**:
- Temperature: 0.7 (balanced creativity and consistency)
- Max tokens: 500 (concise responses)
- Max duration: 30 seconds

### System Prompt

The assistant uses a carefully crafted system prompt that:
1. Establishes the educational context
2. Provides the specific recommendation details
3. Sets clear constraints and tone guidelines
4. Prevents off-topic discussions
5. Enforces SpendSense's ethical guidelines

## Ethical Considerations

This feature follows SpendSense's core principles:

### Transparency
- All responses are clearly marked as educational content
- Users know they're interacting with AI
- The system explains its limitations

### User Control
- Users choose when to engage with the chat
- No automatic suggestions or prompts
- Easy to close and dismiss

### Education Over Sales
- Focused on learning and understanding
- No product recommendations or affiliate links
- No pressure to make financial decisions

### Tone Validation
The system avoids:
- ❌ "overspending"
- ❌ "bad habits"
- ❌ "lack discipline"

Instead uses:
- ✅ "consider reducing"
- ✅ "optimize your spending"
- ✅ "opportunity to save"

## Cost Considerations

### OpenAI API Pricing (as of 2024)

**GPT-4 Turbo**:
- Input: $10 per 1M tokens
- Output: $30 per 1M tokens

**Estimated costs per conversation**:
- Average conversation: 5 messages
- Average input: ~500 tokens (system prompt + history)
- Average output: ~300 tokens per response
- **Cost per conversation**: ~$0.05 - $0.10

### Cost Management Tips

1. **Set usage limits** in OpenAI dashboard
2. **Monitor usage** via OpenAI platform
3. **Consider cheaper models** (GPT-3.5 Turbo) for development
4. **Implement rate limiting** for production
5. **Add caching** for common questions

### Rate Limiting (Future Enhancement)

Consider adding:
- Max conversations per user per day
- Max messages per conversation
- Cooldown periods between requests

## Troubleshooting

### "Failed to process chat request"

**Possible causes**:
1. Missing or invalid `OPENAI_API_KEY`
2. OpenAI API rate limits exceeded
3. Network connectivity issues
4. Insufficient OpenAI credits

**Solutions**:
- Verify your API key in `.env.local`
- Check OpenAI dashboard for rate limits
- Ensure you have credits in your OpenAI account

### Chat doesn't open

**Possible causes**:
1. JavaScript errors in console
2. Missing dependencies
3. Component import errors

**Solutions**:
- Check browser console for errors
- Run `npm install` to ensure all dependencies are installed
- Clear `.next` cache: `rm -rf .next`

### Responses are slow

**Possible causes**:
1. Using GPT-4 (slower but higher quality)
2. High OpenAI API load
3. Network latency

**Solutions**:
- Switch to GPT-3.5 Turbo in `/app/api/chat/route.ts`
- Check OpenAI status page
- Reduce `maxTokens` for faster responses

## Future Enhancements

Potential improvements:
- [ ] Conversation history persistence
- [ ] Export conversation to text/PDF
- [ ] Voice input/output
- [ ] Multi-language support
- [ ] Fine-tuned model on SpendSense data
- [ ] Suggested questions/prompts
- [ ] Feedback collection (👍/👎)
- [ ] Analytics dashboard for common questions

## Security Notes

⚠️ **Important Security Considerations**:

1. **Never commit `.env.local`** - It contains your API key
2. **Use environment variables only** - Don't hardcode API keys
3. **Rotate API keys regularly** - Generate new keys periodically
4. **Set usage limits** - Prevent unexpected charges
5. **Implement authentication** - Restrict access to authorized users only

## Support

For issues or questions:
1. Check the [OpenAI API documentation](https://platform.openai.com/docs)
2. Review the [Vercel AI SDK documentation](https://sdk.vercel.ai/docs)
3. Check the [Next.js documentation](https://nextjs.org/docs)
4. Contact the SpendSense development team

## References

- [Vercel AI SDK](https://sdk.vercel.ai/)
- [OpenAI Platform](https://platform.openai.com/)
- [shadcn/ui](https://ui.shadcn.com/)
- [Radix UI](https://www.radix-ui.com/)
- [Next.js App Router](https://nextjs.org/docs/app)
