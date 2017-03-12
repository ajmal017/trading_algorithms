#!/usr/bin/env python

# --------------------------------------------------------------------------- #
# Developer: Andrew Kirfman                                                   #
# Project: CSCE-470 Course Project                                            #
#                                                                             #
# ./google_search_program/google_scraper.py                                   #
# --------------------------------------------------------------------------- #

# --------------------------------------------------------------------------- #
# Includes                                                                    #
# --------------------------------------------------------------------------- #

from bs4 import BeautifulSoup, SoupStrainer
import requests
import copy
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
import time

# --------------------------------------------------------------------------- #
# Global Variables                                                            #
# --------------------------------------------------------------------------- #

nasdaq_file = "publicly_traded_stocks.txt"
nasdaq_list_url = "http://www.nasdaq.com/screening/companies-by-region.aspx?exchange=NASDAQ&pagesize=200"
PAGES_IN_NASDAQ_DATABASE = 15

nyse_list_url = "http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=NYSE&pagesize=200"
PAGES_IN_NYSE_DATABASE = 16

default_normalization_steps = ['punctuation', 'special_character_removal', 'case_folding']


class NormalizeText:
    def __init__(self):
        pass


    @staticmethod
    def normalize_text(token_stream, normalizations = default_normalization_steps):
        if 'str' not in str(type(token_stream)):
            return ""


        if 'punctuation' in normalizations:
            token_stream = NormalizeText.remove_punctuation(token_stream)

        if 'special_character_removal' in normalizations:
            token_stream = NormalizeText.remove_special_chars(token_stream)

        if 'case_folding' in normalizations:
            token_stream = NormalizeText.remove_case(token_stream)

        if 'stemming' in normalizations:
            token_stream = NormalizeText.stem_text(token_stream)

        if 'lemmatization' in normalizations:
            token_stream = NormalizeText.lemmatize_text(token_stream)

        token_stream = NormalizeText.consolidate_spaces(token_stream)

        return token_stream


    @staticmethod
    def tokenize_text(token_stream):
        # Right now, this module is pretty basic.  It just takes in a string and splits it on spaces.
        # Python's strip function should also get rid of extraneous leading and trailing whitespace
        # If this is proven to be incorrect, then this function should be modified to accommodate

        # Copy the string so I don't inadvertently modify the original list
        temp_token_stream = copy.deepcopy(token_stream)

        # Now, split the string on spaces to make lists of words
        temp_token_stream.split()

        # Return the resulting list
        return temp_token_stream


    @staticmethod
    def remove_punctuation(punctuated_string, punctuation_list = None):

        # If the user does not provide a list of punctuation characters
        # that they would like removed, use this default one.
        if punctuation_list is None:
            punctuation_list = ['!', '"', '#', '$', '%', '\'', '(', ')',\
                '*', '+', '+', ',', '-', '.', '/', ':', ';', '<', '=', '>',\
                '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~']

        temp_punctuated_string = copy.deepcopy(punctuated_string)

        for char in punctuation_list:
            temp_punctuated_string = temp_punctuated_string.replace(char, " ")

        return temp_punctuated_string


    @staticmethod
    def remove_special_chars(special_string, special_chars_list = None):

        # If the user does not provide a list of special characters
        # that they would like removed, use this default one
        if special_chars_list is None:
            special_chars_list = ['\n', '\r', '\t']

        temp_special_string = copy.deepcopy(special_string)

        for char in special_chars_list:
            temp_special_string = temp_special_string.replace(char, " ")

        return temp_special_string


    @staticmethod
    def consolidate_spaces(space_string):
        temp_space_string = copy.deepcopy(space_string)

        while True:
            if temp_space_string == temp_space_string.replace("  ", " "):
                break
            else:
                temp_space_string = temp_space_string.replace("  ", " ")

        return temp_space_string


    @staticmethod
    def remove_case(noncased_string):
        temp_noncased_string = copy.deepcopy(noncased_string)

        return temp_noncased_string.lower()


    @staticmethod
    def stem_text(list_to_stem, stemmer = 'porter'):
        # The input must be of type list.  If not, return an empty list
        if 'list' not in str(type(list_to_stem)):
            return []

        temp_list_to_stem = copy.deepcopy(list_to_stem)

        # This module was made expandable.  Other stemmers could be added if
        # one is potentially better other for some specific situations.
        if 'porter' in stemmer:
            stemmer = PorterStemmer()

            for i in range(0, len(temp_list_to_stem)):
                temp_list_to_stem[i] = stemmer.stem(temp_list_to_stem[i])

        return temp_list_to_stem


    @staticmethod
    def lemmatize_text(list_to_lemmatize):
        # The input must be of type list.  If not, return an empty list
        if 'list' not in str(type(list_to_lemmatize)):
            return []

        temp_list_to_lemmatize = copy.deepcopy(list_to_lemmatize)

        lemmatizer = WordNetLemmatizer()

        for i in range(0, len(temp_list_to_lemmatize)):
            temp_list_to_lemmatize[i] = lemmatizer.lemmatize(temp_list_to_lemmatize[i])

        return temp_list_to_lemmatize


