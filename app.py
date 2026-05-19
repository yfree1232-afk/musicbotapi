from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

API_KEY = "ARC31f8531e8cd5b87c39c3b1"


@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "developer": "Aditya"
    })


@app.route("/youtube/v2/download")
def download():

    api_key = request.args.get("api_key", "").strip()

    if api_key != API_KEY:
        return jsonify({
            "status": "error",
            "message": "Invalid API key"
        }), 401

    query = request.args.get("query", "").strip()

    if not query:
        return jsonify({
            "status": "error",
            "message": "Query missing"
        }), 400

    try:

        # URL or Search
        if "youtube.com" in query or "youtu.be" in query:
            search = query

        elif len(query) == 11 and " " not in query:
            search = f"https://youtube.com/watch?v={query}"

        else:
            search = f"ytsearch1:{query}"

        ydl_opts = {

            # IMPORTANT
            "format": "18/b",

            "quiet": True,
            "no_warnings": True,
            "nocheckcertificate": True,
            "noplaylist": True,

            # Cookies
            "cookiefile": "cookies.txt",

            # Faster
            "skip_download": True,

            # Stable Client
            "extractor_args": {
                "youtube": {
                    "player_client": ["android"]
                }
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(search, download=False)

            # Search results
            if "entries" in info:
                entries = list(info["entries"])

                if not entries:
                    return jsonify({
                        "status": "error",
                        "message": "No results found"
                    }), 404

                info = entries[0]

            url = info.get("url")

            # Fallback
            if not url and "formats" in info:

                for f in info["formats"]:

                    if f.get("url"):
                        url = f["url"]
                        break

            if not url:
                return jsonify({
                    "status": "error",
                    "message": "No stream url found"
                }), 500

            return jsonify({
                "status": "success",

                "data": {
                    "title": info.get("title"),
                    "video_id": info.get("id"),
                    "duration": info.get("duration"),
                    "thumbnail": info.get("thumbnail"),
                    "channel": info.get("uploader"),
                    "views": info.get("view_count"),
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

    app.run(
        host="0.0.0.0",
        port=port
        )
