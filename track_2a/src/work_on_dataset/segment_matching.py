from .common_re import RE_WHITESPACE

def shared_segments(first: list[str], second: list[str]) -> list[list[int]]:
    """
        Map each string in `first` to overlapping string indices in `second`.

        The two lists must represent the same text after removing spaces, CR, LF,
        tabs, and non-breaking spaces. Each output row contains the indices from
        `second` whose non-whitespace characters correspond to characters in
        that string from `first`. Empty/whitespace-only strings get an empty row.
    """
    normalized_first = [RE_WHITESPACE.sub("", part) for part in first]
    normalized_second = [RE_WHITESPACE.sub("", part) for part in second]

    if "".join(normalized_first) != "".join(normalized_second):
        print("".join(normalized_first), "".join(normalized_second))
        raise ValueError("The lists must match after removing whitespace")

    result: list[list[int]] = []
    second_idx = 0
    second_offset = 0

    for first_part in normalized_first:
        row: list[int] = []
        remaining = len(first_part)
        while remaining:
            # Skip empty items, which own no characters.
            while second_idx < len(normalized_second) and not normalized_second[second_idx]:
                second_idx += 1
                second_offset = 0
            if second_idx >= len(normalized_second):  # Defensive; concatenations were checked.
                raise ValueError("The lists must match after removing whitespace")

            take = min(remaining, len(normalized_second[second_idx]) - second_offset)
            if not row or row[-1] != second_idx:
                row.append(second_idx)
            remaining -= take
            second_offset += take
            if second_offset == len(normalized_second[second_idx]):
                second_idx += 1
                second_offset = 0
        result.append(row)

    return result
