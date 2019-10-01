import argparse
import parsing.fb2 as fb2
from converting.epub import book_to_epub


def main():
    parser = argparse.ArgumentParser('Convert FB2 book to EPUB')
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Input FB2 file')
    parser.add_argument(
        '-o', '--output',
        default='output.epub',
        help='Output EPUB file')

    args = parser.parse_args()

    book = fb2.read_fb2(args.input)
    book_to_epub(book, args.output)


if __name__ == "__main__":
    main()
