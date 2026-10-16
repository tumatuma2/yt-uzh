from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
import random, json
from typing import Literal
from my_folders import RESULTS_PATH
from .llm_functions import process_side, llm_functions_init, HoleScoreResult
from .validation_dataset import get_validation_dataset, get_test_dataset
import dotenv

import argparse
ap = argparse.ArgumentParser()
ap.add_argument('--seed', default='1B3C5D7E9FA1B2C3', help='Seed to use for random picks')
ap.add_argument('--limit', default=10, help='Number of entries in the dataset to process')
ap.add_argument('--test', action='store_true', help='Run on test split')
ap_data = ap.parse_args()

TASK_LIMIT = ap_data.limit
RUN_ON_TEST = ap_data.test

RNG_SEED = ap_data.seed
seeded_rand = random.Random(bytes.fromhex(RNG_SEED))

dotenv.load_dotenv()
llm_functions_init() # Call after load_dotenv

@dataclass
class EntrySideResult:
    entry: dict
    side: Literal['A', 'B']
    result: list[HoleScoreResult]

dataset = get_test_dataset() if RUN_ON_TEST else get_validation_dataset()
seeded_rand.shuffle(dataset)

def process_entry_side(entry, side):
    return lambda: EntrySideResult(entry, side, process_side(entry, side))

all_tasks = [
    process_entry_side(entry, side) # Direct lambda had capture issues
    for entry in dataset
    for side in ('A', 'B')
]
if TASK_LIMIT > 0:
    all_tasks = all_tasks[:TASK_LIMIT]

with (RESULTS_PATH / ('result_on_test.jsonl' if RUN_ON_TEST else 'result_on_validation.jsonl')).open('w', encoding='utf-8') as fp:
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [
            executor.submit(task)
            for task in all_tasks
        ]

        for future in as_completed(futures):
            try:
                x = future.result()
            except Exception as e:
                print(f'[ERROR] FUTURE FAILED: {e}')
                continue
            fp.write(f'{json.dumps(asdict(x))}\n')
            fp.flush()
