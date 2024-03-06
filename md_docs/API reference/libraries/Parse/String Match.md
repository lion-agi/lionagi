
## Methods Overview

### `jaro_distance`

Calculates the Jaro distance between two strings, a measure of similarity where 0 signifies no similarity and 1 denotes an exact match.

#### Arguments

- `s (str)`: The first string to compare.
- `t (str)`: The second string to compare.

#### Returns

- `float`: The Jaro distance, ranging from 0 to 1.

### `jaro_winkler_similarity`

Calculates the Jaro-Winkler similarity between two strings, an extension of the Jaro similarity that gives more weight to matches at the start of the strings.

#### Arguments

- `s (str)`: The first string to compare.
- `t (str)`: The second string to compare.
- `scaling (float)`: The scaling factor for adjusting the score based on prefix similarity. Typical values are between 0.1 and 0.25.

#### Returns

- `float`: The Jaro-Winkler similarity, ranging from 0 to 1.

### `levenshtein_distance`

Calculates the Levenshtein distance between two strings, indicating the number of single-character edits (insertions, deletions, or substitutions) required to change one word into the other.

#### Arguments

- `a (str)`: The first string to compare.
- `b (str)`: The second string to compare.

#### Returns

- `int`: The Levenshtein distance between the two strings.

## Examples

### Example: Calculating Jaro Distance

```python
distance = StringMatch.jaro_distance("martha", "marhta")
print(distance)  # Output: 0.9444444444444445
```
This example calculates the Jaro distance between two strings, illustrating their high similarity despite the transposed letters.

### Example: Calculating Jaro-Winkler Similarity

```python
similarity = StringMatch.jaro_winkler_similarity("dixon", "dicksonx", scaling=0.1)
print(similarity)  # Output: Close to 0.813
```
This example demonstrates how the Jaro-Winkler similarity can account for the common prefix "dix" to provide a higher similarity score than the Jaro distance alone might suggest.

### Example: Calculating Levenshtein Distance

```python
distance = StringMatch.levenshtein_distance("kitten", "sitting")
print(distance)  # Output: 3
```

This calculation shows the Levenshtein distance as `3`, indicating that three single-character edits are required to change "kitten" into "sitting": substituting 'k' with 's', substituting 'e' with 'i', and appending 'g'.
