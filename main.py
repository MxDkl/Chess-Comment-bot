import asyncio
import os
import re
import asyncpraw
from asyncpraw.models import Submission
import chess
import chess.engine


COMMENT = """Wanna play a game?
Make your move using algebraic notation.
---
The last move was made by: {user}.
This is the current position:
>**White to play**: [chess.com](https://chess.com/analysis?fen={fen}) \
[lichess.org](https://lichess.org/analysis/standard/{fen})
**Light mode:**
{unicode}
**Dark mode:**
{unicode_ic}"""

def format_board_unicode(unicode: str) -> str:
	# Split into ranks
	unicode = unicode.splitlines()
	# Split ranks into files
	unicode = [r.split(" ") for r in unicode]
	# Replace "⭘"s with empty strings

	for r in range(8):
		for f in range(8):
			if unicode[r][f] == "⭘":
				unicode[r][f] = ""
		unicode[r].append(str(8 - r))
	unicode.insert(0, "||||||||".split("|"), )
	unicode.insert(1, ":-|:-|:-|:-|:-|:-|:-|:-|:-".split("|"))
	unicode.append("a|b|c|d|e|f|g|h|".split("|"))

	return "\n".join(["|" + "|".join(r) + "|" for r in unicode])

async def play(submission: Submission, board: chess.Board) -> None:
	transport, stockfish = await chess.engine.popen_uci("/home/max/chessbot/Stockfish/src/stockfish")
	
	last_comment = submission.created_utc
	while not board.is_game_over():
		await submission.load()
		for comment in await submission.comments():
			if comment.created_utc > last_comment:
				last_comment = comment.created_utc
				print(comment.body)

				try:
					board.push_san(comment.body)
				except ValueError:
					print(f"Illegal move: {comment.body} at {board.fen()}")
					continue

				result = await stockfish.play(board, chess.engine.Limit(depth=18))
				board.push(result.move)

				comment_md = COMMENT.format(
					unicode=format_board_unicode(board.unicode()), 
					unicode_ic=format_board_unicode(board.unicode(invert_color=True)),
					turn=chess.COLOR_NAMES[board.turn].capitalize(),
					user=comment.author,
					fen=board.fen()
				)
				await submission.edit(comment_md)
				print("Edited")
		
		print("i")
		await asyncio.sleep(3*60)
	print("Game over")

async def main() -> None:
	reddit = asyncpraw.Reddit(
		client_id="",
		client_secret="",
		password="",
		user_agent="",
		username=""
	)
	reddit.validate_on_submit = True

	anarchychess = await reddit.subreddit('anarchychess')


	#async for submission in anarchychess.stream.submissions(skip_existing=True):
	board = chess.Board()
	
	comment_md = COMMENT.format(
		unicode=format_board_unicode(board.unicode()), 
		unicode_ic=format_board_unicode(board.unicode(invert_color=True)),
		turn=chess.COLOR_NAMES[board.turn].capitalize(), 
		user="Nobody",
		fen=board.fen()
	)
	submission = await anarchychess.submit("I'm a bot that plays chess. Comment yout move", comment_md)
	print("posted")
	await play(submission, board)

if __name__ == "__main__":
	asyncio.run(main())
