#!/usr/bin/env python3
"""机器人测试评估报告生成工具"""

import os
import sys
import json
from datetime import datetime

# 路径配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
EVAL_STANDARD_PATH = os.path.join(BASE_DIR, "评测标准V2.md")
REPORT_DIR = "/Users/imoolan/antcc/robot-tester/report"


def generate_report(test_info, chat_history, evaluation_result):
    """
    生成评估报告

    Args:
        test_info: 测试基本信息 dict
        chat_history: 聊天记录列表
        evaluation_result: 评估结果 dict

    Returns:
        报告文件路径
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"report_{timestamp}.md"
    report_path = os.path.join(REPORT_DIR, report_filename)

    # 确保报告目录存在
    os.makedirs(REPORT_DIR, exist_ok=True)

    # 构建报告内容
    report = []

    # 标题
    report.append("# 机器人测试评估报告\n\n")

    # 测试信息
    report.append("## 测试信息\n\n")
    report.append("| 项目 | 内容 |\n")
    report.append("|------|------|\n")
    report.append(f"| 测试时间 | {test_info.get('test_time', '')} |\n")
    report.append(f"| 机器人代码 | {test_info.get('robot_code', '')} |\n")
    report.append(f"| 用户身份 | {test_info.get('user_identity', '')} |\n")
    report.append(f"| 模拟场景 | {test_info.get('scenario', '')} |\n")
    report.append(f"| 测试轮次 | {test_info.get('rounds', '')}轮 |\n")
    report.append("\n---\n\n")

    # 聊天记录
    report.append("## 聊天记录\n\n")
    report.append("| 轮次 | 用户 | 机器人 | answerCode |\n")
    report.append("|------|------|--------|------------|\n")

    for chat in chat_history:
        round_num = chat.get('round', '')
        user_msg = chat.get('user', '-')
        bot_msg = chat.get('bot', '').replace('\n', ' ')[:50] + ('...' if len(chat.get('bot', '')) > 50 else '')
        answer_code = chat.get('answerCode', '-')

        if round_num == '欢迎语':
            report.append(f"| 欢迎语 | - | {bot_msg} | {answer_code} |\n")
        else:
            report.append(f"| {round_num} | {user_msg[:30]}{'...' if len(user_msg) > 30 else ''} | {bot_msg} | {answer_code} |\n")

    report.append("\n---\n\n")

    # 评测结果
    report.append("## 评测结果\n\n")

    # 风险类评测
    report.append("### 风险类评测\n\n")
    report.append("| 维度 | 结果 | 详情 |\n")
    report.append("|------|------|------|\n")

    risk_eval = evaluation_result.get('risk', {})
    for dim, result in risk_eval.items():
        status = "✅ 通过" if result.get('passed', True) else "❌ 不通过"
        detail = result.get('detail', '')
        report.append(f"| {dim} | {status} | {detail} |\n")

    report.append("\n")

    # 能力类评测
    report.append("### 能力类评测\n\n")
    report.append("| 维度 | 评分 | 说明 |\n")
    report.append("|------|------|------|\n")

    ability_eval = evaluation_result.get('ability', {})
    for dim, result in ability_eval.items():
        score = result.get('score', 0)
        stars = "⭐" * score + "☆" * (5 - score)
        desc = result.get('description', '')
        report.append(f"| {dim} | {stars} ({score}/5) | {desc} |\n")

    report.append("\n---\n\n")

    # 综合评分
    report.append("## 综合评分\n\n")
    report.append("| 类别 | 得分 |\n")
    report.append("|------|------|\n")

    risk_passed = all(r.get('passed', True) for r in risk_eval.values())
    risk_status = "✅ 全部通过" if risk_passed else "❌ 存在问题"
    report.append(f"| 风险类评测 | {risk_status} |\n")

    avg_ability = sum(r.get('score', 0) for r in ability_eval.values()) / len(ability_eval) if ability_eval else 0
    report.append(f"| 能力类评测 | {avg_ability:.1f}/5.0 |\n")
    report.append(f"| **综合评分** | **{avg_ability:.1f}/5.0** |\n")

    report.append("\n---\n\n")

    # 问题汇总
    report.append("## 问题汇总\n\n")
    issues = evaluation_result.get('issues', [])
    if issues:
        report.append("| 问题类型 | 出现次数 | 具体轮次 |\n")
        report.append("|---------|---------|---------|\n")
        for issue in issues:
            report.append(f"| {issue.get('type', '')} | {issue.get('count', 0)}次 | {issue.get('rounds', '')} |\n")
    else:
        report.append("无重大问题发现。\n")

    report.append("\n---\n\n")

    # 改进建议
    report.append("## 改进建议\n\n")
    suggestions = evaluation_result.get('suggestions', [])
    if suggestions:
        for i, sug in enumerate(suggestions, 1):
            report.append(f"{i}. {sug}\n")
    else:
        report.append("暂无改进建议。\n")

    # 写入文件
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(''.join(report))

    return report_path


def main():
    """命令行入口 - 用于测试"""
    test_info = {
        "test_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "robot_code": "ROB00029078",
        "user_identity": "新手小白",
        "scenario": "尺码咨询",
        "rounds": 10
    }

    chat_history = [
        {"round": "欢迎语", "bot": "您好，欢迎光临", "answerCode": "WELCOME"},
        {"round": "第1轮", "user": "尺码怎么选", "bot": "建议按平时码数购买", "answerCode": "GENERATE"},
    ]

    evaluation_result = {
        "risk": {
            "服务底线": {"passed": True, "detail": ""},
            "暴露机器人": {"passed": True, "detail": ""},
            "服务态度": {"passed": True, "detail": ""}
        },
        "ability": {
            "意图识别": {"score": 4, "description": "能准确识别用户意图"},
            "解答完整": {"score": 3, "description": "部分回答不够完整"}
        },
        "issues": [
            {"type": "空回复", "count": 1, "rounds": "第3轮"}
        ],
        "suggestions": ["建议优化空回复问题"]
    }

    report_path = generate_report(test_info, chat_history, evaluation_result)
    print(f"报告已生成: {report_path}")


if __name__ == "__main__":
    main()