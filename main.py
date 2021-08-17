import asyncio
import os
import asyncpraw
from asyncpraw.models import Comment, util
import chess
import chess.engine


COMMENT = """Wanna play a game?

Make your move using algebraic notation.

The last move was made by: {user}.

This is the current position (White to play):

{ascii}

[chess.com](https://chess.com/analysis?fen={fen}) [lichess.org](https://lichess.org/analysis/standard/{fen})"""


async def play(comment: Comment, board: chess.Board) -> None:
	reddit = asyncpraw.Reddit(
		client_id="",
		client_secret="",
		password="",
		user_agent="",
		username=""
	)
	anarchychess = await reddit.subreddit('anarchychess')

	transport, stockfish = await chess.engine.popen_uci("/home/max/chessbot/Stockfish/src/stockfish")
	
	async for reply in util.stream_generator(reddit.inbox.comment_replies):
	# async for reply in anarchychess.stream.comments(skip_existing=True):
		print(reply.body)
		print(reply.parent_id, comment.id)
		if reply.parent_id == comment.id:
			try:
				board.push_san(comment.body)
			except:
				continue
			move = await stockfish.play(board, chess.engine.Limit(time=0.1))
			board.push(move)

			commend_md = COMMENT.format(ascii=str(board), fen=board.fen(), user=reply.author)
			await comment.edit(commend_md)
			print("Edited")

			if (board.is_game_over()):
				break
	print("Game over")

async def main() -> None:
	reddit = asyncpraw.Reddit(
		client_id="",
		client_secret="",
		password="",
		user_agent="",
		username=""
	)
	anarchychess = await reddit.subreddit('anarchychess')
	#async for submission in anarchychess.stream.submissions(skip_existing=True):
	for x in range(1):
		submission = await reddit.submission(id="p5g2wb")
		board = chess.Board() # "rnbq1bnr/ppppkppp/8/4p3/4P3/8/PPPPKPPP/RNBQ1BNR w - - 2 3"

		comment_md = COMMENT.format(ascii=str(board), fen=board.fen(), user="Nobody")
		comment = await submission.reply(comment_md)
		print("posted")
		await play(comment, board)

if __name__ == "__main__":
	asyncio.run(main())