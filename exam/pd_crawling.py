import pandas as pd

url = 'https://freemeteo.vn/thoi-tiet/ngoc-ha/history/daily-history/?gid=1572463&station=11376&date={}-{:02d}-{:02d}&language=vietnamese&country=vietnam'
tables = pd.read_html(url)

print(tables)

# tables[0].query("Tên == 'Hà Nội'")
print(tables[0].query("Tên == 'Hà Nội'"))

# resp = requests.get(url)
# soup = BeautifulSoup(resp.text)
# table_list = soup.find('div', {'class': 'table-list'})
#
# names, links = [], []
#
# for city in table_list.find_all('a'):
#     names.append(city.text)
#     links.append(city['href'])


# df = pd.DataFrame(zip(names, links), columns=['City', 'Link'])