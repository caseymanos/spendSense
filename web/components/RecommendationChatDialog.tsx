"use client"

import * as React from "react"
import { MessageCircle, Bot, User } from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./ui/dialog"
import { Button } from "./ui/button"
import { PromptInput } from "./ui/prompt-input"
import type { Recommendation } from "../lib/types"
import { cn } from "@/lib/utils"

interface RecommendationChatDialogProps {
  recommendation: Recommendation
}

interface ChatMessage {
  id: string
  role: "user" | "assistant"
  content: string
}

export function RecommendationChatDialog({
  recommendation,
}: RecommendationChatDialogProps) {
  const [isOpen, setIsOpen] = React.useState(false)
  const [messages, setMessages] = React.useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = React.useState(false)
  const scrollRef = React.useRef<HTMLDivElement>(null)

  // Auto-scroll on new messages
  React.useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  const handlePromptSubmit = async (value: string) => {
    if (!value.trim() || isLoading) return

    // Add user message
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: value,
    }

    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [...messages, userMessage].map(m => ({
            role: m.role,
            content: m.content
          })),
          recommendationId: recommendation.recommendation_id,
          recommendationTitle: recommendation.title,
          recommendationRationale: recommendation.rationale,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to send message')
      }

      // Read the streaming response
      const reader = response.body?.getReader()
      if (!reader) throw new Error('No response body')

      const decoder = new TextDecoder()
      let assistantContent = ''
      const assistantMessageId = `assistant-${Date.now()}`

      // Add placeholder for assistant message
      setMessages((prev) => [
        ...prev,
        { id: assistantMessageId, role: "assistant", content: '' }
      ])

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        assistantContent += chunk

        // Update the assistant message with accumulated content
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMessageId
              ? { ...msg, content: assistantContent }
              : msg
          )
        )
      }
    } catch (error) {
      console.error('Failed to send message:', error)
      // Add error message
      setMessages((prev) => [
        ...prev,
        {
          id: `error-${Date.now()}`,
          role: "assistant",
          content: "Sorry, I encountered an error. Please try again.",
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className="mt-3 w-full"
        >
          <MessageCircle className="mr-2 h-4 w-4" />
          Ask Questions
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px] h-[600px] flex flex-col p-0">
        <DialogHeader className="p-6 pb-4">
          <DialogTitle className="flex items-center gap-2">
            <MessageCircle className="h-5 w-5" />
            Ask About This Recommendation
          </DialogTitle>
          <DialogDescription className="text-xs line-clamp-2">
            {recommendation.title}
          </DialogDescription>
        </DialogHeader>

        {/* Chat Messages Area */}
        <div
          ref={scrollRef}
          className="flex-1 overflow-y-auto px-6 pb-4 space-y-4"
        >
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground">
              <Bot className="h-12 w-12 mb-4 opacity-50" />
              <p className="text-sm">
                Ask me anything about this recommendation!
              </p>
              <p className="text-xs mt-2 max-w-sm">
                I can help explain the rationale, suggest next steps, or answer
                questions about how to implement this advice.
              </p>
            </div>
          ) : (
            messages.map((message: ChatMessage) => (
              <div
                key={message.id}
                className={cn(
                  "flex gap-3 items-start",
                  message.role === "user" && "flex-row-reverse"
                )}
              >
                <div
                  className={cn(
                    "flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-full",
                    message.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted"
                  )}
                >
                  {message.role === "user" ? (
                    <User className="h-4 w-4" />
                  ) : (
                    <Bot className="h-4 w-4" />
                  )}
                </div>
                <div
                  className={cn(
                    "flex-1 space-y-2 overflow-hidden rounded-lg px-4 py-2.5 text-sm",
                    message.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted"
                  )}
                >
                  {message.content}
                </div>
              </div>
            ))
          )}
          {isLoading && messages[messages.length - 1]?.role !== "assistant" && (
            <div className="flex gap-3 items-start">
              <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-full bg-muted">
                <Bot className="h-4 w-4" />
              </div>
              <div className="flex-1 space-y-2 overflow-hidden rounded-lg px-4 py-2.5 text-sm bg-muted">
                <div className="flex gap-1">
                  <div className="h-2 w-2 rounded-full bg-foreground/40 animate-bounce [animation-delay:-0.3s]"></div>
                  <div className="h-2 w-2 rounded-full bg-foreground/40 animate-bounce [animation-delay:-0.15s]"></div>
                  <div className="h-2 w-2 rounded-full bg-foreground/40 animate-bounce"></div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t p-4 bg-muted/30">
          <PromptInput
            onSubmit={handlePromptSubmit}
            isLoading={isLoading}
          />
        </div>
      </DialogContent>
    </Dialog>
  )
}
