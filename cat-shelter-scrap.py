import requests
import bs4
import os
import time
import json
import re


def download_page(url, file_name):
    """
    Find and saves html page as "file_name" file.
    :param url: url address of html page
    :param file_name: relative path to the file
    :return:
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"
    }
    try:
        req = requests.get(url, headers)
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(req.text)
    except requests.exceptions.RequestException:
        print("Error - couldn't find the page and download it!")


class CatPage(bs4.BeautifulSoup):
    """
    Class CatPage inherits from BeautifulSoup and
    includes methods to find cat's specific info like name, gender,
    full description, photos and phone numbers at their page
    """
    def get_name(self):
        # finds cat's name
        return self.find(class_="pitomec title").text

    def get_gender(self):
        # finds cat's gender
        return self.find(class_="gender").text

    def get_descript(self):
        # finds cat's short description
        return self.find(class_="fadeInUp wow").text

    def get_full_descript(self):
        # finds cat's full description
        return self.find(class_="cs12").text[1:]

    def get_phone(self):
        # find phone numbers to take the cat
        tag = self.find(class_="circle fa fa-phone")    # empty tag <i class="circle fa fa-phone">
        string = tag.parent.text
        phone_pattern = re.compile("\+ ?7 [0-9]{3} [0-9]{3} [0-9]{2} [0-9]{2}")
        phone = phone_pattern.findall(string)
        return phone

    def get_images(self):
        # find refs to cat's images
        images_ref = []
        try:
            # finds the "main" image
            main_img = self.find(class_="img-wrap").a["href"]
            images_ref.append(main_img)
        except KeyError:
            print("Error - couldn't find main photo!")

        # find and iterate over other pictures
        images = self.find(class_="foto").find_all("a")
        for img in images:
            ref = img.get("href")
            if ref is not None:
                images_ref.append(ref)

        return images_ref


def get_soup(file_name, soup_type="CatPage"):
    """
    Converts html page to the BeautifulSoup object.
    :param file_name: relative path to the html file
    :param soup_type: return bs4.BeautifulSoup object if "bs4" ot CatPage object in "CatPage"
    :return: BeautifulSoup object
    """
    with open(file_name, encoding="utf-8") as file:
        src = file.read()
    try:
        if soup_type == "CatPage":
            soup = CatPage(src, "lxml")
        else:
            soup = bs4.BeautifulSoup(src, "lxml")
    except Exception as e:
        print("Error - couldn't read the file / transform to bs")
        print("Exception is:", e)
    return soup


def delete_file(file_name):
    if os.path.isfile(file_name):
        os.remove(file_name)
    else:
        print("File doesn't exist!")
    return


class Data:
    """
    Class to easier work with data and different formats
    """
    db_list = []

    def dump_into_json(self, json_file):
        # write db_list into json file
        with open(json_file, "a", encoding="utf-8") as file:
            json.dump(self.db_list, file, indent=4, ensure_ascii=False)

    def append_cat(self, cat):
        # append new cat to db_list
        self.db_list.append(cat.transform_into_dict())


class Cat:
    """
    Class Cat contains all needed information about cat:
    name, gender, short and full descriptions, images and phone to take the cat
    """
    def __init__(self, id_name, name, gender, descript, full_descript, phone, images):
        # classic initialization
        self.id_name = id_name
        self.name = name
        self.gender = gender
        self.descript = descript
        self.full_descript = full_descript
        self.phone = phone
        self.images = images

    @classmethod
    def parse_cat_page(cls, base_url, url, delete_src=True):
        # create Cat object from url of cat's own page
        full_url = base_url + url
        id_name = url[8:]    # url looks like /koshki/name, "/koshki/" = url[:8]
        file_name = f"data/page_{id_name}"
        try:
            download_page(full_url, file_name)
            cat_page = get_soup(file_name)
            if delete_src:
                delete_file(file_name)
        except Exception as e:
            print("Error - Couldn't create CatPage object!")
            if delete_src:
                delete_file(file_name)
            return None

        name = cat_page.get_name()
        gender = cat_page.get_gender()
        descript = cat_page.get_descript()
        full_descript = cat_page.get_full_descript()
        phone = cat_page.get_phone()
        images = cat_page.get_images()

        return cls(id_name, name, gender, descript, full_descript, phone, images)

    def transform_into_dict(self):
        data = {
            "id_name": self.id_name,
            "name": self.name,
            "gender": self.gender,
            "short description": self.descript,
            "full description": self.full_descript,
            "phone": self.phone,
            "image": self.images
        }
        return data

    def __str__(self):
        string = (
            f"Cat object: {self.id_name}\n"
            f"name: {self.name}, gender: {self.gender},\n"
            f"short description: {self.descript}\n"
            f"full description: {self.full_descript}\n"
            f"phone numbers: {self.phone}\n"
            f"images ref:\n"
        )
        for img in self.images:
            string += img + '\n'
        return string


def get_all_cats(base_url, json_db, cat_db, delete_src=True):
    """
    Save cat's info into json file
    :param base_url: domain url of pets shelter website
    :param soup: BeautifulSoup object (html page of pets shelter)
    :param json_db: json file to save cats info
    :return:
    """
    for page_count in range(7):
        time.sleep(3)
        full_url = base_url + f"/koshki/?page={page_count}"
        filename = f"data/page{page_count}"

        # load page and create soup
        try:
            download_page(full_url, filename)
            soup = get_soup(filename, "bs4")
            if delete_src:
                delete_file(filename)

        except Exception as e:
            print("Error - Couldn't download page and create soup object!")
            print("Exception:", e)
            if delete_src:
                delete_file(filename)

        cat_counter = 0
        cat_cards = soup.find_all(class_="card box")
        for cat in cat_cards:
            cat_counter += 1
            try:
                cat_url = cat.a["href"]
            except KeyError:
                print("Error - couldn't find ref to cat's page!")
                continue

            # parse info about cat and save it
            try:
                cat = Cat.parse_cat_page(base_url, cat_url)
                cat_db.append_cat(cat)
                print(f"cat {cat.id_name} was saved :)")

            except Exception as e:
                print("Error - couldn't find information")
                print("Exception:", e)

            time.sleep(6)
    cat_db.dump_into_json(json_db)


def main():
    base_url = f"https://izpriuta.ru"
    json_db = f"database.json"
    cat_db = Data()
    get_all_cats(base_url, json_db, cat_db)


if __name__ == "__main__":
    main()

