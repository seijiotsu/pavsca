from typing import List, Tuple
import sys

from phonology.utils import *
from phonology.tre_rule import *

def add_to_category_define_dict(categories: dict, define: str):
    """
    Adds the define specified by `define` into the `categories` dict.
    """
    names, value = define.split('=')
    names = [x.strip() for x in names.split(',')]
    value = [Phoneme(x.strip()) for x in value.split(',')]

    # By now, we should have something like this:
    # names = ['<consonant>', 'C']
    # value = ['p', 't', 'k', 'g']
    for name in names:
        # TODO: Deep copy this? If it's mutated at all then we might
        # run into unexpected results.
        categories[name] = value

def get_phonemes(categories: dict, phonemes: str) -> List[List[Phoneme]]:
    """
    Given something like '#<consonant>_n'
    Will return something like [['#'], ['p', 't', 'k'], ['_'], ['n']]

    Need to handle stress. If we have e.g. /h/#_+k we want something like the following:
    [(['#', '#']), ([], ['h'), (['k'], ['k'], stressed=True)

    To parse that... well basically as we go along, if we see a + or a - that means we need
    to mark the next phoneme we parse as either stressed or unstressed.
    """
    def _get_next_phonemes(index) -> Tuple[List[Phoneme], int]:
        token = ''
        # Case 1: the next token is a category in long form, e.g. <consonant>
        if phonemes[index] == '<':
            while phonemes[index] != '>':
                token += phonemes[index]
                index += 1
            # move past the '>' to continue parsing.
            token += '>'
            index += 1
        # Case 2: the next token is a category in short form, e.g. C
        elif phonemes[index].isupper():
            token = phonemes[index]
            index += 1
        # Case 3: it's something like pʰ, aː, k, ə, etc.
        else:
            token = phonemes[index]
            index += 1
            while index < len(phonemes) and phonemes[index] in ['ʰ']:
                token += phonemes[index]
                index += 1
        
        if token.isupper() or '<' in token:
            return (categories[token], index)
        else:
            return ([Phoneme(token)], index)

    if not phonemes:
        return [PhonemeSet([])]

    result = []
    i = 0
    while i < len(phonemes):
        stress = Stress.A
        if phonemes[i] in ['+', '-']:
            stress = Stress.S if phonemes[i] == '+' else Stress.U
            parsed, i = _get_next_phonemes(i+1)
        else:
            parsed, i = _get_next_phonemes(i)
        result.append(PhonemeSet(parsed, stress))
    return result



def parse_TRE_rule(categories, rule):
    target, replacement, environment = [get_phonemes(categories, x) for x in rule.split('/')]
    return TRERule(target, replacement, environment)

def apply_TRE_rule(tre_rule: TRERule, words: List[Word]):
    """
    """
    def _can_apply_at_index(word: Word, index: int) -> bool:
        """
        ### How this works
        Say we're trying to match p/f/#_m against pmat. Our TRE change will look
        like [('#', '#'), ('p', 'f'), ('m', 'm')]. We try to apply the change to
        index 0 of pmat. We start from index 0 of the TRE change, which is '#'.
        We notice that this is '#', so we check if we're at the beginning of the
        word. We are. But since it's '#' we don't increment our search forward on
        the word. Instead we only increment our TRE change. So now we find that we
        have 'p', and we compare this to index 0 of the word. Continue on until we
        either find a contradiction or we verify we can apply this at this specific
        index.
        """
        curr_index = index
        for part in tre_rule.rule:
            if part[0].is_word_boundary():
                if curr_index != 0 and curr_index != word.length():
                    return False
            elif part[0].is_empty():
                pass
            else:
                if curr_index < word.length() and word.at(curr_index) in part[0].phonemes:
                    part_stress = part[0].stress
                    word_stress = word.stress_at(curr_index)
                    if part_stress != Stress.A and word_stress != part_stress:
                        return False
                    curr_index += 1
                else:
                    return False
        return True

    def _apply_at_index(word: Word, index: int):
        curr_index = index
        for part in tre_rule.rule:
            if part[0].is_word_boundary():
                pass
            elif part[0].is_empty():
                # Epenthesis
                word.insert(curr_index, part[1].phonemes[0]) # TODO: what if we're given multiple phonemes here?
                curr_index += 1
            elif part[1].is_empty():
                # Deletion
                word.remove(curr_index)
            else:
                # Change. First find the corresponding index in the first array. But if
                # the replacement array is shorter then use the last one from that array.
                chg_index = min(part[0].phonemes.index(word.at(curr_index)), len(part[1].phonemes) - 1)
                word.replace(curr_index, part[1].phonemes[chg_index])
                curr_index += 1

    print(f'Applying rule {tre_rule.rule}')
    for word in words:
        for i in range(0, word.length()):
            if _can_apply_at_index(word, i):
                print(f'----> {word} at index={i}')
                _apply_at_index(word, i)
                word.repair()
                print(word)


def apply(commands: List[str], words: List[Word]):
    categories = {}

    for command in commands:
        if '=' in command:
            add_to_category_define_dict(categories, command)
        else:
            # This is a rule that we need to apply.
            # For now we only support basic TARGET/REPLACEMENT/ENVIRONMENT rules.
            tre_rule = parse_TRE_rule(categories, command)
            apply_TRE_rule(tre_rule, words)

    with open(sys.argv[3], 'w', encoding='utf8') as hdl:
        for word in words:
            hdl.write(word.ipa())

if __name__ == '__main__':
    with open(sys.argv[1], 'r', encoding='utf8') as hdl:
        # Special rule: ignore lines starting with '//' since they are
        # comments.
        rule_list = [x for x in hdl.read().split('\n') if x and x[:2] != '//']

    with open(sys.argv[2], 'r', encoding='utf8') as hdl:
        words = hdl.read()
        # We do a little preprocessing to fix common issues.
        words = words.replace(':', 'ː').replace('\'', 'ˈ')
        word_list = [
            Word(word)
            for word in words.split('\n')
        ]

    apply(rule_list, word_list)