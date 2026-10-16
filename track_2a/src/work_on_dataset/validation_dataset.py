from datasets import load_dataset

def dataitem2example(item):
    return {
        'id': item['id'], 'lang_A_id': 'en', 'lang_B_id': item['subset'].split('_')[1].upper(),
        'text_A': item['text_a_untokenized'], 'text_B': item['text_b_untokenized'],
        'labels_A': item['labels_a'], 'labels_B': item['labels_b'],
        'tk_A': item['text_a'], 'tk_B': item['text_b'],
    }

def get_validation_dataset():
    print('Loading dataset...')
    validarion_dataset = [ dataitem2example(item) for item in load_dataset('ZurichNLP/SwissGov-RSD', split='validation') ]
    print(f'Loaded {len(validarion_dataset)} entries from table')
    return validarion_dataset

def get_test_dataset():
    print('Loading dataset... ### TEST SPLIT: DO NOT USE FOR TRAINING ###')
    test_dataset = [ dataitem2example(item) for item in load_dataset('ZurichNLP/SwissGov-RSD', split='test') ]
    print(f'Loaded {len(test_dataset)} entries from table')
    return test_dataset
