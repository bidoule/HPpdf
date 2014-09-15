
from collections import namedtuple

Group = namedtuple('Group', 'name lines')

CONFIG = {
    'GB1': Group('', [(1, 9)]),
    '<Adaptation> Ada 1': Group('Ada 1', [(1, 2)]),
    '<Adaptation> Ada 2': Group('Ada 2', [(3, 4)]),
    '<Adaptation> Ada 3': Group('Ada 3', [(5, 6)]),
    '<Adaptation> Ada 4': Group('Ada 4', [(7, 8)]),
    '<OPTIONS> ABB': Group('ABB', [(1, 3)]),
    '<OPTIONS> Agro': Group('Agro', [(4, 5)]),
    '<OPTIONS> GE': Group('GE', [(6,9)]),
    '<TP S1> TP 1': Group('TP 1', [(1, 1)]),
    '<TP S1> TP 2': Group('TP 2', [(2, 2)]),
    '<TP S1> TP 3': Group('TP 3', [(3, 3)]),
    '<TP S1> TP 4': Group('TP 4', [(4, 4)]),
    '<TP S1> TP 5': Group('TP 5', [(5, 5)]),
    '<TP S1> TP 6': Group('TP 6', [(6, 6)]),
    '<TP S1> TP 7': Group('TP 7', [(7, 7)]),
    '<TP S1> TP 8': Group('TP 8', [(8, 8)]),
    '<TP S1> TP 9': Group('TP 9', [(9, 9)]),
    '<TD S1> TD 1-2': Group('TD 1-2', [(1, 2)]),
    '<TD S1> TD 3-4': Group('TD 3-4', [(3, 4)]),
    '<TD S1> TD 5-6': Group('TD 5-6', [(5, 6)]),
    '<TD S1> TD 7-8': Group('TD 7-8', [(7, 8)]),
    '<TD S1> TD 9': Group('TD 9', [(9, 9)]),
}
