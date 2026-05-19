from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

# Simple API key check (set this in Heroku env vars)
API_KEY = os.environ.get("API_KEY", "myapikey123")

@app.route("/youtube/v2/download", methods=["GET"])
def download():
    # Check API key
    api_key = request.args.get("api_key")
    if api_key != API_KEY:
        return jsonify({"error": "Invalid API key"}), 401

    query = request.args.get("query", "")
    is_video = request.args.get("isVideo", "false").lower() == "true"

    if not query:
        return jsonify({"error": "query is required"}), 400

    # If it looks like a YouTube ID, prefix with URL
    if len(query) == 11 and " " not in query:
        search_query = f"https://www.youtube.com/watch?v={query}"
    else:
        search_query = f"ytsearch1:{query}"

    try:
        if is_video:
            fmt = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        else:
            fmt = "bestaudio[ext=m4a]/bestaudio/best"

        ydl_opts = {
    "format": fmt,
    "quiet": True,
    "no_warnings": True,
    "noplaylist": True,
    "extractor_args": {
        "youtube": {
            "player_client": ["android", "web"],
        }
    },
    "http_headers": {
        "User-Agent": "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36"
    }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)

            # Handle search result
            if "entries" in info:
                info = info["entries"][0]

            # Get the direct URL
            if "url" in info:
                url = info["url"]
            elif "formats" in info:
                formats = info["formats"]
                # Pick best audio format
                audio_formats = [f for f in formats if f.get("acodec") != "none" and f.get("url")]
                if audio_formats:
                    url = audio_formats[-1]["url"]
                else:
                    url = formats[-1]["url"]
            else:
                return jsonify({"error": "Could not extract URL"}), 500

            return jsonify({
                "status": "success",
                "title": info.get("title", "Unknown"),
                "duration": info.get("duration", 0),
                "thumbnail": info.get("thumbnail", ""),
                "url": url,
                "video_id": info.get("id", ""),
                "channel": info.get("uploader", ""),
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "ok", "message": "Arc Music API is running!"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
