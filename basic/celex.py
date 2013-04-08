'''
@author: Tal Linzen
'''

import os

celex_english_dir = os.path.expanduser('~/Dropbox/Experiments/tools/celex_english')

field_documentation = {
    'Attr_A':  'for adjectives: attributive',
    'Attr_N':  'for nouns: attributive ',
    'C_N': 'for nouns: countable   ',
    'Card_NUM':    'for numerals: cardinal ',
    'ClassNum':    'word class: numeric',
    'Class':   'word class: label  ',
    'CobDev':  'COBUILD frequency deviation',
    'CobLog':  'COBUILD frequency: logarithmic ',
    'CobMln':  'COBUILD frequency (1,000:000)num   ',
    'CobSLog': 'COBUILD spoken frequency: logarithmic  ',
    'CobSMln': 'COBUILD spoken frequency (1,000:000)   ',
    'CobS':    'COBUILD spoken frequency 1.3m  ',
    'CobSpellDev': 'COBUILD spelling frequency deviation   ',
    'CobSpellFreq':    'COBUILD spelling frequency ',
    'CobWLog': 'COBUILD written frequency: logarithmic ',
    'CobWMln': 'COBUILD written frequency (1,000:000)  ',
    'CobW':    'COBUILD written frequency 17.4m',
    'Cob': 'COBUILD frequency  ',
    'Comb_ADV':    'for adverbs: combinatory   ',
    'CompCnt': 'number of morphological components ',
    'Comp':    'compound analysis method   ',
    'Cor_C':   'for conjunctions: coordinating ',
    'Def': 'default analysis   ',
    'Dem_PRON':    'for pronouns: demonstrative',
    'DerComp': 'derivational compound analysis method  ',
    'Der': 'derivation analysis',
    'Det_PRON':    'for pronouns: determinative use',
    'Ditrans_V':   'for verbs: ditransitive',
    'Exp_ADV': 'for adverbs: expression',
    'Exp_A':   'for adjectives: expression ',
    'Exp_NUM': 'for numerals: expression   ',
    'Exp_N':   'for nouns: expression  ',
    'Exp_PRON':    'for pronouns: expression   ',
    'Exp_V':   'for verbs: expression  ',
    'FamFreq': 'family frequency   ',
    'FamSize': 'family size',
    'FlatClass':   'flat segmentation: word class labels   ',
    'FlatSA':  'flat segmentation: stem/affix labels   ',
    'Flat':    'flat segmentation  ',
    'GrC_N':   'for nouns: group countable ',
    'GrUnc_N': 'for nouns: group uncountable   ',
    'HeadCnt': 'headword: number of letters',
    'HeadDia': 'headword: diacritics   ',
    'HeadLowSort': 'headword, lowercase, alphabetical: sorted  ',
    'HeadLow': 'headword, lowercase: alphabetical  ',
    'HeadRev': 'headword: reversed ',
    'HeadSylCnt':  'headword: number of orthographic syllables ',
    'HeadSylDia':  'headword, syllabified: diacritics  ',
    'HeadSyl': 'headword: syllabified  ',
    'Head':    'headword   ',
    'Head':    'headword   ',
    'IdNum':   'lemma number   ',
    'ImmAllo': 'stem allomorphy: top level ',
    'ImmClass':    'immediate segmentation: word class labels  ',
    'ImmInfix':    'infixation: top level  ',
    'ImmOpac': 'opacity: top level ',
    'ImmRevers':   'reversion: top level   ',
    'ImmSA':   'immediate segmentation: stem/affix labels  ',
    'ImmSubCat':   'immediate segementation: subcat labels ',
    'ImmSubst':    'affix substitution: top level  ',
    'Imm': 'immediate segmentation ',
    'Intrans_V':   'for verbs: intransitive',
    'Lang':    'language information   ',
    'LevelCnt':    'number of morphological levels ',
    'Link_V':  'for verbs: linking verb',
    'MorCnt':  'number of morphological analyses   ',
    'MorphCnt':    'number of morphological forms  ',
    'MorphStatus': 'morphological status   ',
    'NVAffComp':   'noun-verb-affix compound   ',
    'Ord_ADV': 'for adverbs: ordinary  ',
    'Ord_A':   'for adjectives: ordinary   ',
    'Ord_NUM': 'for numerals: ordinary ',
    'OrthoCnt':    'number of spellings',
    'OrthoStatus': 'status of spelling ',
    'Pers_PRON':   'for pronouns: personal ',
    'PhonCLX': 'phon. headword: CELEX charset  ',
    'PhonCPA': 'phon. headword: CPA charset',
    'PhonCVBr':    'headword, phon CV pattern: with brackets   ',
    'PhonCV':  'headword: phon. CV pattern ',
    'PhonCnt': 'headword: number of phonemes   ',
    'PhonDISC':    'phon. headword: DISC charset   ',
    'PhonSAM': 'phon. headword: SAM-PA charset ',
    'PhonStrsCLX': 'syll. phon. headword, with stress: CELEX charset   ',
    'PhonStrsCPA': 'syll. phon. headword, with stress: CPA charset ',
    'PhonStrsDISC':    'syll. phon. headword, with stress: DISC charset',
    'PhonStrsSAM': 'syll. phon. headword, with stress: SAM-PA charset  ',
    'PhonSylBCLX': 'syll. phon. headword: CELEX charset (brackets) ',
    'PhonSylCLX':  'syll. phon. headword: CELEX charset',
    'PhonSylCPA':  'syll. phon. headword: CPA charset  ',
    'PhonSylDISC': 'syll. phon. headword: DISC charset ',
    'PhonSylSAM':  'syll. phon. headword: SAM-PA charset   ',
    'PhrPrep_V':   'for verbs: phrasal prepositional verb  ',
    'Phr_V':   'for verbs: phrasal verb',
    'Plu_N':   'for nouns: plural use  ',
    'Poss_PRON':   'for pronouns: possessive   ',
    'PostPos_ADV': 'for adverbs: postpositive  ',
    'PostPos_A':   'for adjectives: postpositive   ',
    'PostPos_N':   'for nouns: postpositive',
    'Pred_ADV':    'for adverbs: predicative   ',
    'Pred_A':  'for adjectives: predicative',
    'Prep_V':  'for verbs: prepositional verb  ',
    'PronCnt': 'number of pronunciations   ',
    'PronStatus':  'status of pronunciation',
    'Pron_PRON':   'for pronouns: pronomial use',
    'Proper_N':    'for nouns: proper noun ',
    'Refl_PRON':   'for pronouns: reflexive',
    'Sing_N':  'for nouns: singular use',
    'StrsPat': 'headword: stress pattern   ',
    'StrucAllo':   'stem allomorphy: any level ',
    'StrucBrackLab':   'structured segmentation: word class labels only',
    'StrucLab':    'structured segmentation: word class labels ',
    'StrucOpac':   'opacity: any level ',
    'StrucSubst':  'affix substitution: any level  ',
    'Struc':   'structured segmentation',
    'Sub_C':   'for conjunctions: subordinating',
    'SylCnt':  'headword: number of phonetic syllables ',
    'TransComp_V': 'for verbs: transitive plus complementation ',
    'TransDer':    'derivational transformation: top level ',
    'Trans_V': 'for verbs: transitive  ',
    'Unc_N':   'for nouns: uncountable ',
    'Voc_N':   'for nouns: vocative',
    'Wh_PRON': 'for pronouns: wh-pronoun   ',
}

