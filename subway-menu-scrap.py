import bs4
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.error import HTTPError


def dishes_list(link, server=""):
    try:
        url = urlopen(server+link)
    except HTTPError as e:
        return None

    soup1 = BeautifulSoup(url)
    try:
        print("<------------>")
        print(soup1.h1.get_text())
        print("<------------>")
    except AttributeError as e:
        print("Wrong attribute!")

    dishes = soup1.findAll("a", {"class": "sect_title"})
    for dish in dishes:
        try:
            print(dish.get_text())
        except AttributeError as e:
            print("Wrong attribute!")
    return None


def scrap():
    # find web-page by url
    try:
        url = urlopen("https://subway.ru")
    except HTTPError as e:
        return None
    try:
        obj = BeautifulSoup(url.read())
        menu = obj.find("a", {"class": "mainMenu__itemLink"}, text="Наше меню")
        menu = menu.find_next_sibling()

        for category in menu.ul.children:
            if type(category) == bs4.element.Tag:
                dishes_list(category.a.attrs["href"], server="https://subway.ru")

    except AttributeError as e:
        print("Wrong attribute!")


    except AttributeError as e:
        print(e)
        return None


if __name__ == '__main__':
    scrap()


