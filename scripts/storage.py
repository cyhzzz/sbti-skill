"""SBTI 数据持久化：用户记录读写"""
import json
import os
from datetime import datetime

SKILL_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(SKILL_BASE, "data")
os.makedirs(DATA_DIR, exist_ok=True)

USER_LIST_FILE = os.path.join(DATA_DIR, "users.json")


def _user_file(uid: str) -> str:
    return os.path.join(DATA_DIR, f"{uid}.json")


def list_users() -> list[dict]:
    """返回所有用户列表（不含敏感信息）"""
    if not os.path.exists(USER_LIST_FILE):
        return []
    with open(USER_LIST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def register_user(uid: str, name: str) -> dict:
    """注册新用户（写入 users.json + 创建 data/{uid}.json）"""
    users = list_users()
    for u in users:
        if u["uid"] == uid:
            user = get_user(uid)
            if user is not None:
                return user
            # data 文件丢失，从 users.json 重建
            user = {"uid": uid, "name": u["name"], "created_at": u["created_at"], "records": []}
            save_user(user)
            return user
    user = {
        "uid": uid,
        "name": name,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "records": []
    }
    users.append({"uid": uid, "name": name, "created_at": user["created_at"]})
    with open(USER_LIST_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    save_user(user)  # 创建单独的 data/{uid}.json
    return user


def get_user(uid: str) -> dict | None:
    """读取用户完整记录"""
    path = _user_file(uid)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_user(user: dict) -> None:
    """保存用户完整记录"""
    path = _user_file(user["uid"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(user, f, ensure_ascii=False, indent=2)


def add_record(uid: str, record: dict) -> dict:
    """追加一条测试记录"""
    user = get_user(uid)
    if user is None:
        raise ValueError(f"用户 {uid} 不存在")
    record["taken_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user["records"].append(record)
    save_user(user)
    return record


def get_records(uid: str) -> list[dict]:
    """获取用户所有历史记录"""
    user = get_user(uid)
    if user is None:
        return []
    return user.get("records", [])
