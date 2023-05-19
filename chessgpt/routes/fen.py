from flask import jsonify, request
from chessgpt.authentication.authentication import check_auth

from chessgpt.utils.openai import get_conversation_id_hash


def get_fen_routes(app):
    @app.route("/api/fen", methods=["GET"])
    @check_auth
    def get_fen():
        conversation_id = request.headers.get("Openai-Conversation-Id")
        conversation_id_hash = get_conversation_id_hash(conversation_id)
        game_state = app.database.load_game_state(conversation_id_hash)

        if not game_state:
            app.logger.error(f"No game found for conversation ID: {conversation_id}")
            return jsonify({"success": False, "message": "No game found"}), 404
        return jsonify({"FEN": game_state.board.fen()})
