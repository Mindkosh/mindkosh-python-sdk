from flask import Flask, request, jsonify

PORT = 5000
app = Flask(__name__)


@app.route("/mindkosh", methods=["POST"])
def mindkosh():
    try:
        return jsonify(request.json), 200
    except Exception as e:
        return jsonify({
            "status": "failed",
            "details": str(e)
        }), 500

if __name__ == "__main__":
    app.run(port=PORT,debug=True)
