from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

API_KEY = "ARC31f8531e8cd5b87c39c3b1"


@app.route("/youtube/v2/download")
def download():

    if request.args.get("api_key") != API_KEY:
        return jsonify({
            "status": "error",
            "message": "Invalid API key"
        })

    query = request.args.get("query")

    if not query:
        return jsonify({
            "status": "error",
            "message": "Query missing"
        })

    try:

        ydl_opts = {
            "quiet": True,
            "nocheckcertificate": True,
            "cookiefile": "cookies.txt",
            "noplaylist": True",

            # IMPORTANT
            "format": "b",

            "extractor_args": {
                "youtube": {
                    "player_client": ["android"]
                }
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            if len(query) == 11 and " " not in query:
                data = ydl.extract_info(
                    f"https://youtube.com/watch?v={query}",
                    download=False
                )
            else:
                result = ydl.extract_info(
                    f"ytsearch1:{query}",
                    download=False
                )

                data = result["entries"][0]

            return jsonify({
                "status": "success",
                "title": data.get("title"),
                "duration": data.get("duration"),
                "thumbnail": data.get("thumbnail"),
                "video_id": data.get("id"),
                "channel": data.get("uploader"),
                "url": data.get("url")
            })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
