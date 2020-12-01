import logging

import tornado.web
from tornado.options import options
from app.game_manager import TicTacToeGameManager
from app.handlers import IndexHandler, TicTacToeHandler, TicTacToeSocketHandler
from app.config import settings


def main():
    options.parse_command_line()

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename='app.log',
        filemode='w',
    )
    app_logger = logging.getLogger('app')

    tic_tac_toe_game_manager = TicTacToeGameManager()

    urls = [
        (r"/$", IndexHandler),
        (r"/tic-tac-toe$", TicTacToeHandler),
        (r"/tic-tac-toe/ws$", TicTacToeSocketHandler, dict(game_manager=tic_tac_toe_game_manager))
    ]

    application = tornado.web.Application(
        urls,
        debug=options.debug,
        autoreload=options.debug,
        **settings
    )

    app_logger.info(f'Starting App on Port: {options.port} with Debug Mode: {options.debug}')
    application.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
