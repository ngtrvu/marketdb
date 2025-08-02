import hashlib


def short_str(s, char_length=32):
    """Geneate hexadecimal string with given length from a string

    >>> short_str("hello world", 8)
    '309ecc48'
    """

    if char_length > 128:
        raise ValueError("char_length {} exceeds 128".format(char_length))
    hash_object = hashlib.sha512(s.encode())
    hash_hex = hash_object.hexdigest()
    return hash_hex[0:char_length]


def generate_doc_id(url, id_length=32):
    return short_str(s=url, char_length=id_length)


if __name__ == '__main__':
    print(generate_doc_id("https://news.bitcoin.com/cross-chain-bridge-value-increases-by-89-in-less-than-a-month-surpassing-14-billion-tvl/"))
