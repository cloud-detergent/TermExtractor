import pymorphy2
from collections import namedtuple
from ITermExtractor.Structures.PartOfSpeech import PartOfSpeech, POSNameConverter
from ITermExtractor.Structures.Case import Case, CaseNameConverter
import helpers


__MorphAnalyzer__ = pymorphy2.MorphAnalyzer()
TaggedWord = namedtuple('TaggedWord', ['word', 'pos', 'case', 'normalized'])


def is_word_in_tuple_list(collocation: list, check_word: str) -> bool:
    """
    осуществляет проверку наличия слова (check_word) в словосочетании
    checks if checked word is in collocation
    :param collocation: Tagged word list consisting of named tuples
    :param check_word: an argument to check
    :return: if word is in collocation or not

    >>> is_word_in_tuple_list([TaggedWord(word="огонь", pos=PartOfSpeech.noun, case=Case.nominative, normalized="огонь"), TaggedWord(word="артиллерии", pos=PartOfSpeech.noun, case=Case.genitive, normalized="артиллерия")], "артиллерией")
    True
    """
    if not isinstance(collocation, list) or len(collocation) == 0 or False in [isinstance(word, TaggedWord) for word in collocation]:
        raise TypeError("Необходим список слов с тегами")
    if not isinstance(check_word, str) or check_word == "":
        raise TypeError("Необходимо слово для проверки")

    flag = True
    for word in collocation:
        flag |= check_word == word.word
        if flag:
            break
    return flag


def is_identical_word(word1: str, word2: str) -> bool:
    """
    Compares 2 words and returns true if these are the same word in different cases
    :type word1: str
    :type word2: str
    :param word1: word number 1
    :param word2: word number 2
    :return: if words are the same & differ from each other in cases

    >>> is_identical_word("огонь", "огня")
    True
    >>> is_identical_word("артиллерии", "артиллерии")
    True
    >>> is_identical_word("слово", "начало")
    False
    >>> is_identical_word("в начале было", "в начале были")
    Traceback (most recent call last):
    ...
    TypeError: Были переданы словосочетания
    >>> is_identical_word("парково-хозяйственный", "парково-хозяйственный")
    True
    >>> is_identical_word('', "огонь")
    False
    >>> is_identical_word("Синий", "огонь артиллерии")
    Traceback (most recent call last):
    ...
    TypeError: Были переданы словосочетания
    >>> is_identical_word("огонь артиллерии", "Синий")
    Traceback (most recent call last):
    ...
    TypeError: Были переданы словосочетания
    >>> is_identical_word(1, "в начале были")
    Traceback (most recent call last):
    ...
    TypeError: Требуется два строковых аргумента
    >>> is_identical_word("123123", "в начале были")
    Traceback (most recent call last):
    ...
    TypeError: Были переданы словосочетания
    >>> is_identical_word("артиллерия", "sda123123")
    Traceback (most recent call last):
    ...
    TypeError: Недопустимое значение аргументов. Необходимы символьные строки
    """
    if not(isinstance(word1, str) and isinstance(word2, str)):
        raise TypeError("Требуется два строковых аргумента")
    if word1 == "" or word2 == "":
        return False
    if len(word1.split(' ')) > 1 or len(word2.split(' ')) > 1:
        raise TypeError("Были переданы словосочетания")
    if not (helpers.is_correct_word(word1) and helpers.is_correct_word(word2)):
        raise TypeError("Недопустимое значение аргументов. Необходимы символьные строки")

    word1 = word1.lower()
    word2 = word2.lower()
    result = word1 == word2
    if not result:
        # TODO у каждого слова уже должны быть тэги к моменту вызова этих строк
        # TODO вызывать этот метод после всех манипуляций с извлечением терминов
        word1_parse_info = tag_collocation(word1)[0]
        word2_parse_info = tag_collocation(word2)[0]
        result = word1_parse_info.normalized == word2_parse_info.normalized
    return result


