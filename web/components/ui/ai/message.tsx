'use client';

import { cn } from '@/lib/utils';
import { Bot, User } from 'lucide-react';
import type { ComponentProps, ReactNode } from 'react';

export type MessageProps = ComponentProps<'div'> & {
  from: 'user' | 'assistant';
  children: ReactNode;
};

export const Message = ({ from, className, children, ...props }: MessageProps) => (
  <div
    className={cn(
      'flex gap-3 items-start',
      from === 'user' ? 'flex-row-reverse' : '',
      className
    )}
    {...props}
  >
    {children}
  </div>
);

export type MessageContentProps = ComponentProps<'div'>;

export const MessageContent = ({ className, children, ...props }: MessageContentProps) => (
  <div
    className={cn(
      'flex-1 space-y-2 overflow-hidden rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm',
      className
    )}
    {...props}
  >
    {children}
  </div>
);

export type MessageAvatarProps = ComponentProps<'div'> & {
  name?: string;
  src?: string;
};

export const MessageAvatar = ({ name, src, className, ...props }: MessageAvatarProps) => (
  <div
    className={cn(
      'flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-full border-2 shadow-sm',
      className
    )}
    {...props}
  >
    {src ? (
      <img src={src} alt={name} className="h-full w-full rounded-full object-cover" />
    ) : name === 'User' ? (
      <User className="h-4 w-4" />
    ) : (
      <Bot className="h-4 w-4" />
    )}
  </div>
);
