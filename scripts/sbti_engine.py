"""SBTI 核心算法：计分 + 类型匹配"""
import json
import os
import random

SKILL_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF_DIR = os.path.join(SKILL_BASE, "references")

def _load_json(name: str):
    with open(os.path.join(REF_DIR, name), "r", encoding="utf-8") as f:
        return json.load(f)


def sum_to_level(score: int) -> str:
    if score <= 3:
        return "L"
    if score == 4:
        return "M"
    return "H"


def level_num(level: str) -> int:
    return {"L": 1, "M": 2, "H": 3}[level]


def parse_pattern(pattern: str) -> list[int]:
    return [level_num(c) for c in pattern.replace("-", "")]


def compute_result(answers: dict) -> dict:
    """
    answers: {question_id: selected_value}
    返回完整结果字典
    """
    dim_meta = _load_json("dimension-library.json")
    type_lib = _load_json("type-library.json")
    questions_data = _load_json("questions.json")

    questions = questions_data["questions"]
    special_questions = questions_data["specialQuestions"]
    dimension_order = dim_meta["dimensionOrder"]
    dimensions = dim_meta["dimensions"]
    DRUNK_TRIGGER_Q = "drink_gate_q2"

    # 收集题目（打乱顺序插入关卡题）
    shuffled_qs = questions.copy()
    random.shuffle(shuffled_qs)
    insert_idx = random.randint(0, len(shuffled_qs))
    visible_qs = shuffled_qs[:insert_idx] + [special_questions[0]] + shuffled_qs[insert_idx:]

    # 计算原始分数
    raw_scores = {d: 0 for d in dimension_order}
    for q in questions:
        val = answers.get(q["id"])
        if val is not None:
            raw_scores[q["dim"]] += val

    # 计算级别
    levels = {d: sum_to_level(raw_scores[d]) for d in dimension_order}

    # 用户向量
    user_vector = [level_num(levels[d]) for d in dimension_order]

    # 匹配类型
    ranked = []
    for code, t in type_lib.items():
        if code in ("HHHH", "DRUNK"):
            continue  # 特殊类型不参与常规匹配
        vector = parse_pattern(t["pattern"])
        distance = sum(abs(user_vector[i] - vector[i]) for i in range(len(vector)))
        exact = sum(1 for i in range(len(vector)) if user_vector[i] == vector[i])
        similarity = max(0, round((1 - distance / 30) * 100))
        ranked.append({
            "code": code,
            "cn": t["cn"],
            "distance": distance,
            "exact": exact,
            "similarity": similarity
        })

    ranked.sort(key=lambda x: (x["distance"], -x["exact"], -x["similarity"]))
    best_normal = ranked[0]

    # 特殊触发判断
    drunk_triggered = answers.get(DRUNK_TRIGGER_Q) == 2
    special = False
    final_code = best_normal["code"]

    if drunk_triggered:
        final_code = "DRUNK"
        special = True
    elif best_normal["similarity"] < 60:
        final_code = "HHHH"
        special = True

    final_type = type_lib[final_code]

    # 构建返回结果
    dim_details = []
    for d in dimension_order:
        dim_details.append({
            "dim": d,
            "name": dimensions[d]["name"],
            "level": levels[d],
            "score": raw_scores[d],
            "explanation": dimensions[d]["explanation"][levels[d]]
        })

    result = {
        "type_code": final_code,
        "type_cn": final_type["cn"],
        "type_intro": final_type["intro"],
        "type_desc": final_type["desc"],
        "image_path": f"./image/{final_code}.png",
        "is_special": special,
        "mode_kicker": "隐藏人格已激活" if drunk_triggered else ("系统强制兜底" if special else "你的主类型"),
        "badge": (
            "匹配度 100% · 酒精异常因子已接管" if drunk_triggered else
            f"标准人格库最高匹配仅 {best_normal['similarity']}%" if special else
            f"匹配度 {best_normal['similarity']}% · 精准命中 {best_normal['exact']}/15 维"
        ),
        "sub": (
            "乙醇亲和性过强，系统已直接跳过常规人格审判。" if drunk_triggered else
            "标准人格库对你的脑回路集体罢工了。" if special else
            "维度命中度较高，当前结果可视为你的第一人格画像。"
        ),
        "best_normal": {
            "code": best_normal["code"],
            "cn": type_lib[best_normal["code"]]["cn"],
            "similarity": best_normal["similarity"],
            "exact": best_normal["exact"]
        },
        "dimensions": dim_details,
        "answers": answers
    }

    return result
