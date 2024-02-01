# 🏠🔍 OLX/Otodom flats offer scraper

A Python script that scrapes the flats offers data in Poland from the `olx.pl` and the `otodom.pl`.

The output is in the form of a table in a CSV file.

It functions without any authentication e.g. user sign-ins/ API tokens and keys.

The script has been tested and verified to be working as expected
for scraping a small volume of data for personal use or small to mid-organizations.

It is advised to use a VPN during running the script.

The script was tested on the Chrome 119 Windows 10

- [download links](https://stackoverflow.com/a/77614979/12490791)

## 🔨 Usage

Run and install virtual environment:

```
pip install pipenv
pipenv install
pipenv shell
```

Run the scraper to test out

```
python scraper
```

Run the scraper using the command line interface:

```
python -m scraper [location_query] [area_radius] [scraped_offers_cap]
```

- location_query: Location query for scraping. E.g., `'Warszawa'`.
- area_radius: Radius of the area for scraping in kilometers. Valid options are `0, 5, 10, 15, 25, 50, 75`.
- scraped_offers_cap: Maximum number of offers to scrape. E.g., `1, 10, 100, 500...`

Example

```
python -m scraper "Warszawa" 25 10
```

This command will scrape up to `10 offers` from a `25 km radius` around `Warsaw`.

The output is saved in the `data\raw\{timestamp}_{place}\{site_1}.csv, {site_2}.csv, ...`
For example: `data\raw\2023_11_27_19_41_45_Mierzęcice__Będziński__Śląskie\olx.pl.csv`

## 🪓 Configuration

When arguments in the CLI are not provided the missing values are replaced by the config values.
Simply modify the config file: `scraper\config.py`.
More important arguments are:

```
SCRAPER:
    "location_query": "Dzierzążnia, płoński, mazowieckie",
    "area_radius": 25, # 0km, 5km, 10km, 15km, 25km, 50km, 75km
    "scraped_offers_cap": 3,

WEBDRIVER:
    "path": sanitize_path("scraper\\chromedriver.exe"),  # Path to the webdriver
    "headless": True,  # Set to False to see the browser, watch out LOGGING["debug"]

LOGGING:
    "debug": False,  # also sets the headless option to True
```

## 🤖 Testing

```
python -m unittest tests.scraper
```

## 📦 The data collected

All the data are scraped from the offer, with the corresponding URL,
except the personal data of the seller.

To see what data is scraped look at the example files at:

- `data\raw\2023_11_27_19_41_45_Mierzęcice__Będziński__Śląskie`

## 📜 License

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## 🚨 Attention

_Please be aware that scraping websites can be legally sensitive and may violate terms of service of the website. It is important to always check and comply with the legal and ethical guidelines of web scraping in your region. Continuous or high-volume scraping may lead to IP blocking or legal actions by the website owners. Use this script responsibly and at your own risk._
