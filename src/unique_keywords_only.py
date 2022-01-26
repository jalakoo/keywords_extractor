#!/usr/bin/python

from nltk.corpus import words
import argparse
import os
import csv
import requests
import re
import nltk
import logging

#  SETUP
nltk.download('words')
stopwords_list = requests.get(
    "https://gist.githubusercontent.com/jalakoo/3fbb0370f1710a445d91a9bfd8d0c480/raw/602f07b67ee35c037137e1d5d744c8a21d521498/stop_words.txt").content
stopwords = set(stopwords_list.decode().splitlines())
englishwords = set(words.words())


def get_keywords(path, loglevel):
    logging.basicConfig( level=loglevel )
    logging.info( f'unique_keywords.py: get_keywords: loglevel set to: {loglevel}' )
    output_all_words(path)


# OUTPUT OPTIONS


def output_all_words(path, shouldLog):
    files = text_filepaths_from_dirpath(path, shouldLog)
    # Run through each file
    for filepath in files:
        # Find word count frequency for each file
        dictionary = dictionary_frequency(filepath, shouldLog)
        # Output word counts to a csv file named after the text file
        output_dict(filepath, "_keywords", dictionary, shouldLog)

# SUPPORTING FUNCTIONS


def output_dict(filepath, suffix, dict, shouldLog):
    filename_with_extension = os.path.basename(filepath)
    filename = filename_with_extension.rsplit(".", 1)[0]
    if shouldLog == True:
        print(
            f'unique_keywords_only: output_file_from: base filename: {filename}')
    with open(f'output_keywords/{filename}{suffix}.csv', "w") as csvfile:
        #
        writer = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(["word"])
        for key, value in dict.items():
            writer.writerow([key])


def dictionary_frequency(filepath, shouldLog):
    with open(filepath, "r") as file:
        d = dict()
        text = file.read()
        words = text.split()
        for word in words:
            # Clean word of special characters
            stripped_word = re.sub(r"[^a-zA-Z0-9 ]", "", word)
            # lower case to standardize
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
                f'unique_keywords_only: dictionary_frequency: dict: {sorteddict}')
        return sorteddict


def all_text_from(filepaths, shouldLog):
    text = ""
    for path in filepaths:
        with open(path, "r") as file:
            content = file.read()
            if shouldLog == True:
                print(
                    f'unique_keywords_only: text_from: file content read: {content}')
            text = text + f" {content}"
    if shouldLog == True:
        print(f'unique_keywords_only: text_from: all text:{text}')
    return text


def text_filepaths_from_dirpath(path, shouldLog):
    ext = ('.txt')
    txt_files = [
        f'{path}/{file}' for file in os.listdir(path) if file.endswith(ext)]
    if shouldLog == True:
        for file in txt_files:
            print(
                f"unique_keywords_only.py: text_filepaths: txt_files:{txt_files}")
    return txt_files


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
    # parser.add_argument(
    #     "-v", '--verbose', help='Log function outputs', type=bool, default=False)
    parser.add_argument( '-l',
                    '--loglevel',
                    default='warning',
                    help='Console log level. Example --loglevel debug, default=warning' )
    args = parser.parse_args()
    # logging.basicConfig( level=args.loglevel.upper() )
    # logging.info( f'unique_keywords.py: loglevel set to: {args.loglevel.upper()}' )
    get_keywords(args.path, args.verbose, args.loglevel.upper())
