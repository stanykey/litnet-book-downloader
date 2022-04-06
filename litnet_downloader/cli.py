"""CLI application.

auth-token could be obtained from cookie 'litera-frontend'


Usage:
  litnet-downloader <auth-token> <book-url> [--page-delay=<seconds>]
  litnet-downloader -h | --help | --version
"""

from sys import exit
from time import sleep
from typing import Any

from docopt import docopt

from litnet_downloader.book import Book
from litnet_downloader.book_downloader import BookDownloader
from litnet_downloader.version import __version__


def get_option(options: dict[str, Any], key: str, /, *, default: Any = None) -> Any:
    option = options.get(key, default)
    return option if option else default


def get_book(downloader: BookDownloader, /) -> Book:
    while not (book := downloader.get_book()):
        print("book wasn't downloaded, so sleep a bit try again")
        sleep(5)
    return book


def process_book(book: Book, /) -> None:
    with open(f'{book.title}.txt', 'w', encoding='utf-8') as book_file:
        for idx, chapter in enumerate(book.chapters):
            print(f'process {idx + 1} of {len(book.chapters)}')
            print(f'\ttitle: {chapter.title}')

            book_file.write(chapter.title)
            book_file.write('\n\n')

            with open(chapter.location, 'r', encoding='utf-8') as chapter_file:
                content = ''.join(chapter_file.readlines())
                content = content.replace('<p>', '')
                content = content.replace('</p>', '')
                content = content.replace('<br />', '')

            print(f'\tcontent size: {len(content)}')

            book_file.write(content)
            book_file.flush()


def run() -> None:
    arguments = docopt(__doc__, version=__version__)

    downloader = BookDownloader(
        url=arguments['<book-url>'],
        token=arguments['<auth-token>'],
        delay_secs=int(get_option(arguments, '--page-delay', default=1))
    )

    book = get_book(downloader)
    process_book(book)

    answer = input('Delete cached book data? (yes/no) >> ')
    if answer.lower() == 'yes':
        downloader.cleanup()

    input('Press Enter to exit...')


if __name__ == '__main__':
    exit(run())
