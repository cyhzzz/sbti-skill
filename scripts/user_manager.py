"""SBTI 用户身份管理"""
import storage

def identify_or_register(name: str = None) -> tuple[str, dict]:
    """
    根据姓名查找或注册用户。
    返回 (uid, user_info)
    如果 name 为 None，生成匿名 UID。
    """
    if name:
        # 简单姓名匹配（未来可升级为更复杂匹配）
        users = storage.list_users()
        for u in users:
            if u.get("name") == name:
                full = storage.get_user(u["uid"])
                return u["uid"], full
        # 未找到，注册
        uid = f"user_{len(users) + 1}"
        storage.register_user(uid, name)
        full = storage.get_user(uid)
        return uid, full
    else:
        # 匿名用户
        import uuid
        uid = f"anon_{uuid.uuid4().hex[:8]}"
        storage.register_user(uid, "匿名用户")
        full = storage.get_user(uid)
        return uid, full


def list_all_users() -> list[dict]:
    return storage.list_users()


def get_user_history(uid: str) -> list[dict]:
    return storage.get_records(uid)