def get_main_word(collocation: list) -> str:
    """
    Получает главное слово в словосочетании
    :param collocation: словосочетание с тегами
    :return:

    >>> get_main_word([TaggedWord(word="огня", pos=PartOfSpeech.noun, case=Case.genitive, normalized="огонь"), TaggedWord(word="артиллерии", pos=PartOfSpeech.noun, case=Case.genitive, normalized="артиллерия")])
    'огня'
    >>> get_main_word([TaggedWord(word="огонь", pos=PartOfSpeech.noun, case=Case.nominative, normalized="огонь"), TaggedWord(word="артиллерии", pos=PartOfSpeech.noun, case=Case.genitive, normalized="артиллерия")])
    'огонь'
    >>> get_main_word([TaggedWord(word="парково-хозяйственный", pos=PartOfSpeech.adjective, case=Case.nominative, normalized="парково-хозяйственный"), TaggedWord(word="день", pos=PartOfSpeech.noun, case=Case.nominative, normalized="день")])
    'день'
    >>> get_main_word([TaggedWord(word="слушать", pos=PartOfSpeech.verb, case=Case.none, normalized="слушать"), TaggedWord(word="громко", pos=PartOfSpeech.adverb, case=Case.none, normalized="громко")])
    Traceback (most recent call last):
    ...
    ValueError: Словосочетания с глаголами и наречиями не поддерживаются
    """
    # TODO удаление whitespace'ов
    if not isinstance(collocation, list) or len(collocation) == 0 or False in [isinstance(word, TaggedWord) for word in collocation]:
        raise TypeError("Необходим список слов с тегами")

    pos = [word.pos for word in collocation]
    # TODO пока отрабатывать лишь словосочетания сущ+сущ и прил+сущ
    flag = not(PartOfSpeech.verb in pos and PartOfSpeech.adverb in pos)
    if not flag:
        raise ValueError("Словосочетания с глаголами и наречиями не поддерживаются")

    result = ""
    if len(collocation) == 1 and PartOfSpeech.noun in pos:
        result = collocation[0].word
    else:
        nouns = pos.count(PartOfSpeech.noun)
        if nouns == 1:
            for w in collocation:
                if w.pos == PartOfSpeech.noun:
                    result = w.word
        else:
            for w in collocation:
                if w.case == Case.nominative or w.case == Case.accusative:
                    result = w.word
            if result == '':
                nouns = [word for word in collocation if word.pos == PartOfSpeech.noun]
                if len(nouns) != 0:
                    result = nouns[0].word
    return result
    # получаем список частей речи в словосоч. Если одно сущ, остальные прилагательные
    # если сущ+сущ, то или в  и.п., или первое

# TODO при обнаружении в тексте 2х терминов в разных падежах - приводить к одному
# определение из 2, Какое из них в именительном падеже


def is_identical_collocation(collocation1: str, collocation2: str) -> bool:
    """
    Compares 2 collocations and returns true if they represents the same concept but in different cases
    :param collocation1:
    :param collocation2:
    :return: bool value

    >>> is_identical_collocation('огонь артиллерии', 'огня артиллерии')
    True
    >>> is_identical_collocation('', '')
    Traceback (most recent call last):
    ...
    TypeError: Необходимы словосочетания
    >>> is_identical_collocation('plešemo', 'mi plešemo')
    Traceback (most recent call last):
    ...
    TypeError: Необходимы словосочетания
    >>> is_identical_collocation('mi plešemo', 'plešemo')
    Traceback (most recent call last):
    ...
    TypeError: Необходимы словосочетания
    >>> is_identical_collocation('парково-хозяйственный день', 'парково-хозяйственный 6 день')
    Traceback (most recent call last):
    ...
    ValueError: Слова в словосочетаниях должны состоять из букв
    >>> is_identical_collocation('парково-хозяйственный день', 'парково-хо99зяйственный6 день')
    Traceback (most recent call last):
    ...
    ValueError: Слова в словосочетаниях должны состоять из букв
    >>> is_identical_collocation('минометных дивизионов', 'и дивизионов')
    False
    """

    if not(isinstance(collocation1, str) and isinstance(collocation2, str)):
        raise TypeError("Ошибка типов. Необходимы строки")
    words_coll1 = collocation1.split()
    words_coll2 = collocation2.split()
    if len(words_coll1) <= 1 or len(words_coll2) <= 1:
        raise TypeError("Необходимы словосочетания")
    val_check = [helpers.is_correct_word(word) for word in words_coll1 + words_coll2]
    if False in val_check:
        raise ValueError("Слова в словосочетаниях должны состоять из букв")

    if collocation1 == collocation2:
        return True
    word_count_check = len(words_coll1) == len(words_coll2)
    if not word_count_check:
        return False

    collocation1_tagged = tag_collocation(collocation1)
    collocation2_tagged = tag_collocation(collocation2)
    main_word_1 = get_main_word(collocation1_tagged)
    main_word_2 = get_main_word(collocation2_tagged)

    if not is_identical_word(main_word_1, main_word_2):
        return False
    is_identical = True
    for i in range(0, len(collocation1_tagged)):
        is_identical = is_identical and is_identical_word(collocation1_tagged[i].word, collocation2_tagged[i].word)
        if not is_identical:
            break

    return is_identical


