#!/usr/bin/env python3
"""사용자 정의 전략 모음"""
import random

USER_STRATEGIES = {}


def strategy_3의_배수(data, round_num):
    """3의_배수: 3의 배수 번호 중심 선택 전략"""
    # 3의 배수 번호 중심 선택
    multiples_of_3 = [n for n in range(3, 46, 3)]  # [3,6,9,...,45]
    others = [n for n in range(1, 46) if n % 3 != 0]

    # 3의 배수 4개 + 나머지 2개
    selected = random.sample(multiples_of_3, 4)
    selected += random.sample(others, 2)
    return sorted(selected)

USER_STRATEGIES['3의_배수'] = strategy_3의_배수
