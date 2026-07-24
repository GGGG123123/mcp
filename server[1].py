# -*- coding: utf-8 -*-
"""
实验4-4-b：业务场景Schema设计（FastMCP）

包含两个工具：
1. query_employees：员工信息组合查询、分页、排序
2. batch_send_notifications：批量、多渠道、模板、定时通知

安装：
    pip install fastmcp

运行：
    python 4-4-b_schema_tools.py

平台配置：
    类型：可流式传输的HTTP
    URL：http://你的电脑局域网IP:8001/mcp
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from fastmcp import FastMCP


mcp = FastMCP("实验4-4-b业务场景Schema工具")


EMPLOYEE_DATA: List[Dict[str, Any]] = [
    {
        "employee_id": "E001",
        "name": "张三",
        "department": "技术部",
        "position": "Python开发工程师",
        "salary": 12000.0,
    },
    {
        "employee_id": "E002",
        "name": "李四",
        "department": "技术部",
        "position": "测试工程师",
        "salary": 10000.0,
    },
    {
        "employee_id": "E003",
        "name": "王五",
        "department": "市场部",
        "position": "市场专员",
        "salary": 9000.0,
    },
    {
        "employee_id": "E004",
        "name": "赵六",
        "department": "人力资源部",
        "position": "招聘专员",
        "salary": 8500.0,
    },
    {
        "employee_id": "E005",
        "name": "陈晨",
        "department": "技术部",
        "position": "Java开发工程师",
        "salary": 13500.0,
    },
    {
        "employee_id": "E006",
        "name": "刘洋",
        "department": "财务部",
        "position": "会计",
        "salary": 9500.0,
    },
]


@mcp.tool()
def query_employees(
    name: Optional[str] = None,
    department: Optional[str] = None,
    position: Optional[str] = None,
    min_salary: Optional[float] = None,
    max_salary: Optional[float] = None,
    page: int = 1,
    page_size: int = 10,
    sort_field: Literal[
        "employee_id",
        "name",
        "department",
        "position",
        "salary",
    ] = "employee_id",
    sort_order: Literal["asc", "desc"] = "asc",
) -> Dict[str, Any]:
    """
    根据姓名、部门、职位和薪资范围组合查询员工信息。

    参数：
        name: 可选员工姓名，支持关键字模糊查询。
        department: 可选部门名称，支持关键字查询。
        position: 可选职位名称，支持关键字查询。
        min_salary: 可选最低薪资，必须大于或等于0。
        max_salary: 可选最高薪资，必须大于或等于0。
        page: 当前页码，从1开始，默认1。
        page_size: 每页记录数，范围1～100，默认10。
        sort_field: 排序字段，仅允许employee_id、name、
                    department、position、salary。
        sort_order: 排序方向，仅允许asc或desc。

    返回：
        包含success、total、page、page_size、total_pages、
        data和error字段。
    """
    try:
        if page < 1:
            return {
                "success": False,
                "total": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0,
                "data": [],
                "error": "page必须大于或等于1",
            }

        if page_size < 1 or page_size > 100:
            return {
                "success": False,
                "total": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0,
                "data": [],
                "error": "page_size必须在1～100之间",
            }

        if min_salary is not None and min_salary < 0:
            return {
                "success": False,
                "total": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0,
                "data": [],
                "error": "min_salary不能小于0",
            }

        if max_salary is not None and max_salary < 0:
            return {
                "success": False,
                "total": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0,
                "data": [],
                "error": "max_salary不能小于0",
            }

        if (
            min_salary is not None
            and max_salary is not None
            and min_salary > max_salary
        ):
            return {
                "success": False,
                "total": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0,
                "data": [],
                "error": "min_salary不能大于max_salary",
            }

        result = EMPLOYEE_DATA.copy()

        if name and name.strip():
            keyword = name.strip().lower()
            result = [
                employee
                for employee in result
                if keyword in employee["name"].lower()
            ]

        if department and department.strip():
            keyword = department.strip().lower()
            result = [
                employee
                for employee in result
                if keyword in employee["department"].lower()
            ]

        if position and position.strip():
            keyword = position.strip().lower()
            result = [
                employee
                for employee in result
                if keyword in employee["position"].lower()
            ]

        if min_salary is not None:
            result = [
                employee
                for employee in result
                if employee["salary"] >= min_salary
            ]

        if max_salary is not None:
            result = [
                employee
                for employee in result
                if employee["salary"] <= max_salary
            ]

        result.sort(
            key=lambda employee: employee[sort_field],
            reverse=(sort_order == "desc"),
        )

        total = len(result)
        total_pages = (
            (total + page_size - 1) // page_size
            if total > 0
            else 0
        )

        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        page_data = result[start_index:end_index]

        return {
            "success": True,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "sort_field": sort_field,
            "sort_order": sort_order,
            "data": page_data,
            "error": None,
        }

    except Exception as exc:
        return {
            "success": False,
            "total": 0,
            "page": page,
            "page_size": page_size,
            "total_pages": 0,
            "data": [],
            "error": f"员工信息查询失败：{str(exc)}",
        }


NOTIFICATION_TEMPLATES: Dict[str, str] = {
    "审批通知": "您有一条新的审批任务，请及时处理。",
    "会议提醒": "您有一场即将开始的会议，请按时参加。",
    "系统公告": "系统发布了一条新的公告，请及时查看。",
}


@mcp.tool()
def batch_send_notifications(
    recipients: List[Dict[str, str]],
    title: str,
    body: str,
    channels: List[Literal["email", "sms", "internal"]],
    template: Optional[
        Literal["审批通知", "会议提醒", "系统公告"]
    ] = None,
    scheduled_at: Optional[str] = None,
) -> Dict[str, Any]:
    """
    通过多个渠道向多个收件人批量发送通知。

    参数：
        recipients: 收件人列表，每个元素必须是字典，可包含：
                    recipient_id、name、email、phone、internal_id。
        title: 通知标题，不能为空。
        body: 通知正文，不能为空。
        channels: 发送渠道列表，只允许email、sms、internal。
        template: 可选模板，只允许审批通知、会议提醒、系统公告。
        scheduled_at: 可选定时发送时间，格式YYYY-MM-DD HH:MM:SS；
                      None表示立即发送。

    返回：
        包含success、send_mode、total_recipients、total_tasks、
        success_count、failure_count、results和error字段。
    """
    try:
        if not recipients:
            return {
                "success": False,
                "send_mode": None,
                "scheduled_at": scheduled_at,
                "total_recipients": 0,
                "total_tasks": 0,
                "success_count": 0,
                "failure_count": 0,
                "results": [],
                "error": "收件人列表不能为空",
            }

        if not all(isinstance(item, dict) for item in recipients):
            return {
                "success": False,
                "send_mode": None,
                "scheduled_at": scheduled_at,
                "total_recipients": 0,
                "total_tasks": 0,
                "success_count": 0,
                "failure_count": 0,
                "results": [],
                "error": "recipients中的每个元素都必须是字典",
            }

        if not title or not title.strip():
            return {
                "success": False,
                "send_mode": None,
                "scheduled_at": scheduled_at,
                "total_recipients": len(recipients),
                "total_tasks": 0,
                "success_count": 0,
                "failure_count": 0,
                "results": [],
                "error": "通知标题不能为空",
            }

        if not body or not body.strip():
            return {
                "success": False,
                "send_mode": None,
                "scheduled_at": scheduled_at,
                "total_recipients": len(recipients),
                "total_tasks": 0,
                "success_count": 0,
                "failure_count": 0,
                "results": [],
                "error": "通知正文不能为空",
            }

        if not channels:
            return {
                "success": False,
                "send_mode": None,
                "scheduled_at": scheduled_at,
                "total_recipients": len(recipients),
                "total_tasks": 0,
                "success_count": 0,
                "failure_count": 0,
                "results": [],
                "error": "至少选择一个发送渠道",
            }

        unique_channels = list(dict.fromkeys(channels))

        final_body = body.strip()
        if template is not None:
            final_body = (
                f"{NOTIFICATION_TEMPLATES[template]}\n\n{final_body}"
            )

        send_mode = "immediate"

        if scheduled_at is not None:
            try:
                scheduled_time = datetime.strptime(
                    scheduled_at,
                    "%Y-%m-%d %H:%M:%S",
                )
            except ValueError:
                return {
                    "success": False,
                    "send_mode": None,
                    "scheduled_at": scheduled_at,
                    "total_recipients": len(recipients),
                    "total_tasks": 0,
                    "success_count": 0,
                    "failure_count": 0,
                    "results": [],
                    "error": (
                        "scheduled_at格式错误，"
                        "正确格式为YYYY-MM-DD HH:MM:SS"
                    ),
                }

            if scheduled_time <= datetime.now():
                return {
                    "success": False,
                    "send_mode": None,
                    "scheduled_at": scheduled_at,
                    "total_recipients": len(recipients),
                    "total_tasks": 0,
                    "success_count": 0,
                    "failure_count": 0,
                    "results": [],
                    "error": "定时发送时间必须晚于当前时间",
                }

            send_mode = "scheduled"

        results: List[Dict[str, Any]] = []

        for index, recipient in enumerate(recipients, start=1):
            recipient_id = recipient.get(
                "recipient_id",
                f"recipient_{index}",
            )
            recipient_name = recipient.get("name", "未命名收件人")

            for channel in unique_channels:
                if channel == "email":
                    destination = recipient.get("email")
                elif channel == "sms":
                    destination = recipient.get("phone")
                else:
                    destination = recipient.get("internal_id")

                if not destination:
                    results.append(
                        {
                            "recipient_id": recipient_id,
                            "name": recipient_name,
                            "channel": channel,
                            "destination": None,
                            "success": False,
                            "status": "failed",
                            "error": (
                                f"收件人缺少{channel}渠道所需地址"
                            ),
                        }
                    )
                    continue

                results.append(
                    {
                        "recipient_id": recipient_id,
                        "name": recipient_name,
                        "channel": channel,
                        "destination": destination,
                        "title": title.strip(),
                        "body": final_body,
                        "success": True,
                        "status": (
                            "scheduled"
                            if send_mode == "scheduled"
                            else "sent"
                        ),
                        "error": None,
                    }
                )

        success_count = sum(
            1 for result in results if result["success"]
        )
        failure_count = len(results) - success_count

        return {
            "success": failure_count == 0,
            "send_mode": send_mode,
            "scheduled_at": scheduled_at,
            "template": template,
            "channels": unique_channels,
            "total_recipients": len(recipients),
            "total_tasks": len(results),
            "success_count": success_count,
            "failure_count": failure_count,
            "results": results,
            "error": (
                None
                if failure_count == 0
                else "部分通知发送失败，请查看results字段"
            ),
        }

    except Exception as exc:
        return {
            "success": False,
            "send_mode": None,
            "scheduled_at": scheduled_at,
            "total_recipients": len(recipients),
            "total_tasks": 0,
            "success_count": 0,
            "failure_count": 0,
            "results": [],
            "error": f"批量通知处理失败：{str(exc)}",
        }


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8001,
    )
