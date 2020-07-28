from bs4 import BeautifulSoup
import re
import urllib.request
import sys

STORY_TEMPLATE = "https://www.fanfiction.net/s/{0}/{1}/"
USERNAME_RE = "^\/u\/\d+\/[a-zA-Z]+"
TITLE_CHAPTER_RE = "Chapter\s\d+.+fanfic\s\|\sFanFiction"
TITLE_ONESHOT_RE = ",\sa\s.+\sfanfic\s\|\sFanFiction"


def main(story_id):
    story = []

    story_info = get_story_info(story_id)

    if story_info['exists']:
        story.append(story_info['text'])

        if (story_info['length']) > 1:
            for i in range(2, story_info['length'] + 1):
                story.append(get_chapter(story_id, i))

        print(story_info['title'])
        print(story_info['author'])
        print("\n")
        for chap in story:
            print(chap)
            print("\n")


def get_story_info(story_id):
    story_info = {}

    with urllib.request.urlopen(STORY_TEMPLATE.format(story_id, 1)) as response:

        if response.getcode() == 200:
            html = response.read()
            soup = BeautifulSoup(html, "html.parser")

            story_text = soup.find(id="storytext")

            if story_text is not None:

                for tag in story_text.find_all():
                    for attribute in ["class", "id", "name", "style"]:
                        del tag[attribute]

                story_info['text'] = str(story_text)
                story_info['exists'] = True

                chap_select = soup.find(id="chap_select")

                if chap_select == None:
                    story_info['length'] = 1
                else:
                    story_info['length'] = len(chap_select.contents[0].contents)

                story_info['author'] = soup.find(href=re.compile(USERNAME_RE)).get_text()

                title = soup.title.get_text()

                if story_info['length'] == 1:
                    title_re = re.compile(TITLE_ONESHOT_RE)
                else:
                    title_re = re.compile(TITLE_CHAPTER_RE)

                match = title_re.search(title)

                story_info['title'] = title[:match.start()].strip()

            else:
                story_info['exists'] = False

        else:
            print("Error connecting to fanfiction.net")
            story_info['exists'] = False

    return story_info


def get_chapter(story_id, chapter):
    story_text = ""

    with urllib.request.urlopen(STORY_TEMPLATE.format(story_id, chapter)) as response:
        if response.getcode() == 200:
            html = response.read()
            soup = BeautifulSoup(html, "html.parser")

            story_node = soup.find(id="storytext")

            for tag in story_node.find_all():
                for attribute in ["class", "id", "name", "style"]:
                    del tag[attribute]

            story_text = str(story_node)

    return story_text



main(sys.argv[1])