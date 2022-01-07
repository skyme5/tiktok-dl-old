from datetime import datetime

from tiktok_dl.utils import int_or_none, str_or_none, try_get


def aweme_extractor(video_data: dict):
    video_info = try_get(video_data, lambda x: x["videoData"]["itemInfos"], dict)
    author_info = try_get(video_data, lambda x: x["videoData"]["authorInfos"], dict)
    share_info = try_get(video_data, lambda x: x["shareMeta"], dict)
    music_info = try_get(video_data, lambda x: x["videoData"]["musicInfos"], dict)
    author_stats = try_get(video_data, lambda x: x["videoData"]["authorStats"], dict)

    unique_id = str_or_none(author_info.get("uniqueId"))
    timestamp = try_get(video_info, lambda x: int(x["createTime"]), int)
    date = datetime.utcfromtimestamp(timestamp).strftime("%Y%m%d")

    height = try_get(video_info, lambda x: x["video"]["videoMeta"]["height"], int)
    width = try_get(video_info, lambda x: x["video"]["videoMeta"]["width"], int)

    return {
        "id": str_or_none(video_info.get("id")),
        "play_urls": try_get(video_info, lambda x: x["video"]["urls"], list),
        "ext": "mp4",
        "width": width,
        "height": height,
        "duration": try_get(
            video_info, lambda x: x["video"]["videoMeta"]["duration"], int
        ),
        "thumbnails": try_get(video_info, lambda x: x["covers"], list),
        "comment_count": int_or_none(video_info.get("commentCount")),
        "digg_count": int_or_none(video_info.get("diggCount")),
        "share_count": int_or_none(video_info.get("shareCount")),
        "play_count": int_or_none(video_info.get("playCount")),
        "create_time": timestamp,
        "upload_date": date,
        "title": "{} on TikTok".format(str_or_none(author_info.get("nickName"))),
        "description": str_or_none(share_info.get("desc")),
        "nick_name": str_or_none(author_info.get("nickName")),
        "unique_id": unique_id,
        "sec_uid": str_or_none(author_info.get("secUid")),
        "user_id": str_or_none(author_info.get("userId")),
        "user_url": "https://www.tiktok.com/@" + unique_id,
        "profile_pics": try_get(author_info, lambda x: x["covers"], list),
        "webpage_url": "https://www.tiktok.com/@{}/video/{}?source=h5_t".format(
            str_or_none(author_info.get("uniqueId")), str_or_none(video_info.get("id"))
        ),
        "follower_count": int_or_none(author_stats.get("followerCount")),
        "heart_total": str_or_none(author_stats.get("heartCount")),
        "challenge_list": try_get(
            video_data, lambda x: x["videoData"]["challengeInfoList"], list
        ),
        "duet_info": try_get(video_data, lambda x: x["videoData"]["duetInfo"], str),
        "text_extra": try_get(video_data, lambda x: x["videoData"]["textExtra"], list),
        "music_id": str_or_none(music_info.get("musicId")),
        "music_title": str_or_none(music_info.get("musicName")),
        "music_artist": str_or_none(music_info.get("authorName")),
        "music_covers": try_get(music_info, lambda x: x["covers"], list),
    }
