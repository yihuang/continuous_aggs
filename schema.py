# coding: utf-8
from sqlalchemy import BigInteger, Boolean, Column, DateTime, Enum, Integer, MetaData, Numeric, Table, Text, text

metadata = MetaData()


t_continuous_aggs = Table(
    't_continuous_aggs', metadata,
    Column('name', Text, primary_key=True),
    Column('completed', DateTime(True)),
    Column('invalidated', DateTime(True))
)


t_kline_1m = Table(
    't_kline_1m', metadata,
    Column('time', DateTime(True), primary_key=True),
    Column('open', Numeric),
    Column('high', Numeric),
    Column('low', Numeric),
    Column('close', Numeric),
    Column('volume', Numeric),
    Column('value', Numeric)
)


t_kline_3m = Table(
    't_kline_3m', metadata,
    Column('time', DateTime(True), primary_key=True),
    Column('open', Numeric),
    Column('high', Numeric),
    Column('low', Numeric),
    Column('close', Numeric),
    Column('volume', Numeric),
    Column('value', Numeric)
)


t_kline_5m = Table(
    't_kline_5m', metadata,
    Column('time', DateTime(True), primary_key=True),
    Column('open', Numeric),
    Column('high', Numeric),
    Column('low', Numeric),
    Column('close', Numeric),
    Column('volume', Numeric),
    Column('value', Numeric)
)


t_kline_15m = Table(
    't_kline_15m', metadata,
    Column('time', DateTime(True), primary_key=True),
    Column('open', Numeric),
    Column('high', Numeric),
    Column('low', Numeric),
    Column('close', Numeric),
    Column('volume', Numeric),
    Column('value', Numeric)
)


t_kline_1h = Table(
    't_kline_1h', metadata,
    Column('time', DateTime(True), primary_key=True),
    Column('open', Numeric),
    Column('high', Numeric),
    Column('low', Numeric),
    Column('close', Numeric),
    Column('volume', Numeric),
    Column('value', Numeric)
)


t_kline_1d = Table(
    't_kline_1d', metadata,
    Column('time', DateTime(True), primary_key=True),
    Column('open', Numeric),
    Column('high', Numeric),
    Column('low', Numeric),
    Column('close', Numeric),
    Column('volume', Numeric),
    Column('value', Numeric)
)


t_order_history = Table(
    't_order_history', metadata,
    Column('id', BigInteger, nullable=False, server_default=text("nextval('t_orders_id_seq'::regclass)")),
    Column('side', Enum('buy', 'sell', name='side'), nullable=False),
    Column('amount', Numeric),
    Column('deal_amount', Numeric, server_default=text("0")),
    Column('price', Numeric),
    Column('user_id', Integer, nullable=False),
    Column('done', Boolean, nullable=False, server_default=text("false")),
    Column('time', DateTime(True), nullable=False, server_default=text("now()"))
)


t_order_pending = Table(
    't_order_pending', metadata,
    Column('id', BigInteger, nullable=False, unique=True, server_default=text("nextval('t_orders_id_seq'::regclass)")),
    Column('side', Enum('buy', 'sell', name='side'), nullable=False),
    Column('amount', Numeric),
    Column('deal_amount', Numeric, server_default=text("0")),
    Column('price', Numeric, index=True),
    Column('user_id', Integer, nullable=False),
    Column('done', Boolean, nullable=False, server_default=text("false")),
    Column('time', DateTime(True), nullable=False, server_default=text("now()"))
)


t_orders = Table(
    't_orders', metadata,
    Column('id', BigInteger, nullable=False, server_default=text("nextval('t_orders_id_seq'::regclass)")),
    Column('side', Enum('buy', 'sell', name='side'), nullable=False),
    Column('amount', Numeric),
    Column('deal_amount', Numeric, server_default=text("0")),
    Column('price', Numeric),
    Column('user_id', Integer, nullable=False),
    Column('done', Boolean, nullable=False, server_default=text("false")),
    Column('time', DateTime(True), nullable=False, server_default=text("now()"))
)


t_test = Table(
    't_test', metadata,
    Column('id', Integer)
)


t_trades = Table(
    't_trades', metadata,
    Column('id', BigInteger, primary_key=True, server_default=text("nextval('t_trades_id_seq'::regclass)")),
    Column('taker_id', BigInteger, nullable=False),
    Column('maker_id', BigInteger, nullable=False),
    Column('price', Numeric),
    Column('amount', Numeric),
    Column('taker_done', Boolean, nullable=False),
    Column('maker_done', Boolean, nullable=False),
    Column('time', DateTime(True), nullable=False, server_default=text("now()"))
)