class NasdaqScraper:
    def __init__(self):
        self.nasdaq_file_object = None

    # This function overwrites whatever was in the nasdaq_file and opens
    # it for new writing
    def open_nasdaq_file(self):
        self.nasdaq_file_object = open(nasdaq_file, "w")

    def close_nasdaq_file(self):
        self.nasdaq_file_object.close()

    def update_nasdaq_file(self):
        # Open the file that all the stock ticker names will be written to.
        # Write the result as a CSV with elements of the form: <company name>,<ticker symbol>
        output_file = open(nasdaq_file, "w")

        for i in range(1, PAGES_IN_NASDAQ_DATABASE):
            nasdaq_data = requests.get(nasdaq_list_url + "&page=" + str(i))

            nasdaq_soup = BeautifulSoup(nasdaq_data.text, 'html5lib')

            # Start pulling out the irrelevent data elements
            filtered_nasdaq = ""
            filtered_nasdaq = nasdaq_soup.find_all('td', {"class" : None}, style=None)

            temp_filtered_nasdaq = []
            final_filtered_nasdaq = []

            # Starting with 4th first entry in the list, out of every 4 entries in the
            # list, two are useful and two are not (something about country of origin and
            # IPO year)
            for i in range(0, len(filtered_nasdaq)):
                if i > 3 and (i % 4 == 0 or i % 4 == 1):
                    temp_filtered_nasdaq.append(filtered_nasdaq[i])

            # Finish filtering the text
            for i in range(0, len(temp_filtered_nasdaq)):

                if len(temp_filtered_nasdaq[i].find_all('a')) == 0:
                    final_filtered_nasdaq.append(temp_filtered_nasdaq[i].text.strip(" \t\n"))
                else:
                    final_filtered_nasdaq.append(temp_filtered_nasdaq[i].find_all('a')[0].text.strip(" \t\n"))

            # There are some weird entries sticking around after the initial filtering is done.
            # Attempt to filter out those extraneous entries.
            temp_list = []
            for i in range(0, len(final_filtered_nasdaq)):
                if i % 2 == 0:
                    continue

                if not any(c.islower() for c in final_filtered_nasdaq[i]):
                    # Tokenize and normalize the company names
                    company_name = final_filtered_nasdaq[i - 1]

                    company_name = NormalizeText.normalize_text(str(company_name))

                    temp_list.append(company_name)
                    temp_list.append(final_filtered_nasdaq[i])

            final_filtered_nasdaq = temp_list

            if len(final_filtered_nasdaq) % 2 != 0:
                print "[ERROR]: Nasdaq file not consistent!"
                return

            for i in range(0, len(final_filtered_nasdaq)):
                if i % 2 == 1:
                    continue

                output_file.write("%s,%s,NASDAQ\n" % (final_filtered_nasdaq[i], final_filtered_nasdaq[i + 1]))

            # Wait two seconds in-between making a request
            time.sleep(2)
def main(argc, argv):


        for i in range(0, PAGES_IN_NYSE_DATABASE):
            nasdaq_data = requests.get(nyse_list_url + "&page=" + str(i))

            nasdaq_soup = BeautifulSoup(nasdaq_data.text, 'html5lib')

            # Start pulling out the irrelevent data elements
            filtered_nasdaq = ""
            filtered_nasdaq = nasdaq_soup.find_all('td', {"class" : None}, style=None)

            temp_filtered_nasdaq = []
            final_filtered_nasdaq = []

            # Starting with 4th first entry in the list, out of every 4 entries in the
            # list, two are useful and two are not (something about country of origin and
            # IPO year)
            for i in range(0, len(filtered_nasdaq)):
                if i > 3 and (i % 4 == 0 or i % 4 == 1):
                    temp_filtered_nasdaq.append(filtered_nasdaq[i])

            # Finish filtering the text
            for i in range(0, len(temp_filtered_nasdaq)):

                if len(temp_filtered_nasdaq[i].find_all('a')) == 0:
                    final_filtered_nasdaq.append(temp_filtered_nasdaq[i].text.strip(" \t\n"))
                else:
                    final_filtered_nasdaq.append(temp_filtered_nasdaq[i].find_all('a')[0].text.strip(" \t\n"))

            # There are some weird entries sticking around after the initial filtering is done.
            # Attempt to filter out those extraneous entries.
            temp_list = []
            for i in range(0, len(final_filtered_nasdaq)):
                if i % 2 == 0:
                    continue

                if not any(c.islower() for c in final_filtered_nasdaq[i]):
                    # Tokenize and normalize the company names
                    company_name = final_filtered_nasdaq[i - 1]

                    company_name = NormalizeText.normalize_text(str(company_name))

                    temp_list.append(company_name)
                    temp_list.append(final_filtered_nasdaq[i])

            final_filtered_nasdaq = temp_list

            if len(final_filtered_nasdaq) % 2 != 0:
                print "[ERROR]: Nasdaq file not consistent!"
                return

            for i in range(0, len(final_filtered_nasdaq)):
                if i % 2 == 1:
                    continue

                output_file.write("%s,%s,NYSE\n" % (final_filtered_nasdaq[i], final_filtered_nasdaq[i + 1]))

            # Wait two seconds in-between making a request
            time.sleep(2)

        # Close the output file now that I'm done writing all of the stock results
        output_file.close()


def get_nasdaq_file(self):
    pass


def update_file():
    scraper = NasdaqScraper()

    scraper.update_nasdaq_file()







# I probably would want this to do a little bit more than just
# update the file when calling it as a script.  I'll worry about that later.
# Potentially think about adding options using getopt.
if __name__ == "__main__":
    update_file()