def in_collocation_list(collocation: str, collocation_list: list) -> (bool, str):
    # TODO мб возвращать термин в нормальной форме, если попадается в collocation? mainword в и.п.
    """
    Осуществляет проверку наличия словосочетания с списке, учитывая падеж
    :param collocation: словосочетание
    :param collocation_list: список словосочетаний
    :return: да/нет + идентичный элемент

    >>> in_collocation_list('огонь артиллерии', ['основная задача', 'стрелкового оружия', 'огня артиллерии'])
    (True, 'огня артиллерии')
    >>> in_collocation_list('огонь артиллерии', ['основная задача', 'стрелкового оружия', 'артиллерийская подготовка'])
    (False, None)
    >>> in_collocation_list('', ['основная задача', 'стрелкового оружия', 'огня артиллерии'])
    Traceback (most recent call last):
    ...
    ValueError: Необходимо словосочетание для проверки
    >>> in_collocation_list('огонь артиллерии', [])
    (False, None)
    >>> in_collocation_list('и дивизионов', ['командующий войсками армии', 'стрелковых дивизий минометных дивизионов', 'минометных дивизионов',  'боевому применению'])
    (False, None)
    """

    if not isinstance(collocation, str):
        raise TypeError("Ошибка типов. Необходимо словосочетание")
    if not isinstance(collocation_list, list):
        raise TypeError("Ошибка типов. Необходим список словосочетаний")

    words_coll = collocation.split()
    if len(words_coll) <= 1:
        raise ValueError("Необходимо словосочетание для проверки")
    if len(collocation_list) == 0:
        return False, None

    val_check = [helpers.is_correct_word(word) for word in words_coll]
    val_check_coll = [isinstance(coll, str) and False not in [helpers.is_correct_word(coll_word) for coll_word in coll.split()]
                      for coll in collocation_list]
    if False in val_check or False in val_check_coll:
        raise ValueError("Слова в словосочетаниях должны состоять из букв")

    flag = collocation in collocation_list
    found_index = -1
    collocation_list.sort()  # key=lambda x: x
    if not flag:
        identity_check = [is_identical_collocation(collocation, coll) for coll in collocation_list]
        flag = True in identity_check
        if flag:
            found_index = identity_check.index(True)
    return flag, collocation_list[found_index] if found_index > -1 else None


def tag_collocation(collocation: str) -> list:
    """
    Присваивает каждому слову в словосочетании метки части речи и падежа
    :param collocation: словосочетание
    :return: размеченный список слов

    >>> tag_collocation('огонь артиллерии')
    [TaggedWord(word='огонь', pos=<PartOfSpeech.noun: (1, 'S существительное (яблоня, лошадь, корпус, вечность)')>, case=<Case.nominative: (1, 'именительный')>, normalized='огонь'), TaggedWord(word='артиллерии', pos=<PartOfSpeech.noun: (1, 'S существительное (яблоня, лошадь, корпус, вечность)')>, case=<Case.genitive: (2, 'родительный')>, normalized='артиллерия')]

    >>> tag_collocation('парково-хозяйственный день') # отчего-то слово день определяется как слово в винительном падеже
    [TaggedWord(word='парково-хозяйственный', pos=<PartOfSpeech.adjective: (3, 'A  прилагательное (коричневый, таинственный, морской)')>, case=<Case.nominative: (1, 'именительный')>, normalized='парково-хозяйственный'), TaggedWord(word='день', pos=<PartOfSpeech.noun: (1, 'S существительное (яблоня, лошадь, корпус, вечность)')>, case=<Case.accusative: (4, 'винительный')>, normalized='день')]

    >>> tag_collocation('слушать громко')
    [TaggedWord(word='слушать', pos=<PartOfSpeech.verb: (2, 'V глагол (пользоваться, обрабатывать)')>, case=<Case.none: (0,)>, normalized='слушать'), TaggedWord(word='громко', pos=<PartOfSpeech.adverb: (4, 'ADV наречие (сгоряча, очень)')>, case=<Case.none: (0,)>, normalized='громко')]
    """
    words = collocation.split()
    tagged_words = [] # боевая деятельность и все проявления
    for word in words:
        parse_info = __MorphAnalyzer__.parse(word)[0]
        pos = POSNameConverter.to_enum(str(parse_info.tag.POS))
        case = CaseNameConverter.to_enum(str(parse_info.tag.case))
        normalized = parse_info.normal_form
        tagged_words.append(TaggedWord(word=word, pos=pos, case=case, normalized=normalized))

    return tagged_words

# TODO на некоторые слова pymorphy дает несколько вариантов с одинаковыми вероятностями, метод определения?