from collections.abc import Iterable


def normalize_tags(tags: Iterable[str | None] | None) -> list[str]:
    if not tags:
        return []

    # trim whitespace from tag names
    trimmed_tags = [name.strip() for name in tags if name is not None and name.strip()]

    # remove duplicates while preserving the order
    unique_tags: set[str] = set()
    normalized_tags: list[str] = []
    for name in trimmed_tags:
        if name in unique_tags:
            continue
        unique_tags.add(name)
        normalized_tags.append(name)

    return normalized_tags
