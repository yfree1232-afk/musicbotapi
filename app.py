from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

API_KEY = os.environ.get("API_KEY", "ARC31f8531e8cd5b87c39c3b1")


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "message": "Arc Music API Running"
    })


@app.route("/youtube/v2/download", methods=["GET"])
def download():

    api_key = request.args.get("api_key")

    if api_key != API_KEY:
        return jsonify({
            "status": "error",
            "message": "Invalid API key"
        }), 401

    query = request.args.get("query")
    is_video = request.args.get("isVideo", "false").lower() == "true"

    if not query:
        return jsonify({
            "status": "error",
            "message": "Query parameter required"
        }), 400

    try:

        # YouTube URL or Search
        if "youtube.com" in query or "youtu.be" in query:
            search = query
        elif len(query) == 11 and " " not in query:
            search = f"https://www.youtube.com/watch?v={query}"
        else:
            search = f"ytsearch1:{query}"

        # Format selection
        if is_video:
            fmt = "bv*+ba/b"
        else:
            fmt = "bestaudio/best"

        ydl_opts = {
            "format": fmt,
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "cookiefile": "cookies.txt",

            # Better extraction
            "extractor_args": {
                "youtube": {
                    "player_client": ["android"]
                }
            },

            # Faster
            "skip_download": True,

            # Avoid certificate issue
            "nocheckcertificate": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(search, download=False)

            # Search result handling
            if "entries" in info:
                entries = list(info["entries"])

                if not entries:
                    return jsonify({
                        "status": "error",
                        "message": "No results found"
                    }), 404

                info = entries[0]

            url = None

            # Best audio/video URL
            if "formats" in info:

                formats = info["formats"]

                valid_formats = [
                    f for f in formats
                    if f.get("url")
                ]

                if is_video:
                    valid_formats = [
                        f for f in valid_formats
                        if f.get("vcodec") != "none"
                    ]
                else:
                    valid_formats = [
                        f for f in valid_formats
                        if f.get("acodec") != "none"
                    ]

                if valid_formats:
                    url = valid_formats[-1]["url"]

            # fallback
            if not url:
                url = info.get("url")

            if not url:
                return jsonify({
                    "status": "error",
                    "message": "Stream URL not found"
                }), 500

            return jsonify({
                "status": "success",
                "developer": "Aditya",

                "data": {
                    "title": info.get("title"),
                    "video_id": info.get("id"),
                    "duration": info.get("duration"),
                    "thumbnail": info.get("thumbnail"),
                    "channel": info.get("uploader"),
                    "views": info.get("view_count"),
                    "publish_date": info.get("upload_date"),
                    "url": url
                }
            })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
