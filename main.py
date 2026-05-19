from fastapi import FastAPI, HTTPException, Query
import yt_dlp

app = FastAPI(title="ArcMusic Custom API Backend")

@app.get("/")
def home():
    return {"status": "ok", "message": "Arc API clone is running smoothly."}

# Bot is path par request bhej raha hai
@app.get("/youtube/v2/download")
def download_audio(
    api_key: str = Query(...),
    isVideo: bool = Query(False),
    query: str = Query(...)
):
    """
    Go bot se aane wali requests ko handle karega aur direct streaming/download URL dega.
    """
    # Aap chahein toh yahan custom API key validation bhi laga sakte hain, abhi sabhi ko allow kiya hai.
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'skip_download': True,
        # Khas taur par Telegram bots ke liye cookie ya user-agent errors se bachne ke liye
        'http_chunk_size': 1048576, 
    }
    
    # Agar query sirf ek video ID hai ya text hai, toh use handle karein
    if not query.startswith(("http://", "https://")):
        # Agar sirf ID hai (jaise error me '8qX0VIVxivU' hai)
        if len(query) == 11 and " " not in query:
            url_to_extract = f"https://www.youtube.com/watch?v={query}"
        else:
            url_to_extract = f"ytsearch:{query}"
    else:
        url_to_extract = query

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url_to_extract, download=False)
            
            if 'entries' in info:
                video_data = info['entries'][0]
            else:
                video_data = info
                
            stream_url = video_data.get("url")
            
            # Go bot ko response me direct URL ya JSON metadata chahiye hota hai. 
            # Hum ek standard stream response object bhej rahe hain:
            return {
                "status": "success",
                "title": video_data.get("title"),
                "id": video_data.get("id"),
                "duration": video_data.get("duration"),
                "url": stream_url,  # Direct audio stream link
                "download_url": stream_url
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Custom API Error: {str(e)}")
