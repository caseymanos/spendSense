"use client";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Video } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { ExternalLink } from "lucide-react";
import YoutubeVideo from "youtube-video-element/react";
import MediaThemeSutro from "player.style/sutro/react";

interface VideoDialogProps {
  video: Video | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function VideoDialog({ video, open, onOpenChange }: VideoDialogProps) {
  if (!video) return null;

  const youtubeWatchUrl = `https://www.youtube.com/watch?v=${video.youtube_id}`;
  const youtubeVideoUrl = `https://www.youtube.com/watch?v=${video.youtube_id}`;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl p-0 overflow-hidden">
        {/* Video Player */}
        <div className="relative w-full aspect-video bg-black">
          <MediaThemeSutro
            style={
              {
                "--media-primary-color": "#1e1a1a",
                width: "100%",
                height: "100%",
                aspectRatio: "16/9",
              } as React.CSSProperties
            }
          >
            <YoutubeVideo
              slot="media"
              src={youtubeVideoUrl}
              playsInline
              crossOrigin="anonymous"
              style={{ width: "100%", height: "100%", aspectRatio: "16/9" }}
            />
          </MediaThemeSutro>
        </div>

        {/* Video Details */}
        <DialogHeader className="p-6 space-y-3">
          <DialogTitle className="text-xl font-bold leading-tight pr-8">
            {video.title}
          </DialogTitle>

          {video.channel_name && (
            <div className="flex items-center gap-2">
              <Badge variant="default" className="font-normal">
                {video.channel_name}
              </Badge>
              <a
                href={youtubeWatchUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-muted-foreground hover:text-primary transition-colors inline-flex items-center gap-1"
              >
                Watch on YouTube
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          )}

          {video.description && (
            <DialogDescription className="text-sm leading-relaxed">
              {video.description}
            </DialogDescription>
          )}
        </DialogHeader>
      </DialogContent>
    </Dialog>
  );
}
