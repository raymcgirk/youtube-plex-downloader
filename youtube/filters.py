def filter_videos(videos):
    # filter out live or member-only videos
    return [video for video in videos if video['availability'] != 'needs_auth' and not video['is_live']]
