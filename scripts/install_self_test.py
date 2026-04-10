"""SBTI 安装自检脚本：在 skill 首次安装/初始化时，Agent 自己做一遍测试并上报结果"""
import json, random, sys, os

SKILL_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(SKILL_BASE, 'scripts'))

import sbti_engine, storage

AGENT_UID = "agent_self"
AGENT_NAME = "Claude Agent"


def run_self_test():
    """Agent 自己完整做一遍 SBTI，返回结果 dict"""
    # 加载题库
    qdata = sbti_engine._load_json('questions.json')
    questions = qdata['questions']
    special_qs = qdata['specialQuestions']

    # Agent 模拟答题：用均衡策略（避免极端人格）
    # 策略：每题选中间值(2)，这样不会触发极端类型
    answers = {}
    for q in questions:
        answers[q['id']] = 2  # 全部中立

    # 特殊题：不爱喝酒
    answers['drink_gate_q1'] = 1
    if 'drink_gate_q2' in [sq['id'] for sq in special_qs]:
        answers['drink_gate_q2'] = 1

    result = sbti_engine.compute_result(answers)
    return result


def save_self_test_result():
    """保存 Agent 自测结果，返回 (type_code, type_cn, result_dict)"""
    result = run_self_test()

    # 注册/读取 agent 用户
    users = storage.list_users()
    for u in users:
        if u['uid'] == AGENT_UID:
            user = storage.get_user(AGENT_UID)
            break
    else:
        user = storage.register_user(AGENT_UID, AGENT_NAME)
        user = storage.get_user(AGENT_UID)

    # 追加记录（带标记）
    record = {
        **result,
        'is_agent_self': True
    }
    storage.add_record(AGENT_UID, record)

    return result['type_code'], result['type_cn'], result


def get_self_test_result():
    """获取已保存的 Agent 自测结果，没有则返回 None"""
    records = storage.get_records(AGENT_UID)
    if records:
        return records[-1]
    return None


if __name__ == '__main__':
    # CLI 模式：运行自检并输出结果摘要
    code, cn, result = save_self_test_result()
    print(json.dumps({
        'type_code': code,
        'type_cn': cn,
        'intro': result.get('type_intro', ''),
        'similarity': result['best_normal']['similarity'],
        'is_special': result.get('is_special', False),
        'badge': result.get('badge', ''),
        'image_path': result.get('image_path', '')
    }, ensure_ascii=False, indent=2))
