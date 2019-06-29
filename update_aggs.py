import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from schema import (
    t_trades, t_continuous_aggs, t_kline_1m, t_kline_3m,
    t_kline_5m, t_kline_15m, t_kline_1h, t_kline_1d
)


def update_invalidation(conn, table, column=None, name=None):
    column = column or table.c.time
    name = name or table.name
    completed = None
    invalidated = None

    q = sa.select([t_continuous_aggs.c.completed, t_continuous_aggs.c.invalidated]
                  ).where(t_continuous_aggs.c.name == name)
    rows = conn.execute(q).fetchall()
    if rows:
        completed, invalidated = rows[0]
    q = sa.select([sa.func.max(column)], from_obj=table)
    if completed:
        q = q.where(column >= completed)
    rows = conn.execute(q).fetchall()
    if rows:
        new_invalidated, = rows[0]
        if invalidated is None or new_invalidated > invalidated:
            inst = pg.insert(t_continuous_aggs).values((name, completed, new_invalidated))
            inst = inst.on_conflict_do_update(
                index_elements=[t_continuous_aggs.c.name],
                set_={
                    'invalidated': inst.excluded.invalidated
                }
            )
            conn.execute(inst)


def trade_kline_builder(t_from, t_to, completed, invalidated):
    q = sa.select(
        [sa.func.time_bucket(t_from.c.time, sa.text("'1 minute'")).label('time'),
         sa.func.first(pg.aggregate_order_by(t_from.c.price, t_from.c.time)).label('open'),
         sa.func.max(t_from.c.price).label('high'),
         sa.func.min(t_from.c.price).label('low'),
         sa.func.last(pg.aggregate_order_by(t_from.c.price, t_from.c.time)).label('close'),
         sa.func.sum(t_from.c.amount).label('volume'),
         sa.func.sum(t_from.c.price * t_from.c.amount).label('value')],
        from_obj=t_from
    ).group_by(sa.text('1')).where(t_from.c.time <= invalidated)

    if completed is not None:
        q = q.where(t_from.c.time >= completed)

    inst = pg.insert(t_to).from_select(t_to.columns, q)
    inst = inst.on_conflict_do_update(
        index_elements=[t_to.c.time],
        set_={
            'open': inst.excluded.open,
            'high': inst.excluded.high,
            'low': inst.excluded.low,
            'close': inst.excluded.close,
            'volume': inst.excluded.volume,
            'value': inst.excluded.value,
        }
    )
    print(inst.compile(dialect=pg.dialect()))
    return inst


def kline_builder(interval):
    def builder(t_from, t_to, completed, invalidated):
        # aggregation query
        q = sa.select(
            [sa.func.time_bucket(t_from.c.time, sa.text("'%s'" % interval)).label('time'),
             sa.func.first(pg.aggregate_order_by(t_from.c.open, t_from.c.time)).label('open'),
             sa.func.max(t_from.c.high).label('high'),
             sa.func.min(t_from.c.low).label('low'),
             sa.func.last(pg.aggregate_order_by(t_from.c.close, t_from.c.time)).label('close'),
             sa.func.sum(t_from.c.volume).label('volume'),
             sa.func.sum(t_from.c.value).label('value')],
            from_obj=t_from
        ).group_by(sa.text('1')).where(t_from.c.time <= invalidated)

        if completed is not None:
            q = q.where(t_from.c.time >= completed)

        # upsert materialized table
        inst = pg.insert(t_to).from_select(t_to.columns, q)
        inst = inst.on_conflict_do_update(
            index_elements=[t_kline_1m.c.time],
            set_={
                'open': inst.excluded.open,
                'high': inst.excluded.high,
                'low': inst.excluded.low,
                'close': inst.excluded.close,
                'volume': inst.excluded.volume,
                'value': inst.excluded.value,
            }
        )
        print(inst.compile(dialect=pg.dialect()))
        return inst
    return builder


def materialise_agg(conn, t_from, t_to, query_builder, name):
    completed = None
    invalidated = None

    q = sa.select([t_continuous_aggs.c.completed, t_continuous_aggs.c.invalidated]
                  ).where(t_continuous_aggs.c.name == name)
    rows = conn.execute(q).fetchall()
    if rows:
        completed, invalidated = rows[0]

    if invalidated is None:
        print('need to run update_invalidation first.')
        return

    if completed is not None and invalidated <= completed:
        print('no changes.')
        return

    inst = query_builder(t_from, t_to, completed, invalidated)
    conn.execute(inst)

    conn.execute(
        sa.update(t_continuous_aggs)
        .where(t_continuous_aggs.c.name == name)
        .values(completed=invalidated)
    )


def update_continuous_aggs(engine, t_from, t_to, query_builder, name=None):
    name = name or t_to.name
    with engine.begin() as conn:
        update_invalidation(conn, t_from, name=name)
    with engine.begin() as conn:
        materialise_agg(conn, t_from, t_to, query_builder, name)


if __name__ == '__main__':
    engine = sa.create_engine('postgresql://yihuang:123456@localhost/testdb')
    update_continuous_aggs(engine, t_trades, t_kline_1m, trade_kline_builder)
    update_continuous_aggs(engine, t_kline_1m, t_kline_3m, kline_builder('3 minutes'))
    update_continuous_aggs(engine, t_kline_1m, t_kline_5m, kline_builder('5 minutes'))
    update_continuous_aggs(engine, t_kline_5m, t_kline_15m, kline_builder('15 minutes'))
    update_continuous_aggs(engine, t_kline_15m, t_kline_1h, kline_builder('1 hour'))
    update_continuous_aggs(engine, t_kline_1h, t_kline_1d, kline_builder('1 day'))
