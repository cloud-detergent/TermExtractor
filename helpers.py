import string

def concat_words(words: list, delimiter=' ') -> str:
    """
    Соединяет слова по разделителю
    :param words: список слов
    :param delimiter:
    :return: словосочетание

    >>> concat_words([ 'оптический', 'привод' ]  )
    'оптический привод'
    >>> concat_words([ 'высокооборотистый', 'оптический', 'привод' ], '-')
    'высокооборотистый-оптический-привод'
    >>> concat_words([ 'привод'])
    'привод'
    >>> concat_words([])
    ''
    """
    flag = False in [isinstance(word, str) for word in words]
    if flag:
        raise ValueError("Необходим список строк")
    if len(words) == 0:
        return ""
    if len(words) == 1:
        return words[0]
    result = ""
    for word in words[0:len(words)-1]:
        if word != "":
            result += "{0}{1}".format(word, delimiter)
    result += words[-1]
    return result


def remove_spans(term: str, spans: list) -> str:
    """
    Удаляет из строки слова, включенные в стоп-список
    :param term: термин
    :param spans: список интервалов
    :return: отредактированный термин
    >>> remove_spans('белый высокооборотистый оптический привод', [(1, 5)])
    'высокооборотистый оптический привод'
    >>> remove_spans('новое высокоэтажное быстрое строительство', [(1, 5), (20, 27)])
    'высокоэтажное строительство'

    """
    # TODO протестировать
    flag = False in [isinstance(span, tuple) and len(span) == 2 and isinstance(span[0], int)
                     and isinstance(span[1], int) and span[0] < span[1] for span in spans]
    if flag:
        raise ValueError("Требуется список интервалов, упакованных в кортежи")
    allowed_spans = []
    max_len = len(term)
    for i in range(0, len(spans)):
        if i == 0 and spans[i][0] > 1:
            allowed_spans.append((1, spans[i][0]))
        elif i == len(spans) - 1 and spans[i][1]< max_len:
            allowed_spans.append((spans[i][1], max_len))
        else:
            allowed_spans.append((spans[i][1], spans[i+1][0]))

    parts = [term[span[0]: span[1]] for span in allowed_spans]
    edited_term = concat_words(parts)
    while edited_term[0] in string.whitespace:
        edited_term = edited_term[1:]
    while '  ' in edited_term:
        edited_term = edited_term.replace('  ', ' ')
    return edited_term
