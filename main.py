import asyncio
import os
import asyncpraw
from asyncpraw.models import Comment
import chess
import chess.engine


COMMENT = """Wanna play a game?\n
Make your move using algebraic notation.\n
The last move was made by: {user}.\n
This is the current position (White to play):\n
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
	
	comment_id = comment.id
	async for reply in anarchychess.stream.comments(skip_existing=True):
		print(reply.body)
		if reply.parent_id == comment_id:
			try:
				board.push_san(comment.body)
			except:
				continue
			move = await stockfish.play(board, chess.engine.Limit(time=0.1))
			board.push(move)
			commend_md = COMMENT.format(ascii=str(board), fen=board.fen(), user=reply.author)
			await comment.edit(commend_md)
			print("Edited")

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
		board = chess.Board("rnbq1bnr/ppppkppp/8/4p3/4P3/8/PPPPKPPP/RNBQ1BNR w - - 2 3")
		comment_md = COMMENT.format(ascii=" ", fen=board.fen(), user="Nobody")
		comment = await submission.reply(comment_md)
		print("posted")
		await play(comment, board)

if __name__ == "__main__":
	asyncio.run(main())