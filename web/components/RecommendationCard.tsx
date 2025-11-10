'use client'

import React, { useState, useEffect } from 'react'
import type { Recommendation, Video } from '../lib/types'
import { Card, CardContent } from './ui/card'
import { RecommendationChatDialog } from './RecommendationChatDialog'
import { CreditUtilizationMotion } from './charts/CreditUtilizationMotion'
import { DebtAvalancheChart } from './charts/DebtAvalancheChart'
import { VideoCard } from './ui/video-card'
import { VideoDialog } from './VideoDialog'
import { api } from '../lib/api'

export function RecommendationCard({ rec }: { rec: Recommendation }) {
  const [videos, setVideos] = useState<Video[]>([])
  const [selectedVideo, setSelectedVideo] = useState<Video | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [loadingVideos, setLoadingVideos] = useState(false)

  // Fetch videos if recommendation has a topic
  useEffect(() => {
    if (rec.topic && rec.type === 'education') {
      setLoadingVideos(true)
      api.videos(rec.topic)
        .then(setVideos)
        .catch(err => {
          // Silently handle 404s for topics without videos
          if (!err.message.includes('404')) {
            console.error(`Failed to load videos for topic ${rec.topic}:`, err)
          }
          setVideos([])
        })
        .finally(() => setLoadingVideos(false))
    }
  }, [rec.topic, rec.type])

  // Render chart based on content type
  const renderChart = () => {
    if (!rec.content || !rec.content.type) return null

    switch (rec.content.type) {
      case 'credit_utilization':
        return <CreditUtilizationMotion
          utilization={rec.content.data.utilization}
          cardMask={rec.content.data.cardMask}
          data={rec.content.data}
          className="mt-4"
        />
      case 'debt_avalanche':
        return <DebtAvalancheChart debts={rec.content.data} className="mt-4" />
      default:
        return null
    }
  }

  const handleVideoClick = (video: Video) => {
    setSelectedVideo(video)
    setDialogOpen(true)
  }

  return (
    <>
      <Card className="mt-3">
        <CardContent className="py-4">
          <div className="font-semibold">{rec.title}</div>
          <div className="mt-1 text-sm text-muted-foreground">{rec.rationale}</div>

          {/* Videos Section - Show only the best video (first one) */}
          {videos.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-semibold mb-3 text-foreground/80">
                Learn More
              </h4>
              <div className="max-w-md">
                <VideoCard
                  video={videos[0]}
                  onClick={() => handleVideoClick(videos[0])}
                />
              </div>
            </div>
          )}

          {renderChart()}
          <RecommendationChatDialog recommendation={rec} />
        </CardContent>
      </Card>

      <VideoDialog
        video={selectedVideo}
        open={dialogOpen}
        onOpenChange={setDialogOpen}
      />
    </>
  )
}
