import discord
from discord.ext import commands
import chess
from PIL import Image, ImageDraw, ImageFont
import os

# Initialize the bot and enable required intents
intents = discord.Intents.default()
intents.message_content = True  # Allows the bot to access message content
intents.members = True  # Allows the bot to access member data

bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionary to store game states for multiple players
games = {}

# Function to generate a simple chess board image using Pillow
def generate_board_image(board):
    square_size = 60
    board_img = Image.new("RGB", (square_size * 8, square_size * 8), "white")
    draw = ImageDraw.Draw(board_img)

    # Colors for the chessboard
    colors = ["#f0d9b5", "#b58863"]  # Light and dark squares

    for rank in range(8):
        for file in range(8):
            color = colors[(rank + file) % 2]
            draw.rectangle([file * square_size, rank * square_size, 
                            (file + 1) * square_size, (rank + 1) * square_size], fill=color)

    # Load default font for text if needed
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()

    # Place pieces on the board
    for square, piece in board.piece_map().items():
        x = (chess.square_file(square)) * square_size + square_size // 3
        y = (7 - chess.square_rank(square)) * square_size + square_size // 4
        draw.text((x, y), str(piece), font=font, fill="black")

    # Save the image
    board_img.save('chess_board.png')

# Event when bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Command to show chess instructions
@bot.command()
async def chess(ctx):
    instructions = (
        "Welcome to the Chess Bot!\n"
        "Here are the commands you can use:\n\n"
        "**1. Start a Game**:\n"
        "`!start_game @opponent`\n"
        "This command starts a new chess game with the mentioned opponent.\n\n"
        "**2. Make a Move**:\n"
        "`!move @opponent <move>`\n"
        "Use this command to make a move in UCI format. For example, `!move @opponent e2e4`.\n\n"
        "**Move Notation**:\n"
        "- The format for moves is `e2e4`, which means moving from e2 to e4.\n"
        "- Other examples: `g1f3`, `d7d5`, etc.\n\n"
        "Have fun playing chess!"
    )
    await ctx.send(instructions)

# Command to start a new game
@bot.command()
async def start_game(ctx, opponent: discord.Member = None):
    if opponent is None:
        await ctx.send("You need to mention an opponent!")
        return

    # Debug: Show the command is being received
    print(f"Game started by {ctx.author} against {opponent}")

    game_id = f"{ctx.author.id}_{opponent.id}"
    if game_id in games:
        await ctx.send(f"A game between {ctx.author} and {opponent} is already in progress!")
        return

    # Initialize a new chess board and generate the image
    games[game_id] = chess.Board()
    generate_board_image(games[game_id])
    await ctx.send(f"Game started between {ctx.author} and {opponent}!", file=discord.File('chess_board.png'))

# Command to make a move manually
@bot.command()
async def move(ctx, opponent: discord.Member, move: str):
    game_id = f"{ctx.author.id}_{opponent.id}"
    
    # Debugging output
    print(f"Move command received from {ctx.author} to move {move} against {opponent}")
    
    if game_id not in games:
        await ctx.send("No game in progress!")
        return
    
    board = games[game_id]
    
    try:
        chess_move = chess.Move.from_uci(move)
        if chess_move in board.legal_moves:
            board.push(chess_move)
            generate_board_image(board)  # Update the board image after the move
            await ctx.send(f"{ctx.author.mention} moved {move}.", file=discord.File('chess_board.png'))
        else:
            await ctx.send("Illegal move!")
    except Exception as e:
        await ctx.send(f"Error processing move: {e}")

# Run the bot with your token (replace with your own bot token or use Replit Secrets)
bot.run(os.getenv('DISCORD_TOKEN'))

