def test_types(substructure, keyname=''):
    if isinstance(substructure, list):
        type_list = [type(x) for x in substructure]
    pass