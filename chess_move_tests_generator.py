import argparse
import chess
import json
import sys

def get_move_type(board, move):
    """
    Determine the type of a chess move.
    
    Args:
        board: A chess.Board object
        move: A chess.Move object
    
    Returns:
        str: Type of the move - one of the following:
            "KingSideCastle", "QueenSideCastle", "EnPassant", "PromotionCapture", 
            "Promotion", "Capture", "Basic"
    """
    # Check for castling
    if board.is_kingside_castling(move):
        return "KingSideCastle"
    elif board.is_queenside_castling(move):
        return "QueenSideCastle"
    
    # Check for en passant
    if board.is_en_passant(move):
        return "EnPassant"
    
    # Check for promotion
    if move.promotion is not None:
        # Check if it's also a capture
        if board.is_capture(move):
            return "PromotionCapture"
        else:
            return "Promotion"
    
    # Check for regular capture
    if board.is_capture(move):
        return "Capture"
    
    # If none of the above, it's a basic move
    return "Basic"

def add_test_data(test):
    """
    Adds test data for a given chess position by generating all legal moves and their associated information.

    This function analyzes a chess position specified by a FEN string and generates detailed information
    about each legal move possible from that position. For each move, it captures:
    - Basic move information (from square, to square, moving piece)
    - Special move properties (captures, promotions)
    - Move type (normal, castling, en passant)
    - Position representation after the move (in FEN format)
    - Move notation in different formats (UCI, SAN, LAN)

    Args:
        test (dict): A dictionary containing at least a 'fen' key with a valid FEN string representing
                    the chess position to analyze.

    Returns:
        None. The function modifies the input dictionary by adding a 'moves' key containing a list
        of dictionaries, each representing a legal move and its associated information.

    Example:
        test = {
            'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        }
        add_test_data(test)
        # test now contains a 'moves' key with all legal moves from the starting position
    """
    board = chess.Board()
    board.set_fen(test['fen'])
    moves = []
    for move in board.legal_moves:
        from_square = chess.square_name(move.from_square)
        to_square = chess.square_name(move.to_square)
        piece = board.piece_at(move.from_square).symbol()

        if move.promotion:
            promotion = chess.piece_symbol(move.promotion)
            promotion = promotion.upper() if board.turn == chess.WHITE else promotion.lower()
        else:
            promotion = None

        capture = board.piece_at(move.to_square)
        capture = capture.symbol() if capture else None
        if board.is_en_passant(move):
            capture = 'p' if board.turn == chess.WHITE else 'P'

        move_type = get_move_type(board, move)

        board.push(move)
        fen = board.fen()
        board.pop()

        moves.append({
            'move': {
                'from': from_square,
                'to': to_square,
                'piece': piece,
                'capture': capture,
                'promotion': promotion,
                'type': move_type
            },
            'uci': board.uci(move),
            'san': board.san(move),
            'lan': board.lan(move),
            'fen': fen
        })
    test['moves'] = moves

def get_args():
    """Parse command line arguments for the chess move test generator.

    This function sets up and processes command line arguments for generating chess move test data. 
    It handles input/output file paths and output format options.

    Returns:
        argparse.Namespace: Parsed command line arguments containing:
            - input (str): Path to input file with test definitions
            - output (str): Path where output test data will be written
            - minify (bool): Whether to minify the output JSON file
    """
    arg_parser = argparse.ArgumentParser(description='Generate test data for chess move generators')

    arg_parser.add_argument('input', type=str, help='Input file containing tests definitions')
    arg_parser.add_argument('output', type=str, help='Output file containing tests with computed test data')
    arg_parser.add_argument('--minify', '-m', action='store_true', help='Minify the output JSON file')

    return arg_parser.parse_args()

def read_tests_definitions(input):
    """
    Reads chess test definitions from a JSON file.

    Args:
        input (str): Path to the input JSON file containing test definitions.

    Returns:
        dict: The parsed JSON data containing the test definitions.

    Raises:
        JSONDecodeError: If the input file contains invalid JSON.
        FileNotFoundError: If the input file does not exist.
        PermissionError: If the program lacks permission to read the input file.
    """
    with open(input, 'r') as input_file:
        tests = json.load(input_file)

    return tests

def write_tests_data(output, minify, tests):
    """
    Writes test data to a JSON file.

    Args:
        output (str): Path to the output JSON file.
        minify (bool): If True, writes minified JSON without indentation.
                      If False, writes pretty-printed JSON with indentation.
        tests (dict): Test data to write to the file.

    Returns:
        None

    Raises:
        IOError: If there is an error writing to the output file.
    """
    with open(output, 'w') as output_file:
        if minify:
            # Write minified JSON (no indentation)
            json.dump(tests, output_file, separators=(',', ':'))
        else:
            # Write pretty-printed JSON (with indentation)
            json.dump(tests, output_file, indent=4)

def main():
    args = get_args()
    tests = read_tests_definitions(args.input)

    for test in tests:
        add_test_data(test)

    write_tests_data(args.output, args.minify, tests)


if __name__ == '__main__':
    main()