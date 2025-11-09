"use client";

import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Play, Clock } from "lucide-react";
import { Video } from "@/lib/types";

interface VideoCardProps {
  video: Video;
  onClick?: () => void;
}

function formatDuration(seconds: number | null | undefined): string {
  if (!seconds) return "";

  if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  } else {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
}

export function VideoCard({ video, onClick }: VideoCardProps) {
  // Use thumbnail URL from API (already includes YouTube CDN URL)
  const [imgError, setImgError] = useState(false);

  const handleImageError = () => {
    setImgError(true);
  };

  return (
    <Card
      className="group relative overflow-hidden cursor-pointer transition-all hover:shadow-lg hover:scale-[1.02] border-border/50"
      onClick={onClick}
    >
      {/* Thumbnail Container */}
      <div className="relative aspect-video bg-muted overflow-hidden flex items-center justify-center">
        {!imgError ? (
          <img
            src={video.thumbnail_url}
            alt={video.title}
            className="w-full h-full object-cover transition-transform group-hover:scale-105"
            loading="lazy"
            onError={handleImageError}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-muted">
            <Play className="w-16 h-16 text-muted-foreground/50" />
          </div>
        )}

        {/* Play Overlay */}
        <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
          <div className="bg-white/90 rounded-full p-4 transform group-hover:scale-110 transition-transform">
            <Play className="w-8 h-8 text-black fill-black" />
          </div>
        </div>

        {/* Duration Badge */}
        {video.duration_seconds && (
          <Badge
            variant="secondary"
            className="absolute bottom-2 right-2 bg-black/80 text-white border-0 backdrop-blur-sm"
          >
            <Clock className="w-3 h-3 mr-1" />
            {formatDuration(video.duration_seconds)}
          </Badge>
        )}
      </div>

      {/* Video Info */}
      <div className="p-3 space-y-1">
        <h4 className="font-semibold text-sm line-clamp-2 leading-snug group-hover:text-primary transition-colors">
          {video.title}
        </h4>

        {video.channel_name && (
          <p className="text-xs text-muted-foreground">
            {video.channel_name}
          </p>
        )}
      </div>
    </Card>
  );
}