db_fields = {
    'efl': ['IdNum', 'Head', 'Cob', 'CobDev', 'CobMln', 'CobLog', 'CobW',
        'CobWMln', 'CobWLog', 'CobS', 'CobSMln', 'CobSLog'],
    'eml': ['IdNum', 'Head', 'Cob', 'MorphStatus', 'Lang', 'MorphCnt',
        'NVAffComp', 'Der', 'Comp', 'DerComp', 'Def', 'Imm', 'ImmSubCat',
        'ImmSA', 'ImmAllo', 'ImmSubst', 'ImmOpac', 'TransDer', 'ImmInfix',
        'ImmRevers', 'FlatSA', 'StrucLab', 'StrucAllo', 'StrucSubst',
        'StrucOpac'],
    'esl': ['IdNum', 'Head', 'Cob', 'ClassNum', 'C_N', 'Unc_N', 'Sing_N',
        'Plu_N', 'GrC_N', 'GrUnc_N', 'Attr_N', 'PostPos_N', 'Voc_N',
        'Proper_N', 'Exp_N', 'Trans_V', 'TransComp_V', 'Intrans_V',
        'Ditrans_V', 'Link_V', 'Phr_V', 'Prep_V', 'PhrPrep_V', 'Exp_V',
        'Ord_A', 'Attr_A', 'Pred_A', 'PostPos_A', 'Exp_A', 'Ord_ADV',
        'Pred_ADV', 'PostPos_ADV', 'Comb_ADV', 'Exp_ADV', 'Card_NUM',
        'Ord_NUM', 'Exp_NUM', 'Pers_PRON', 'Dem_PRON', 'Poss_PRON',
        'Refl_PRON', 'Wh_PRON', 'Det_PRON', 'Pron_PRON', 'Exp_PRON',
        'Cor_C', 'Sub_C'],
    'efw': ['IdNum', 'Word', 'IdNumLemma', 'Cob', 'CobDev', 'CobMln',
        'CobLog', 'CobW', 'CobWMln', 'CobWLog', 'CobS', 'CobSMln',
        'CobSLog'],
    'emw': ['IdNum', 'Word', 'Cob', 'IdNumLemma', 'FlectType', 'TransInfl']
}

