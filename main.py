from fastapi import FastAPI, HTTPException, Query
import yt_dlp

app = FastAPI(title="ArcMusic Custom API Backend")

@app.get("/")
def home():
    return {"status": "ok", "message": "Arc API clone is running smoothly."}

@app.get("/youtube/v2/download")
def download_audio(
    api_key: str = Query(...),
    isVideo: bool = Query(False),
    query: str = Query(...)
):
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'skip_download': True,
        'http_chunk_size': 1048576,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    if not query.startswith(("http://", "https://")):
        if len(query) == 11 and " " not in query:
            url_to_extract = f"https://www.youtube.com/watch?v={query}"
        else:
            url_to_extract = f"ytsearch:{query}"
    else:
        url_to_extract = query

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url_to_extract, download=False)
            
            if 'entries' in info and len(info['entries']) > 0:
                video_data = info['entries'][0]
            else:
                video_data = info
                
            stream_url = video_data.get("url")
            
            if not stream_url:
                return {"success": False, "error": "Could not extract stream URL"}

            # Yeh hai wo exact format jo Go bot dhoond raha hai (Nested "data" object)
            return {
                "success": True,
                "data": {
                    "id": video_data.get("id"),
                    "title": video_data.get("title"),
                    "duration": int(video_data.get("duration", 0)),
                    "thumbnail": video_data.get("thumbnail", ""),
                    "url": stream_url,
                    "download_url": stream_url,  # Go bot isko read karega
                    "job_id": "arc_music_custom_sync" # Backup key agar wo job id mange
                }
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
        
