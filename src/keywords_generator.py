#!/usr/bin/python

import math
from operator import itemgetter
import argparse
import os
import csv
import yake
import requests
import re
import nltk
from nltk.corpus import words

# Rake Support
from rake_nltk import Rake
import nltk
nltk.download('stopwords')
nltk.download('punkt')

# SETUP
stopwords_list = requests.get(
    "https://gist.githubusercontent.com/jalakoo/3fbb0370f1710a445d91a9bfd8d0c480/raw/602f07b67ee35c037137e1d5d744c8a21d521498/stop_words.txt").content
stopwords = set(stopwords_list.decode().splitlines())
nltk.download('words')
englishwords = set(words.words())


def get_keywords(path, shouldLog, enableAllWords, enableYake, enableRake):
    if enableAllWords:
        output_all_words(path, shouldLog)
    if enableRake:
        output_with_rake(path, shouldLog)
    if enableYake:
        output_with_yake(path, shouldLog)


# OUTPUT OPTIONS


def output_with_yake(path, shouldLog):
    # Update to export files
    files = text_filepaths_from_dirpath(path, shouldLog)
    for filepath in files:
        with open(filepath, "r") as file:
            text = file.read()
            dictionary = extract_with_yake(text, shouldLog)
            output_dict(filepath, "_yake", dictionary, shouldLog)


def output_with_rake(path, shouldLog):
    files = text_filepaths_from_dirpath(path, shouldLog)
    for filepath in files:
        with open(filepath, "r") as file:
            text = file.read()
            dictionary = extract_with_rake(text, shouldLog)
            output_dict(filepath, "_rake", dictionary, shouldLog)


def output_all_words(path, shouldLog):
    files = text_filepaths_from_dirpath(path, shouldLog)
    # Run through each file
    for filepath in files:
        # Find word count frequency for each file
        dictionary = dictionary_frequency(filepath, shouldLog)
        # Output word counts to a csv file named after the text file
        output_dict(filepath, "_allwords", dictionary, shouldLog)

# SUPPORTING FUNCTIONS


def output_dict(filepath, suffix, dict, shouldLog):
    filename_with_extension = os.path.basename(filepath)
    filename = filename_with_extension.rsplit(".", 1)[0]
    if shouldLog == True:
        print(
            f'frequency_counter: output_file_from: base filename: {filename}')
    with open(f'output/{filename}{suffix}.csv', "w") as csvfile:
        #
        writer = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(["video", "word", "count"])
        for key, value in dict.items():
            writer.writerow([filename, key, value])


def dictionary_frequency(filepath, shouldLog):
    with open(filepath, "r") as file:
        d = dict()
        text = file.read()
        words = text.split()
        for word in words:
            stripped_word = re.sub(r"[^a-zA-Z0-9 ]", "", word)
            lowercased = stripped_word.lower()
            if lowercased == "":
                continue
            if lowercased not in englishwords:
                continue
            if any(stopword for stopword in stopwords if(stopword.lower() == lowercased)):
                continue
            if lowercased in d:
                d[lowercased] = d[lowercased] + 1
            else:
                d[lowercased] = 1
        sortedlist = sorted(d.items(), key=lambda x: x[1])
        sorteddict = dict(sortedlist)
        if shouldLog == True:
            print(
                f'frequency_counter: dictionary_frequency: dict: {sorteddict}')
        return sorteddict


def all_text_from(filepaths, shouldLog):
    text = ""
    for path in filepaths:
        with open(path, "r") as file:
            content = file.read()
            if shouldLog == True:
                print(
                    f'frequency_counter: text_from: file content read: {content}')
            text = text + f" {content}"
    if shouldLog == True:
        print(f'frequency_counter: text_from: all text:{text}')
    return text


def text_filepaths_from_dirpath(path, shouldLog):
    ext = ('.txt')
    txt_files = [
        f'{path}/{file}' for file in os.listdir(path) if file.endswith(ext)]
    if shouldLog == True:
        for file in txt_files:
            print(
                f"frequency_counter.py: text_filepaths: txt_files:{txt_files}")
    return txt_files


def extract_with_yake(text, shouldLog):
    language = "en"
    max_ngram_size = 3
    deduplication_threshold = 0.9
    numOfKeywords = 20
    custom_kw_extractor = yake.KeywordExtractor(
        lan=language, n=max_ngram_size, dedupLim=deduplication_threshold, top=numOfKeywords, features=None)
    # Produces tuples
    keywords_tuple = custom_kw_extractor.extract_keywords(text)
    keywords = dict()
    for key, value in keywords_tuple:
        keywords[key] = value
    if shouldLog == True:
        print(f"frequency_counter.py: extract_with_yake: {keywords}")
    return keywords


def extract_with_rake(text, shouldLog):
    r = Rake()
    r.extract_keywords_from_text(text)
    # Produces a tuple
    keywords_tuple = r.get_ranked_phrases_with_scores()
    # Convert tuples to a dict
    keywords = dict()
    for value, key in keywords_tuple:
        keywords[key] = value
    if shouldLog == True:
        print(f'frequency_counter: extract_with_rake: text input: {text}')
        print(f'frequency_counter: extract_with_rake: keywords: {keywords}')
    return keywords


# Validate path argument
def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    working_path = os.getcwd()
    default_path = os.path.dirname(working_path + "/input/")
    parser.add_argument(
        "-p", '--path', help='Path of text files to process', type=dir_path, default=default_path)
    parser.add_argument(
        "-v", '--verbose', help='Log function outputs', type=bool, default=False)
    parser.add_argument(
        "-a", '--allwords', help='Extract all english words', type=bool, default=True)
    parser.add_argument(
        "-y", '--yake', help='Extract words using Yake', type=bool, default=False)
    parser.add_argument(
        "-r", '--rake', help='Extract words using Rake', type=bool, default=False)
    args = parser.parse_args()
    get_keywords(args.path, args.verbose, args.allwords, args.yake, args.rake)
