from enum import Enum


class Case(Enum):
    nominative = 1,  """именительный"""
    genitive = 2, """родительный"""
    dative = 3, """дательный"""
    accusative = 4, """винительный"""
    ablative = 5, """творительный"""
    prepositional = 6, """предложный"""  # locative
    none = 0,


class CaseNameConverter(object):

    _table = {
        Case.nominative: 'nomn',
        Case.genitive: 'gent',
        Case.dative: 'datv',
        Case.accusative: 'accs',
        Case.ablative: 'ablt',
        Case.prepositional: 'loct',
        Case.none: 'none',
    }

    @staticmethod
    def to_enum(case: str):
        """
        Converts string representation of case to enum

        :param case:
        :return:

        >>> CaseNameConverter.to_enum('nomn')
        <Case.nominative: (1, 'именительный')>
        >>> CaseNameConverter.to_enum('')
        Traceback (most recent call last):
        ...
        ValueError: Аргументом должна быть строка с наименованием падежа
        """
        if "" == case:
            raise ValueError('Аргументом должна быть строка с наименованием падежа')
        case = case.lower()
        cache = dict(CaseNameConverter._table)
        if not case in cache.values():
            draft = case[:3]
            similar = [cache_case for cache_case in cache.values() if cache_case.startswith(draft)]
            if len(similar) == 0:
                raise ValueError('Не допустимое значение аргумента')
            case = similar[0]
        result = ""
        for key in cache.keys():
            if CaseNameConverter._table[key] == case:
                result = key
                break
        return result