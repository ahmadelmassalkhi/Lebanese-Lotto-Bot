import time
import random
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from Draw import *


class Bot:
    MIN_YEAR = 2002
    ALT_TEXT = 'Lotto Lebanon PLAY LEBANON LOTTO, loto libanais, Buy The Lotto, Check the Results, Win The Draw.'

    def valid_year(self, year):
        return (Bot.MIN_YEAR <= year) and (year <= datetime.now().year)


    def get_year_url(self, year: int):
        if not self.valid_year(year):
            raise ValueError("Invalid year.")
        return f'https://www.lebanon-lotto.com/past_results_list.php?pastyearsresults={year}'
    
    #####################################################################################################
    #####################################################################################################
            
    def extract_draw(self, a_tag):
        # Extract draw number from title
        draw_number = a_tag.get('title').split()[-1]

        # Get date of draw
        draw_date = a_tag.find('p').text

        # Get draw result
        draw_result = self.extract_draw_result(a_tag.get('href'))

        return Draw(draw_number, draw_date, draw_result)
    

    def extract_draw_result(self, draw_url: str):
        max_retries = 5
        backoff_factor = 1

        for attempt in range(max_retries):
            try:
                # Fetch the web page content
                response = requests.get(draw_url)
                response.raise_for_status()  # Raise an exception for HTTP errors

                # Parse HTML using BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find all img tags with the specified alt attribute
                img_tags = soup.find_all('img', alt=Bot.ALT_TEXT)

                # Extract draw result from image src
                draw_result = []
                bonus = 0
                for idx, img in enumerate(img_tags):
                    # extract number
                    last_two_digits = img['src'][-6:-4]
                    # remove leading zeroes
                    number = int(last_two_digits.lstrip('0'))
                    # check if number = bonus
                    if idx == len(img_tags)-1: return DrawResult(draw_result, number)
                    # add to list (not bonus)
                    draw_result.append(number)

            except requests.exceptions.RequestException as e:
                wait_time = backoff_factor * (2 ** attempt) + random.uniform(0, 1)
                print(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)

        print(f'Failed to fetch draw result from {draw_url} after {max_retries} attempts.')
        return []
    
    
    #####################################################################################################
    #####################################################################################################
    
    def extract_draws_year(self, year: int):
        try:
            # Validate year
            if not self.valid_year(year):
                raise ValueError(f'Invalid year {year}.')

            # Parse the HTML content
            soup = BeautifulSoup(requests.get(self.get_year_url(year)).content, 'html.parser')

            # Find all <a> tags with title attribute starting with "Lotto Lebanon draw"
            lotto_links = soup.find_all('a', title=lambda title: title and title.startswith('Lotto Lebanon draw'))

            # Process lotto links & return results
            draws = []
            for link in reversed(lotto_links):
                draws.append(self.extract_draw(link))
                print(draws[-1].to_string())
            return draws
        
        # handle exceptions
        except ValueError as ve:
            print(f"ValueError: {ve}, year {year}")
        except ConnectionError as ce:
            print(f"ConnectionError: {ce}, year {year}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}, year {year}")
        exit(1)

    def extract_draws_years(self, start: int, finish: int):
        if not self.valid_year(start):
            raise ValueError(f'Invalid year {start}.')
        if not self.valid_year(finish):
            raise ValueError(f'Invalid year {finish}.')

        draws = {}
        with ThreadPoolExecutor(max_workers=12) as executor:
            future_to_year = {executor.submit(self.extract_draws_year, year): year for year in range(start, finish + 1)}
            for future in as_completed(future_to_year):
                year = future_to_year[future]
                try:
                    draws[year] = future.result()
                except Exception as e:
                    print(f'Year {year} generated an exception: {e}')
        return draws
    
    #####################################################################################################
    #####################################################################################################
    
    def extract_draws_current_year(self):
        return self.extract_draws_years(datetime.now().year, datetime.now().year)
    

    def extract_draws_all_time(self):
        return self.extract_draws_years(Bot.MIN_YEAR, datetime.now().year)
    
    
    def extract_latest_draw(self):
        try:
            year = datetime.now().year
            
            # request the html
            request = requests.get(self.get_year_url(year))

            # Parse the HTML content
            soup = BeautifulSoup(request.content, 'html.parser')

            # Find all <a> tags with title attribute starting with "Lotto Lebanon draw"
            lotto_links = soup.find_all('a', title=lambda title: title and title.startswith('Lotto Lebanon draw'))

            # extract & return latest draw
            return self.extract_draw(lotto_links[0])
        
        # handle exceptions
        except ValueError as ve:
            print(f"ValueError: {ve}, year {year}")
        except ConnectionError as ce:
            print(f"ConnectionError: {ce}, year {year}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}, year {year}")
        quit()

    
if __name__ == "__main__":
    start_time = time.time()

    # extract draws from range of years
    bot = Bot()
    draws = bot.extract_draws_current_year()

    # save draws for each year, and join them all into one final result txt file
    saver = DrawSaver()
    saver.save_draws_dict(draws)
    saver.join_draw_files()

    # calculate time taken
    end_time = time.time()
    print(f'Time taken = {end_time - start_time}')
