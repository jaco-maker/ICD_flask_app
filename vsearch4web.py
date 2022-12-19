


def Search4Letters(phrase: str, letters: str='aeiou') -> set:
    """Returns the set of letters found in phrase.
    sets are unordered, unchangeable, and unindexed."""
    return set(letters).intersection(set(phrase))

