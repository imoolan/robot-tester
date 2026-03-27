#!/usr/bin/env python3
"""客服机器人测试工具 - 对话接口调用脚本"""

import sys
import json
import time
import requests

API_URL = "https://isportal-ws-pre.antgroup.com/proxy/isagentcore/robot/test/runBatch.json"
REFERER = "https://box-agent-pre.antgroup.com/"
HEADERS = {
    "Content-Type": "application/json",
    "Referer": REFERER
}

# 默认参数
DEFAULT_PARAMS = {
    "urId": "1099000000047269953",
    "token": "3be12435-9f79-4398-9e2b-0320b5646b10",
    "visitorSourceId": "2787129059"
}


def create_session(robot_code: str) -> dict:
    """创建会话"""
    session_id = f"test_session_{int(time.time())}"
    payload = {
        "robotCode": robot_code,
        "sessionId": session_id,
        "action": "START_SESSION",
        "senderType": "SYSTEM",
        **DEFAULT_PARAMS
    }
    resp = requests.post(API_URL, headers=HEADERS, json=payload)
    data = resp.json()
    if data.get("success"):
        return {
            "success": True,
            "sessionId": data["data"].get("sessionUuId"),
            "welcomeText": data["data"].get("commonText"),
            "answerCode": data["data"].get("answerCode")
        }
    return {"success": False, "error": data.get("message")}


def chat(robot_code: str, session_id: str, query: str) -> dict:
    """发送对话消息"""
    payload = {
        "robotCode": robot_code,
        "sessionId": session_id,
        "query": query,
        "action": "CHAT",
        "senderType": "USER",
        **DEFAULT_PARAMS
    }
    resp = requests.post(API_URL, headers=HEADERS, json=payload)
    data = resp.json()
    if data.get("success"):
        return {
            "success": True,
            "reply": data["data"].get("commonText", ""),
            "answerCode": data["data"].get("answerCode"),
            "answerType": data["data"].get("answerType")
        }
    return {"success": False, "error": data.get("message")}


def close_session(robot_code: str, session_id: str) -> dict:
    """关闭会话"""
    payload = {
        "robotCode": robot_code,
        "sessionId": session_id,
        "action": "CLOSE_SESSION",
        "senderType": "SYSTEM",
        **DEFAULT_PARAMS
    }
    resp = requests.post(API_URL, headers=HEADERS, json=payload)
    data = resp.json()
    return {"success": data.get("success", False)}


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: robot_chat.py <action> [args...]"}, ensure_ascii=False))
        sys.exit(1)

    action = sys.argv[1]

    if action == "create":
        # 创建会话: python robot_chat.py create <robot_code>
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Missing robot_code"}, ensure_ascii=False))
            sys.exit(1)
        result = create_session(sys.argv[2])
        print(json.dumps(result, ensure_ascii=False))

    elif action == "chat":
        # 对话: python robot_chat.py chat <robot_code> <session_id> <query>
        if len(sys.argv) < 5:
            print(json.dumps({"error": "Usage: robot_chat.py chat <robot_code> <session_id> <query>"}, ensure_ascii=False))
            sys.exit(1)
        result = chat(sys.argv[2], sys.argv[3], sys.argv[4])
        print(json.dumps(result, ensure_ascii=False))

    elif action == "close":
        # 关闭会话: python robot_chat.py close <robot_code> <session_id>
        if len(sys.argv) < 4:
            print(json.dumps({"error": "Missing parameters"}, ensure_ascii=False))
            sys.exit(1)
        result = close_session(sys.argv[2], sys.argv[3])
        print(json.dumps(result, ensure_ascii=False))

    else:
        print(json.dumps({"error": f"Unknown action: {action}"}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()