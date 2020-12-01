import json
import logging
from builtins import super

from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler, WebSocketClosedError

from app.game_manager import InvalidGameError

logger = logging.getLogger("app")


class IndexHandler(RequestHandler):
    def get(self):
        self.redirect('/tic-tac-toe')


class TicTacToeHandler(RequestHandler):
    def get(self):
        self.render("tic_tac_toe.html")


class TicTacToeSocketHandler(WebSocketHandler):

    def initialize(self, game_manager, *args, **kwargs):
        self.game_manager = game_manager
        self.game_id = None
        super().initialize(*args, **kwargs)

    def open(self):
        """Opens a Socket Connection to client"""
        self.send_message(action="open", message="Connected to Game Server")

    def on_message(self, message):
        data = json.loads(message)
        action = data["action"]

        if action == "new":
            # Create a new game id and respond the game id
            self.game_id = self.game_manager.new_game(self)
            self.send_message(action="wait-pair", game_id=self.game_id)
        elif action == "abort":
            self.game_manager.abort_game(self.game_id)
            self.send_message(action="end", game_id=self.game_id, result="A")
            self.send_pair_message(action="end", game_id=self.game_id, result="A")
            self.game_manager.end_game(self.game_id)
        elif action == "join":
            try:
                game_id = int(data["game_id"])
                self.game_manager.join_game(game_id, self)
            except (ValueError, TypeError, InvalidGameError):
                self.send_message(action="error", message=f'Invalid Game Id: {game_id}')
            else:
                self.game_id = game_id
                self.send_message(action="paired", game_id=game_id)
                self.send_pair_message(action="paired", game_id=game_id)
        elif action == 'move':
            player_selection = data.get("player_move")
            player_move = (int(player_selection[0]), int(player_selection[2]))
            if player_move:
                self.game_manager.record_move(self.game_id, player_move, self)
            self.send_message(action="opp-move")
            self.send_pair_message(action="move", opp_move=player_selection)

            print("---------")
            if self.game_manager.has_game_ended(self.game_id):
                game_result = self.game_manager.get_game_result(self.game_id, self)
                self.send_message(action="end", result=game_result)
                opp_result = "L" if game_result == "W" else game_result
                self.send_pair_message(action="end", result=opp_result)
                self.game_manager.end_game(self.game_id)
            print("---------")

    def send_message(self, action="open", **data):
        message = {
            "action": action,
            "data": data
        }
        try:
            self.write_message(json.dumps(message))
        except WebSocketClosedError:
            logger.warning("WS_CLOSED", "Could Not send Message: " + json.dumps(message))
            self.send_pair_message(action="pair-closed")
            self.close()

    def send_pair_message(self, action, **data):
        """Send Message to paired Handler"""
        if not self.game_id:
            return
        try:
            paired_handler = self.game_manager.get_pair(self.game_id, self)
        except InvalidGameError:
            logging.error("Inalid Game: {0}. Cannot send pair msg: {1}".format(self.game_id, data))
        else:
            if paired_handler:
                paired_handler.send_message(action, **data)

    def __str__(self):
        return str(self.__dict__)
