from typing import List
from enum import Enum

class Stress(Enum):
    Stressed = 0
    Unstressed = 1
    Any = 2

class Word:
    def __init__(self, word: str):
        """
        Takes a string such as "ak.mak" as input, and parses it
        into a Word.

        Currently handles the following phonemes:
        - basic phonemes (e.g. p, t, k)
        - aspiration (ʰ)

        Currently handles manually specified syllables and syllable stress.
        """
        temp = []
        curr_syllable = 0
        syllable = []
        self.stressed_syllable = 0 # default, override if we find "'" or "ˈ" later on.
        for c in word:
            # Edge case: syllable marker. Increment curr_syllable
            if c == '.':
                curr_syllable += 1
                continue
            elif c == '\'' or c == "ˈ":
                # This is a stressed syllable marker. The next syllable is the stressed one.
                curr_syllable += 1
                self.stressed_syllable = curr_syllable
                continue

            # Normal case: this is some sort of phoneme component.
            if c == 'ʰ':
                # This isn't a standalone phoneme, append to the previous
                # phoneme.
                temp[-1] += c
            else:
                # This is a standalone phoneme, add to temp.
                temp.append(c)
                # Add to the current syllable.
                syllable.append(curr_syllable)
        self.phonemes = temp
        self.syllable = syllable

    def get_syllables_as_list(self) -> List[List[str]]:
        """
        For a word like "pac.man" we will return [['p', 'a', 'c'], ['m', 'a', n']]
        """
        buckets = [[] for x in range(self.syllable[-1] + 1)]
        for i, phoneme in enumerate(self.phonemes):
            buckets[self.syllable[i]].append(phoneme)
        return buckets

    def get_stress_at_index(self, index: int) -> Stress:
        if self.syllable[index] == self.stressed_syllable:
            return Stress.Stressed
        else:
            return Stress.Unstressed

    def __repr__(self) -> str:
        return ''.join(self.phonemes)