
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from typing import Literal
import json, random, logging
from pathlib import Path
from my_folders import RESULTS_PATH
from my_lllm import lllm_logger
from .llm_functions import process_side, llm_functions_init, HoleScoreResult
from .validation_dataset import get_validation_dataset
import dotenv

THIS_FOLDER = Path(__file__).resolve().parent
#seeded_rand = random.Random(86442167181706)
#seeded_rand = random.Random(637450176)
seeded_rand = random.Random(1786435477635)

dotenv.load_dotenv()
llm_functions_init() # Call after load_dotenv

@dataclass
class EntrySideResult:
    entry: dict
    side: Literal['A', 'B']
    result: list[HoleScoreResult]

dataset = get_validation_dataset()
seeded_rand.shuffle(dataset)

def process_entry_side(entry, side):
    return lambda: EntrySideResult(entry, side, process_side(entry, side))

all_tasks = [
    process_entry_side(entry, side) # Direct lambda had capture issues
    for entry in dataset
    for side in ('A', 'B')
]

lllm_logger.setLevel(logging.ERROR)

with (RESULTS_PATH / 'result_on_validation.jsonl').open('w', encoding='utf-8') as fp:
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
