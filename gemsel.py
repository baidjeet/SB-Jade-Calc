from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def fetch_gem_prices_with_selenium(query, headless=False): # IF YOU WANT IT TO SHOW THE CHROME BROWSER OPENING UP CHANGE "headless=True" INTO -> "headless=False"
    service = Service(ChromeDriverManager().install())
    options = Options()
    
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")  # Sometimes needed if running on Windows

    driver = webdriver.Chrome(service=service, options=options)
    prices = {}
    try:
        driver.get(f"https://www.skyblock.bz/search?query={query}")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "item-name")))
        time.sleep(2)  # Ensure all data is loaded
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        cards = soup.find_all('div', class_='card')
        for card in cards:
            name = card.find('div', class_='item-name').text.strip()
            price_text = card.find('p', class_='card_menu').text
            try:
                buy_price = float(price_text.split('Buy Price:')[1].split('coins')[0].replace(',', '').strip())
                sell_price = float(price_text.split('Sell Price:')[1].split('coins')[0].replace(',', '').strip())
                prices[name] = {'Buy Price': buy_price, 'Sell Price': sell_price}
            except Exception as e:
                print(f"Error processing {name}: {e}")
        return prices
    finally:
        driver.quit()

def get_user_input():
    quantities = {
        'Rough Jade Gemstone': int(input("Enter the number of Rough Jade Gemstones in your inventory: ")),
        'Flawed Jade Gemstone': int(input("Enter the number of Flawed Jade Gemstones in your inventory: ")),
        'Fine Jade Gemstone': int(input("Enter the number of Fine Jade Gemstones in your inventory: ")),
        'Flawless Jade Gemstone': int(input("Enter the number of Flawless Jade Gemstones in your inventory: "))
    }
    return quantities

def calculate_crafting_profit(prices, quantities):
    tax_rate = 1.011  # 1.1% tax (EDIT THIS IF YOU HAVE A DIFFERENT TAX BASED ON PROFILE UPGRADES)

    # Constants for the number of gemstones needed for crafting
    rough_to_flawed_ratio = 80
    flawed_to_fine_ratio = 80
    fine_to_flawless_ratio = 80

    # Calculate potential conversions and leftovers
    possible_flawed_from_rough = quantities['Rough Jade Gemstone'] // rough_to_flawed_ratio
    remaining_rough = quantities['Rough Jade Gemstone'] % rough_to_flawed_ratio
    
    total_flawed = possible_flawed_from_rough + quantities['Flawed Jade Gemstone']
    possible_fine_from_flawed = total_flawed // flawed_to_fine_ratio
    remaining_flawed = total_flawed % flawed_to_fine_ratio
    
    total_fine = possible_fine_from_flawed + quantities['Fine Jade Gemstone']
    possible_flawless_from_fine = total_fine // fine_to_flawless_ratio
    remaining_fine = total_fine % fine_to_flawless_ratio

    # Revenue calculations with tax 
    sell_as_rough_revenue = quantities['Rough Jade Gemstone'] * prices['Rough Jade Gemstone']['Sell Price'] / tax_rate
    sell_as_flawed_revenue = quantities['Flawed Jade Gemstone'] * prices['Flawed Jade Gemstone']['Sell Price'] / tax_rate
    sell_as_fine_revenue = quantities['Fine Jade Gemstone'] * prices['Fine Jade Gemstone']['Sell Price'] / tax_rate
    sell_as_flawless_revenue = quantities['Flawless Jade Gemstone'] * prices['Flawless Jade Gemstone']['Sell Price'] / tax_rate
    total_revenue_selling_as_is = sell_as_rough_revenue + sell_as_flawed_revenue + sell_as_fine_revenue + sell_as_flawless_revenue

    crafted_fine_revenue = possible_fine_from_flawed * prices['Fine Jade Gemstone']['Sell Price'] / tax_rate
    crafted_flawless_revenue = possible_flawless_from_fine * prices['Flawless Jade Gemstone']['Sell Price'] / tax_rate
    total_revenue_crafting_fine = crafted_fine_revenue + (remaining_flawed * prices['Flawed Jade Gemstone']['Sell Price'] / tax_rate)
    total_revenue_crafting_flawless = crafted_flawless_revenue + (remaining_fine * prices['Fine Jade Gemstone']['Sell Price'] / tax_rate)

    # Print detailed outputs for each scenario
    print("Revenue Calculations (after 1.1% tax):")
    print("Selling all as is:")
    print(f"  Rough: {quantities['Rough Jade Gemstone']} at {prices['Rough Jade Gemstone']['Sell Price']} each -> {sell_as_rough_revenue:.2f} coins")
    print(f"  Flawed: {quantities['Flawed Jade Gemstone']} at {prices['Flawed Jade Gemstone']['Sell Price']} each -> {sell_as_flawed_revenue:.2f} coins")
    print(f"  Fine: {quantities['Fine Jade Gemstone']} at {prices['Fine Jade Gemstone']['Sell Price']} each -> {sell_as_fine_revenue:.2f} coins")
    print(f"  Flawless: {quantities['Flawless Jade Gemstone']} at {prices['Flawless Jade Gemstone']['Sell Price']} each -> {sell_as_flawless_revenue:.2f} coins")
    print(f"Total revenue from selling as is: {total_revenue_selling_as_is:.2f} coins\n")

    print("Crafting to Fine and selling:")
    print(f"  Crafted {possible_fine_from_flawed} Fine gemstones, Revenue: {crafted_fine_revenue:.2f} coins")
    print(f"  Remaining Flawed: {remaining_flawed} worth {remaining_flawed * prices['Flawed Jade Gemstone']['Sell Price'] / tax_rate:.2f} coins")
    print(f"Total revenue from crafting to Fine and selling leftovers: {total_revenue_crafting_fine:.2f} coins\n")

    print("Crafting to Flawless and selling:")
    print(f"  Crafted {possible_flawless_from_fine} Flawless gemstones, Revenue: {crafted_flawless_revenue:.2f} coins")
    print(f"  Remaining Fine: {remaining_fine} worth {remaining_fine * prices['Fine Jade Gemstone']['Sell Price'] / tax_rate:.2f} coins")
    print(f"Total revenue from crafting to Flawless and selling leftovers: {total_revenue_crafting_flawless:.2f} coins\n")

    # Strategy determination
    best_strategy_revenue = max(total_revenue_selling_as_is, total_revenue_crafting_fine, total_revenue_crafting_flawless)
    if best_strategy_revenue == total_revenue_selling_as_is:
        print("Best strategy: Sell all gemstones as is.")
    elif best_strategy_revenue == total_revenue_crafting_fine:
        print("Best strategy: Craft as much to Fine and sell.")
    else:
        print("Best strategy: Craft as much to Flawless and sell.")



    # Include decision-making for the best strategy

def main():
    gem_type = 'jade'
    prices = fetch_gem_prices_with_selenium(gem_type)
    quantities = get_user_input()
    calculate_crafting_profit(prices, quantities)

if __name__ == "__main__":
    main()
