'use client';

import { cn } from '@/lib/utils';
import React, { useMemo, type ComponentProps } from 'react';
import ReactMarkdown, { type Options } from 'react-markdown';
import rehypeKatex from 'rehype-katex';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import 'katex/dist/katex.min.css';

export interface ResponseProps extends ComponentProps<'div'> {
  children: string;
  options?: Omit<Options, 'children'>;
  allowedImagePrefixes?: string[];
  allowedLinkPrefixes?: string[];
  defaultOrigin?: string;
  parseIncompleteMarkdown?: boolean;
}

function parseIncompleteContent(content: string): string {
  if (!content) return content;

  // Count formatting tokens to determine if they need to be closed
  const boldCount = (content.match(/\*\*/g) || []).length;
  const italicCount = (content.match(/(?<!\*)\*(?!\*)/g) || []).length;
  const strikeCount = (content.match(/~~/g) || []).length;
  const codeCount = (content.match(/`/g) || []).length;

  let result = content;

  // Auto-close incomplete bold
  if (boldCount % 2 !== 0 && !content.endsWith('**')) {
    result += '**';
  }

  // Auto-close incomplete italic
  if (italicCount % 2 !== 0 && !content.endsWith('*')) {
    result += '*';
  }

  // Auto-close incomplete strikethrough
  if (strikeCount % 2 !== 0 && !content.endsWith('~~')) {
    result += '~~';
  }

  // Auto-close incomplete code (but not in code blocks)
  if (codeCount % 2 !== 0 && !content.includes('```')) {
    result += '`';
  }

  return result;
}

export function Response({
  children,
  className,
  options,
  allowedImagePrefixes = ['*'],
  allowedLinkPrefixes = ['*'],
  defaultOrigin,
  parseIncompleteMarkdown = true,
  ...props
}: ResponseProps) {
  const content = useMemo(() => {
    if (parseIncompleteMarkdown && typeof children === 'string') {
      return parseIncompleteContent(children);
    }
    return children;
  }, [children, parseIncompleteMarkdown]);

  return (
    <div
      className={cn(
        'prose prose-sm dark:prose-invert max-w-none',
        'prose-p:leading-relaxed prose-pre:p-0',
        'prose-headings:font-semibold prose-headings:tracking-tight',
        'prose-a:text-primary prose-a:no-underline hover:prose-a:underline',
        'prose-code:text-sm prose-code:bg-muted prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded-md prose-code:before:content-none prose-code:after:content-none',
        'prose-pre:bg-muted prose-pre:border prose-pre:border-border',
        'prose-blockquote:border-l-primary prose-blockquote:italic',
        'prose-ul:list-disc prose-ol:list-decimal',
        'prose-li:marker:text-muted-foreground',
        'prose-table:border prose-table:border-border',
        'prose-th:border prose-th:border-border prose-th:bg-muted prose-th:px-4 prose-th:py-2',
        'prose-td:border prose-td:border-border prose-td:px-4 prose-td:py-2',
        'prose-img:rounded-lg prose-img:border prose-img:border-border',
        className
      )}
      {...props}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex]}
        components={{
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '');
            const language = match ? match[1] : '';

            if (!inline) {
              return (
                <div className="relative group">
                  <pre className="overflow-x-auto p-4 rounded-lg bg-muted border border-border">
                    <code className={cn('text-sm', className)} {...props}>
                      {children}
                    </code>
                  </pre>
                  {language && (
                    <div className="absolute top-2 right-2 text-xs text-muted-foreground bg-background/80 px-2 py-1 rounded">
                      {language}
                    </div>
                  )}
                </div>
              );
            }

            return (
              <code className={className} {...props}>
                {children}
              </code>
            );
          },
          a({ href, children, ...props }) {
            // Security: Check if link is allowed
            const isAllowed =
              allowedLinkPrefixes.includes('*') ||
              allowedLinkPrefixes.some((prefix) => href?.startsWith(prefix));

            if (!isAllowed) return <>{children}</>;

            const fullHref =
              href?.startsWith('/') && defaultOrigin
                ? `${defaultOrigin}${href}`
                : href;

            return (
              <a
                href={fullHref}
                target="_blank"
                rel="noopener noreferrer"
                {...props}
              >
                {children}
              </a>
            );
          },
          img({ src, alt, ...props }) {
            // Security: Check if image is allowed
            const isAllowed =
              allowedImagePrefixes.includes('*') ||
              allowedImagePrefixes.some((prefix) => src?.startsWith(prefix));

            if (!isAllowed) return null;

            const fullSrc =
              src?.startsWith('/') && defaultOrigin
                ? `${defaultOrigin}${src}`
                : src;

            return <img src={fullSrc} alt={alt} loading="lazy" {...props} />;
          },
        }}
        {...options}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
