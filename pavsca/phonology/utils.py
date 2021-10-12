from enum import Enum
from typing import List

class PType(Enum):
    C = 0
    V = 1

class Stress(Enum):
    S = 0 # Stressed
    U = 1 # Unstressed
    A = 2 # Any

class Phoneme():
    def __init__(self, phoneme: str):
        self.value = phoneme

    def __repr__(self) -> str:
        return self.value

    def __eq__(self, other) -> bool:
        return self.value == other.value

class Syllable():
    def __init__(self, phonemes: List[Phoneme], stressed=False):
        self.phonemes = phonemes
        self.stressed = stressed

    def __repr__(self) -> str:
        return f'{("+" if self.stressed else "-")}({" ".join([repr(x) for x in self.phonemes])})'

class Word():
    def __init__(self, 
        word: str = None,
        syllables: List[Syllable] = None
    ):
        """
        Takes in either a pre-made list of syllables or a raw
        string word as input.
        """
        if syllables:
            self.syllables = syllables
        elif word:
            self.syllables = []
            curr_syllable = []
            curr_phoneme = ''
            # If no syllable in the word is marked as stressed, that means the first
            # syllable is stressed.
            curr_syllable_is_stressed = '\'' not in word and 'ˈ' not in word
            for c in word:
                if c == 'ˈ' or c == '\'' or c == '.':
                    # Beginning a new syllable.
                    if curr_phoneme:
                        curr_syllable.append(Phoneme(curr_phoneme))
                        curr_phoneme = ''
                    if curr_syllable:
                        self.syllables.append(Syllable(
                            curr_syllable,
                            stressed=curr_syllable_is_stressed
                        ))
                        curr_syllable = []
                    curr_syllable_is_stressed = c != '.'
                else:
                    if c == 'ʰ' or c == 'ː':
                        # Not beginning a new phoneme! Adding to the existing phoneme.
                        curr_phoneme += c
                    else:
                        # Beginning a new phoneme.
                        if curr_phoneme:
                            curr_syllable.append(Phoneme(curr_phoneme))
                        curr_phoneme = c
            # Clean up
            if curr_phoneme:
                curr_syllable.append(Phoneme(curr_phoneme))
            if curr_syllable:
                self.syllables.append(Syllable(
                    curr_syllable,
                    stressed=curr_syllable_is_stressed
                ))

    def length(self) -> int:
        return sum([len(syl.phonemes) for syl in self.syllables])

    def at(self, index) -> Phoneme:
        """
        Returns the phoneme at the given index in this word.
        """
        # Inefficient approach for now. Go through the syllables
        # one by one, counting upwards.
        i = 0
        for syllable in self.syllables:
            for phoneme in syllable.phonemes:
                if i == index:
                    return phoneme
                i += 1

    def stress_at(self, index) -> Phoneme:
        """
        Returns the stress of the phoneme at the given index in this word.
        """
        i = 0
        for syllable in self.syllables:
            for _ in syllable.phonemes:
                if i == index:
                    return Stress.S if syllable.stressed else Stress.U
                i += 1

    def replace(self, index, phoneme: Phoneme):
        """
        Replaces the phoneme at this given index with a new phoneme.
        """
        i = 0
        for syllable in self.syllables:
            for j, _ in enumerate(syllable.phonemes):
                if i == index:
                    # Replace the phoneme here.
                    syllable.phonemes[j] = phoneme
                    return
                i += 1

    def insert(self, index, phoneme: Phoneme):
        """
        Inserts a new phoneme before the given index in this word. Adds it
        to the same syllable currently present at this index.
        """
        i = 0
        for syllable in self.syllables:
            for j, _ in enumerate(syllable.phonemes):
                if i == index:
                    # Insert the phoneme here.
                    syllable.phonemes.insert(j, phoneme)
                    return
                i += 1

    def remove(self, index):
        """
        Removes the phoneme at the given index in this word. This may cause
        the syllable to become invalid (e.g. no vowel present). So you should
        repair it afterwards if necessary.
        """
        i = 0
        for syllable in self.syllables:
            for j, _ in enumerate(syllable.phonemes):
                if i == index:
                    # Remove the phoneme here.
                    syllable.phonemes.pop(j)
                    return
                i += 1

    def repair(self):
        """
        Go through all of the syllables. If there are any invalid ones (currently
        meaning they have no vowels) then merge them into adjacent syllables (prefer
        ones to the right).
        """

        def _valid(syllable: Syllable) -> bool:
            base = ['a', 'e', 'i', 'o', 'u', 'ə']
            long = [x + 'ː' for x in base]
            concat = base + long
            for phoneme in syllable.phonemes:
                if phoneme.value in concat:
                    return True
            return False

        while any(not _valid(syl) for syl in self.syllables):
            print(self.syllables)
            print(list(_valid(x) for x in self.syllables))
            i = 0
            while i < len(self.syllables):
                if not _valid(self.syllables[i]):
                    # Try merging to the right if possible
                    if i != len(self.syllables) - 1 and _valid(self.syllables[i+1]):
                        invalid = self.syllables.pop(i)
                        # Prepend invalid syllables to the other valid syllable
                        self.syllables[i].phonemes = invalid.phonemes + self.syllables[i].phonemes
                        # If one of the syllables was stressed, conserve that.
                        self.syllables[i].stressed = self.syllables[i].stressed or invalid.stressed
                    elif i != 0 and _valid(self.syllables[i-1]):
                        invalid = self.syllables.pop()
                        # Append
                        self.syllables[i-1].phonemes += invalid.phonemes
                        # Conserve stress
                        self.syllables[i-1].stressed = self.syllables[i-1].stressed or invalid.stressed
                i += 1

    def __repr__(self) -> str:
        return f'[{"".join([repr(x) for x in self.syllables])}]'

    def ipa(self) -> str:
        """
        Returns the standard IPA form of the word
        """
        res = ''
        for i, syllable in enumerate(self.syllables):
            if i != 0:
                # We need to add the stress marking
                res += 'ˈ' if syllable.stressed else '.'
            for phoneme in syllable.phonemes:
                res += phoneme.value
        return res