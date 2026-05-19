from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

API_KEY = os.environ.get(
    "API_KEY",
    "ARC31f8531e8cd5b87c39c3b1"
)


@app.route("/")
def home():
    return jsonify({
        "status": "online"
    })


@app.route("/youtube/v2/download")
def download():

    api_key = request.args.get("api_key")

    if api_key != API_KEY:
        return jsonify({
            "status": "error",
            "message": "Invalid API key"
        }), 401

    query = request.args.get("query")

    if not query:
        return jsonify({
            "status": "error",
            "message": "Query missing"
        }), 400

    try:

        ydl_opts = {
            "quiet": True,
            "nocheckcertificate": True,
            "cookiefile": "cookies.txt",
            "noplaylist": True,

            # MOST STABLE
            "format": "b",

            "extractor_args": {
                "youtube": {
                    "player_client": ["android"]
                }
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            if len(query) == 11 and " " not in query:
                info = ydl.extract_info(
                    f"https://youtube.com/watch?v={query}",
                    download=False
                )
            else:
                result = ydl.extract_info(
                    f"ytsearch1:{query}",
                    download=False
                )

                info = result["entries"][0]

            return jsonify({
                "status": "success",
                "title": info.get("title"),
                "duration": info.get("duration"),
                "thumbnail": info.get("thumbnail"),
                "video_id": info.get("id"),
                "channel": info.get("uploader"),
                "url": info.get("url")
            })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
