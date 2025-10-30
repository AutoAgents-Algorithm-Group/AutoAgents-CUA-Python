import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from DrissionPage import ChromiumPage, ChromiumOptions
from src.autoagents_cua.browser import PageExtractor

if __name__ == "__main__":
    options = ChromiumOptions()
    options.auto_port()
    page = ChromiumPage(addr_or_opts=options)

    page.get('https://en.wikipedia.org/')

    page.wait(2)
    extractor = PageExtractor(page)

    # #extractor.extract_elements(save_to_file="google_elements.txt")
    extractor.extract_elements(save_to_file="wiki_elements.txt")
    page.wait(10)
    # extractor.print_elements()

    # extractor.print_grouped_selectors()

    # extractor.get_elements_by_tag('input')

    # extractor.get_selector_list()

    # extractor.get_elements()

    # extractor.clear()

    page.quit()
