# -*- coding: utf-8 -*-

# Version: Python 3.9.6
# Datum: 14.07.2022

"""This script will shuffle all filenames of the directory and split into train and test set"""

import os
import random


def split_dataset(data, seed_value=42):
    """Creates two lists of train and testset filenames."""
    random.seed(seed_value)
    random.shuffle(data)

    split_idx = round(len(data)*0.8)
    train_set = data[:split_idx]
    test_set = data[split_idx:]
    return train_set, test_set


def main():
    dir_path = "gold-pcc/bracketed_files/"
    files_list = os.listdir(dir_path)
    split_dataset(files_list, seed_value=42)


if __name__ == '__main__':
    main()
