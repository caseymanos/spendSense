"use client"

import * as React from "react"
import { Paperclip, CornerDownLeft } from "lucide-react"
import { cn } from "@/lib/utils"

export interface PromptInputProps
  extends Omit<React.TextareaHTMLAttributes<HTMLTextAreaElement>, 'onSubmit'> {
  onSubmit?: (value: string) => void
  isLoading?: boolean
}

const PromptInput = React.forwardRef<HTMLTextAreaElement, PromptInputProps>(
  ({ className, onSubmit, isLoading, ...props }, ref) => {
    const [value, setValue] = React.useState("")
    const textareaRef = React.useRef<HTMLTextAreaElement>(null)

    React.useImperativeHandle(ref, () => textareaRef.current!)

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault()
        handleSubmit()
      }
    }

    const handleSubmit = () => {
      if (value.trim() && !isLoading && onSubmit) {
        onSubmit(value)
        setValue("")
        if (textareaRef.current) {
          textareaRef.current.style.height = "auto"
        }
      }
    }

    const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      setValue(e.target.value)
      // Auto-resize textarea
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto"
        textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
      }
    }

    return (
      <div className="relative flex items-end gap-2 rounded-lg border bg-background p-2">
        <textarea
          ref={textareaRef}
          className={cn(
            "min-h-[60px] max-h-[200px] w-full resize-none bg-transparent px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50",
            className
          )}
          placeholder="Ask a question about this recommendation..."
          value={value}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          rows={1}
          {...props}
        />
        <div className="flex gap-1">
          <button
            type="button"
            onClick={handleSubmit}
            disabled={!value.trim() || isLoading}
            className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-9 w-9"
          >
            <CornerDownLeft className="h-4 w-4" />
            <span className="sr-only">Send message</span>
          </button>
        </div>
      </div>
    )
  }
)

PromptInput.displayName = "PromptInput"

export { PromptInput }
