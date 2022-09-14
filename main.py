import sqlalchemy as db
import requests
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
from decimal import Decimal


def create_table():
    metadata = db.MetaData()

    table = db.Table('ads', metadata,
                     db.Column('image', db.Text()),
                     db.Column('title', db.String(255)),
                     db.Column('date_posted', db.Date()),
                     db.Column('city', db.String(255)),
                     db.Column('beds', db.String(20)),
                     db.Column('description', db.Text()),
                     db.Column('price', db.DECIMAL()),
                     db.Column('currency', db.String(3)),
                     )

    metadata.create_all(engine)
    return table


def insert_many(values_list):
    query = db.insert(table)
    connection.execute(query, values_list)


def get_url(page):
    return f'https://www.kijiji.ca/b-apartments-condos/city-of-toronto/page-{page}/c37l1700273?ad=offering'


def parse_page(page):
    r = requests.get(get_url(page))

    soup = BeautifulSoup(r.content, 'html.parser')
    items = soup.select('div div.clearfix')[1:]

    data = []
    for i in items:
        image_url = i.select_one('.image').select_one('img')['src']
        title = i.select_one('.title a').text.strip()
        location = i.select_one('.location')
        date_created = location.select_one('.date-posted').text.strip()
        try:
            temp = datetime.strptime(date_created, "%d/%m/%Y")
            if temp:
                date_created = temp.strftime("%d-%m-%Y")
        except ValueError:
            if date_created.endswith('ago'):
                date_created = date.today().strftime("%d-%m-%Y")
            elif 'Yesterday' == date_created:
                date_created = (date.today() - timedelta(days=1)).strftime("%d-%m-%Y")
        city = location.select('.location span')[0].text.strip()
        beds = i.select_one('.bedrooms').text.split(":")[1].strip()
        description = i.select_one('.description').text.strip()
        price = i.select_one('.price').text.strip()
        currency = "USD"
        if price == "Please Contact":
            price = Decimal(-1.0)
        else:
            if price[0] == "€":
                currency = "EUR"
            elif price[0] == "¥":
                currency = "YEN"
            price = price[1:]
            price = Decimal(price.replace(',', ''))
        data.append({'image': image_url,
                    'title': title,
                    'date_posted': date_created,
                    'city': city,
                    'beds': beds,
                    'description': description,
                    'price': price,
                    'currency': currency})
    return r.url, data


def parse():
    page = 1
    while True:
        data = parse_page(page)
        insert_many(data[1])
        if 'page-' in data[0] and data[0] != get_url(page):
            break
        page += 1
        print(f'Parsing page: {page}')


if __name__ == '__main__':
    DB_NAME = 'postgres'
    DB_USER = 'postgres'
    DB_PASSWORD = 'password'

    db_string = f'postgresql://{DB_USER}:{DB_PASSWORD}@localhost:5433/{DB_NAME}'
    engine = db.create_engine(db_string)
    connection = engine.connect()
    connection.execute("SET DateStyle='DMY'")
    table = create_table()
    parse()
