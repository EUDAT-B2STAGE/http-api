# -*- coding: utf-8 -*-

"""
Compute the md5 checksum of a file or zipfile,
given its path (using hashlib).

From:
https://stackoverflow.com/questions/16874598/how-do-i-calculate-the-md5-checksum-of-a-file-in-python#16876405
and
https://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file#3431835

:param file_path: Path of the file.
:returns: The md5 checksum.
"""

import hashlib


def compute_md5(file_path):
    md5sum = None

    with open(file_path, 'rb') as file_to_check:
        data = file_to_check.read()
        md5sum = hashlib.md5(data).hexdigest()

    return md5sum
