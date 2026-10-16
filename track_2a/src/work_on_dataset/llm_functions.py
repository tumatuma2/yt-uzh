import os
from typing import Literal, TypedDict
from dataclasses import dataclass

from .segmenter import get_segmenter
from .common_re import RE_ANY_LETTER
from .segment_matching import shared_segments

from my_lllm import Message, MyLLLM, my_lllm_init
from assistent_prob import AssistentProb_ChatParams, getAssistentProb

# @TODO: This works only with unique ids in all datasets!!!
from .cache import HoleScoreCache, HoleScoreKey, HoleScoreResult
shared_cache = HoleScoreCache()

lmTarget: MyLLLM | None = None

def llm_functions_init(): # DO AFTER LOAD DOTENV
    global lmTarget

    my_lllm_init()

    lmTarget = MyLLLM(
        model=os.environ['LLM_NAME'],

        **AssistentProb_ChatParams,
    )

class MyInput(TypedDict):
    original: str
    new_prefix: str
    new_suffix: str
class MyInputWithTarget(MyInput):
    new_middle: str

def genPrompt(x: MyInputWithTarget) -> list[Message]:
    return [
        { 'role': 'system', 'content': 'Fill the appropriate part of speach in the translated text so it mantains the same meaning as original. Do not output any explaination or text or extra content except the required filling words', },
        { 'role': 'user', 'content': f'[ ## original text ## ]\n{x['original']}\n\n[ ## new text prefix ## ]\n{x['new_prefix']}\n\n[ ## new text suffix ## ]\n{x['new_suffix']}', },
        { 'role': 'assistant', 'content': f'{x['new_middle']}', },
    ]

def process_side(item, hole_src: Literal['A', 'B']):
    global lmTarget, shared_cache

    other_src = { 'A': 'B', 'B': 'A' }[hole_src]
    segmenter = get_segmenter(item[f'lang_{hole_src}_id'])
    seg_text = segmenter.segment(item[f'text_{hole_src}'])
    other_text = item[f'text_{other_src}']

    valid_hole_idxs = [ idx for idx, hole_text in enumerate(seg_text) if RE_ANY_LETTER.match(hole_text) is not None ]

    our_holes_to_theirs = shared_segments(seg_text, item[f'tk_{hole_src}'].split(' '))
    res: list[HoleScoreResult] = []

    for hole_idx in valid_hole_idxs:
        key = HoleScoreKey(item['id'], hole_src, hole_idx)

        value = shared_cache.get(key)
        if value is not None:
            print(f'Duplicate work, pruning {key} task')
        else:
            myin = MyInputWithTarget(
                original=other_text,
                new_prefix=' '.join(seg_text[:hole_idx]) + ' ',
                new_middle=seg_text[hole_idx],
                new_suffix=' ' + ' '.join(seg_text[hole_idx+1:]),
            )

            assert lmTarget is not None, 'Initialize llm_functions before processing'
            print(f'Processing: {item['id']} | {hole_src} | {hole_idx}')
            assistant_lprob, _ = getAssistentProb(lmTarget, genPrompt(myin))

            value = HoleScoreResult(tks_idx=our_holes_to_theirs[hole_idx], score=assistant_lprob)
            shared_cache.put(key, value)

        res.append(value)

    return res
