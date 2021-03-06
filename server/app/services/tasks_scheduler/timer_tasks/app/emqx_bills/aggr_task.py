import arrow

from actor_libs.database.async_db import db
from actor_libs.tasks.backend import get_task_result
from actor_libs.types import TaskResult
from .sql_statements import (
    emqx_bills_hour_aggr_sql, emqx_bills_day_aggr_sql,
    emqx_bills_month_aggr_sql
)
from ..config import project_config


__all__ = ['emqx_bills_aggr_task']


async def emqx_bills_aggr_task() -> TaskResult:
    aggr_result = {}
    date_now = arrow.now(tz=project_config['TIMEZONE'])

    aggr_result['emqx_bills_hour'] = await _hour_emqx_bills_count()
    if date_now.hour == 0:
        aggr_result['emqx_bills_day'] = await _day_emqx_bills_count()
    if date_now.day == 1 and date_now.hour == 0:
        aggr_result['emqx_bills_month'] = await _month_emqx_bills_count()
    aggr_status = aggr_result.values()
    if aggr_status and all(aggr_status):
        task_result = get_task_result(
            status=3, message='Emqx bills aggr success', result=aggr_result
        )
    else:
        task_result = get_task_result(
            status=4, message='Emqx bills aggr failed', result=aggr_result
        )
    return task_result


async def _hour_emqx_bills_count() -> bool:
    execute_result = await db.execute(emqx_bills_hour_aggr_sql)
    return execute_result


async def _day_emqx_bills_count() -> bool:
    execute_result = await db.execute(emqx_bills_day_aggr_sql)
    return execute_result


async def _month_emqx_bills_count() -> bool:
    execute_status = await db.execute(emqx_bills_month_aggr_sql)
    return execute_status