field_keys = {
    'ClassNum': {   # Page 4-83
        '1': 'noun',
        '2': 'adjective',
        '3': 'number',
        '4': 'verb',
        '5': 'article',
        '6': 'pronoun',
        '7': 'adverb',
        '8': 'preposition',
        '9': 'conjunction',
        '10': 'interjection',
        '11': 'single_contraction',
        '12': 'complex_contraction',
        '13': '?', # Not from the docs
        '14': '??',
        '15': '???'
    },
    'FlectType': {  # Page 4-78
        'S': 'singular',
        'P': 'plural',
        'b': 'positive',
        'c': 'comparative',
        's': 'superlative',
        'i': 'infinitive',
        'p': 'participle',
        'e': 'present_tense',
        'a': 'past_tense',
        '1': '1st_person_verb',
        '2': '2nd_person_verb',
        '3': '3rd_person_verb',
        'r': 'rare_form',
        'X': 'headword_form'
    }
}


class Celex(object):

    def __init__(self):
        self.lemmas = self.read_dbs(['efl', 'eml', 'esl'])
        self.lemma_heads = {}
        for lemma in self.lemmas:
            self.lemma_heads.setdefault(lemma['Head'], []).append(lemma)
        self.wordforms = self.read_dbs(['efw', 'emw'])
        self.lemma_lookup = {x['Head']: x for x in self.lemmas}
        self.wf_lookup = {x['Word']: x for x in self.wordforms}

    def read_dbs(self, dbs):
        first_db = self.read_db(dbs[0])
        for other_db_name in dbs[1:]:
            other_db = self.read_db(other_db_name)
            for first, other in zip(first_db, other_db):
                first.update(other)
        return first_db

    def read_db(self, db):
        fname = os.path.join(celex_english_dir, db, '%s.cd' % db)
        return [dict(zip(db_fields[db], x.split('\\')))
                for x in open(fname).readlines()]
