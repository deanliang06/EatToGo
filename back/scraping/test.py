from scrape import RestaurantResults

if __name__ == "__main__":
    rest = RestaurantResults("https://www.opentable.com/vejigante-restaurant")
    rest.scraping()