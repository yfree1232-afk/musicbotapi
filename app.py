from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

API_KEY = os.environ.get("API_KEY", "ARC31f8531e8cd5b87c39c3b1")

@app.route("/youtube/v2/download", methods=["GET"])
def download():
    api_key = request.args.get("api_key")
    if api_key != API_KEY:
        return jsonify({"error": "Invalid API key"}), 401

    query = request.args.get("query", "")
    is_video = request.args.get("isVideo", "false").lower() == "true"

    if not query:
        return jsonify({"error": "query is required"}), 400

    # YouTube ID ya search query
    if len(query) == 11 and " " not in query:
        search_query = f"https://www.youtube.com/watch?v={query}"
    else:
        search_query = f"ytsearch:{query}"

    try:
        if is_video:
            fmt = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        else:
            fmt = "bestaudio/best"

        ydl_opts = {
            "format": fmt,
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "extract_flat": False,
            "extractor_args": {
                "youtube": {
                    "player_client": ["android"],
                }
            },
            "http_headers": {
                "User-Agent": "com.google.android.youtube/17.36.4 (Linux; U; Android 12) gzip"
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)

            # Search result handle karo
            if "entries" in info:
                entries = list(info["entries"])
                if not entries:
                    return jsonify({"error": "No results found"}), 404
                info = entries[0]

            # URL nikalo
            url = None
            if "url" in info:
                url = info["url"]
            elif "formats" in info and info["formats"]:
                for f in reversed(info["formats"]):
                    if f.get("url") and f.get("acodec") != "none":
                        url = f["url"]
                        break
                if not url:
                    url = info["formats"][-1]["url"]

            if not url:
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
