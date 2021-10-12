from typing import List

from .utils import Phoneme, Stress

class PhonemeSet():
    def __init__(self, phonemes: List[Phoneme], stress: Stress=Stress.A):
        self.phonemes = phonemes
        self.stress = stress

    def is_word_boundary(self) -> bool:
        return len(self.phonemes) == 1 and self.phonemes[0] == Phoneme('#')

    def is_insertion_point(self) -> bool:
        return len(self.phonemes) == 1 and self.phonemes[0] == Phoneme('_')

    def is_empty(self) -> bool:
        return len(self.phonemes) == 0

    def __repr__(self) -> str:
        stress_mark = ''
        if self.stress == Stress.S:
            stress_mark = '+'
        elif self.stress == Stress.U:
            stress_mark = '-'
        return f'{stress_mark}{self.phonemes}'

class TRERule():
    """
    Target / Replacement / Environment rule.
    """
    def __init__(
        self,
        target: PhonemeSet,
        replacement: PhonemeSet,
        environment: PhonemeSet
    ):
        # Pad target and replacement so that they are the same length.
        if len(target) < len(replacement):
            target += [PhonemeSet([]) for x in range(0, len(replacement) - len(target))]
        if len(replacement) < len(target):
            replacement += [PhonemeSet([]) for x in range(0, len(target) - len(replacement))]

        # Find the index of ['_'] in the environment and insert our substitution rule there.
        ind = [i for i, phoneme_set in enumerate(environment) if phoneme_set.is_insertion_point()][0]
        tre_rule_from = environment[:ind] + target + environment[ind+1:]
        tre_rule_to = environment[:ind] + replacement + environment[ind+1:]

        self.rule = list(zip(tre_rule_from, tre_rule_to))