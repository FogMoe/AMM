import os
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Pool, Transaction, PoolPriceHistory
from amm import AMM
from datetime import datetime, timedelta
import json
import random  # 用于生成初始K线图数据

# 初始化应用
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///amm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db.init_app(app)

# 初始化登录管理
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 初始化应用数据库
def initialize_app():
    with app.app_context():
        # 删除现有表并重新创建
        db.drop_all()
        db.create_all()
        
        # 检查是否已经有池子数据
        if not Pool.query.first():
            initial_pool = Pool(token1_reserve=10.0, token2_reserve=1000.0)
            db.session.add(initial_pool)
            db.session.commit()
            
            # 生成一些初始K线图数据
            generate_initial_price_history(initial_pool.id)

# 生成初始价格历史数据用于演示
def generate_initial_price_history(pool_id):
    pool = Pool.query.get(pool_id)
    if not pool:
        return
        
    # 初始价格（token2/token1）
    initial_price = pool.token2_reserve / pool.token1_reserve
    
    # 生成过去7天的小时K线数据
    now = datetime.utcnow()
    for i in range(168, 0, -1):  # 7天 * 24小时
        time_point = now - timedelta(hours=i)
        
        # 随机波动价格（±5%）
        price_change = random.uniform(-0.05, 0.05)
        close_price = initial_price * (1 + price_change)
        
        # 创建一小时的OHLC数据
        high_price = close_price * random.uniform(1, 1.02)
        low_price = close_price * random.uniform(0.98, 1)
        open_price = low_price + random.uniform(0, high_price - low_price)
        
        # 模拟成交量
        volume = random.uniform(0.5, 5.0)
        
        # 计算对应的token储备
        k = pool.token1_reserve * pool.token2_reserve
        token1_reserve = (k / close_price) ** 0.5
        token2_reserve = token1_reserve * close_price
        
        # 创建历史记录
        history = PoolPriceHistory(
            pool_id=pool_id,
            open_price=open_price,
            close_price=close_price,
            high_price=high_price,
            low_price=low_price,
            volume=volume,
            token1_reserve=token1_reserve,
            token2_reserve=token2_reserve,
            timestamp=time_point,
            period='1h'
        )
        db.session.add(history)
    
    # 创建日K数据
    for i in range(30, 0, -1):  # 30天
        time_point = now - timedelta(days=i)
        
        # 获取当天的小时数据并聚合
        day_start = time_point.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        # 计算日K
        day_high = initial_price * (1 + random.uniform(0, 0.1))
        day_low = initial_price * (1 - random.uniform(0, 0.1))
        day_open = day_low + random.uniform(0, day_high - day_low)
        day_close = day_low + random.uniform(0, day_high - day_low)
        day_volume = random.uniform(5, 50)
        
        # 计算对应的token储备
        k = pool.token1_reserve * pool.token2_reserve
        token1_reserve = (k / day_close) ** 0.5
        token2_reserve = token1_reserve * day_close
        
        history = PoolPriceHistory(
            pool_id=pool_id,
            open_price=day_open,
            close_price=day_close,
            high_price=day_high,
            low_price=day_low,
            volume=day_volume,
            token1_reserve=token1_reserve,
            token2_reserve=token2_reserve,
            timestamp=time_point,
            period='1d'
        )
        db.session.add(history)
    
    db.session.commit()

# 主页
@app.route('/')
def index():
    return render_template('index.html')

# 注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        
        # 验证用户输入
        if not username or not email:
            flash('用户名和邮箱都是必填项!', 'danger')
            return redirect(url_for('register'))
            
        # 检查用户名和邮箱是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已存在!', 'danger')
            return redirect(url_for('register'))
            
        if User.query.filter_by(email=email).first():
            flash('邮箱已注册!', 'danger')
            return redirect(url_for('register'))
        
        # 创建新用户(默认有10 token1)
        new_user = User(username=username, email=email, token1_balance=10.0, token2_balance=0.0)
        db.session.add(new_user)
        db.session.commit()
        
        # 登录用户
        login_user(new_user)
        
        flash('注册成功! 已获得10个Token1作为奖励。', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

# 登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        
        user = User.query.filter_by(username=username).first()
        
        if not user:
            flash('用户不存在!', 'danger')
            return redirect(url_for('login'))
        
        login_user(user)
        flash('登录成功!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')

# 登出
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已成功登出!', 'success')
    return redirect(url_for('index'))

# 用户面板
@app.route('/dashboard')
@login_required
def dashboard():
    # 获取池子信息
    pool = Pool.query.first()
    # 获取交易历史
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.timestamp.desc()).limit(10).all()
    
    # 创建AMM实例用于计算
    amm = AMM(pool.token1_reserve, pool.token2_reserve)
    exchange_rate = amm.get_exchange_rate()
    
    return render_template('dashboard.html', 
                           user=current_user, 
                           pool=pool, 
                           transactions=transactions,
                           exchange_rate=exchange_rate)

# 交易页面
@app.route('/swap', methods=['GET', 'POST'])
@login_required
def swap():
    pool = Pool.query.first()
    amm = AMM(pool.token1_reserve, pool.token2_reserve)
    
    if request.method == 'POST':
        swap_type = request.form.get('swap_type')
        amount = float(request.form.get('amount'))
        
        if amount <= 0:
            flash('交易数量必须大于0!', 'danger')
            return redirect(url_for('swap'))
        
        current_price = amm.get_exchange_rate()
        
        if swap_type == 'token1_to_token2':
            # 检查用户余额
            if current_user.token1_balance < amount:
                flash('Token1余额不足!', 'danger')
                return redirect(url_for('swap'))
            
            # 计算可得到的token2数量
            token2_amount, slippage, fee_amount = amm.swap_token1_to_token2(amount)
            
            # 更新用户余额
            current_user.token1_balance -= amount
            current_user.token2_balance += token2_amount
            
            # 更新池子
            pool.token1_reserve += amount
            pool.token2_reserve -= token2_amount
            pool.last_updated = datetime.utcnow()
            
            # 记录交易
            transaction = Transaction(
                user_id=current_user.id,
                transaction_type='token1_to_token2',
                token1_amount=amount,
                token2_amount=token2_amount,
                fee_amount=fee_amount,
                slippage=slippage,
                price=current_price
            )
            
            flash(f'交易成功! 用 {amount} Token1 兑换了 {token2_amount:.4f} Token2，滑点: {slippage:.2f}%，手续费: {fee_amount:.4f} Token1', 'success')
            
        elif swap_type == 'token2_to_token1':
            # 检查用户余额
            if current_user.token2_balance < amount:
                flash('Token2余额不足!', 'danger')
                return redirect(url_for('swap'))
            
            # 计算可得到的token1数量
            token1_amount, slippage, fee_amount = amm.swap_token2_to_token1(amount)
            
            # 更新用户余额
            current_user.token2_balance -= amount
            current_user.token1_balance += token1_amount
            
            # 更新池子
            pool.token2_reserve += amount
            pool.token1_reserve -= token1_amount
            pool.last_updated = datetime.utcnow()
            
            # 记录交易
            transaction = Transaction(
                user_id=current_user.id,
                transaction_type='token2_to_token1',
                token1_amount=token1_amount,
                token2_amount=amount,
                fee_amount=fee_amount,
                slippage=slippage,
                price=1/current_price
            )
            
            flash(f'交易成功! 用 {amount} Token2 兑换了 {token1_amount:.4f} Token1，滑点: {slippage:.2f}%，手续费: {fee_amount:.4f} Token2', 'success')
        
        # 保存交易记录和更新
        db.session.add(transaction)
        
        # 更新价格历史数据
        update_price_history(pool)
        
        db.session.commit()
        
        return redirect(url_for('dashboard'))
    
    # 获取当前汇率
    exchange_rate = amm.get_exchange_rate()
    
    return render_template('swap.html', 
                           user=current_user, 
                           pool=pool, 
                           exchange_rate=exchange_rate)

# 更新价格历史记录
def update_price_history(pool):
    # 获取最新价格
    current_price = pool.token2_reserve / pool.token1_reserve
    now = datetime.utcnow()
    
    # 更新小时K线
    current_hour = now.replace(minute=0, second=0, microsecond=0)
    hour_candle = PoolPriceHistory.query.filter_by(
        pool_id=pool.id, 
        period='1h',
        timestamp=current_hour
    ).first()
    
    if hour_candle:
        # 更新已有K线
        hour_candle.high_price = max(hour_candle.high_price, current_price)
        hour_candle.low_price = min(hour_candle.low_price, current_price)
        hour_candle.close_price = current_price
        hour_candle.volume += 1  # 简化处理，每笔交易+1
        hour_candle.token1_reserve = pool.token1_reserve
        hour_candle.token2_reserve = pool.token2_reserve
    else:
        # 创建新K线
        hour_candle = PoolPriceHistory(
            pool_id=pool.id,
            open_price=current_price,
            close_price=current_price,
            high_price=current_price,
            low_price=current_price,
            volume=1,
            token1_reserve=pool.token1_reserve,
            token2_reserve=pool.token2_reserve,
            timestamp=current_hour,
            period='1h'
        )
        db.session.add(hour_candle)
    
    # 更新日K线
    current_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    day_candle = PoolPriceHistory.query.filter_by(
        pool_id=pool.id, 
        period='1d',
        timestamp=current_day
    ).first()
    
    if day_candle:
        # 更新已有K线
        day_candle.high_price = max(day_candle.high_price, current_price)
        day_candle.low_price = min(day_candle.low_price, current_price)
        day_candle.close_price = current_price
        day_candle.volume += 1
        day_candle.token1_reserve = pool.token1_reserve
        day_candle.token2_reserve = pool.token2_reserve
    else:
        # 创建新K线
        day_candle = PoolPriceHistory(
            pool_id=pool.id,
            open_price=current_price,
            close_price=current_price,
            high_price=current_price,
            low_price=current_price,
            volume=1,
            token1_reserve=pool.token1_reserve,
            token2_reserve=pool.token2_reserve,
            timestamp=current_day,
            period='1d'
        )
        db.session.add(day_candle)

# API - 计算交易预览
@app.route('/api/preview_swap', methods=['POST'])
@login_required
def preview_swap():
    data = request.json
    swap_type = data.get('swap_type')
    amount = float(data.get('amount', 0))
    
    pool = Pool.query.first()
    amm = AMM(pool.token1_reserve, pool.token2_reserve)
    
    if swap_type == 'token1_to_token2':
        output_amount, slippage = amm.get_token2_output(amount)
        fee_amount = amount * amm.fee_percent
        
        return jsonify({
            'input_amount': amount,
            'output_amount': output_amount,
            'fee_amount': fee_amount,
            'slippage': slippage,
            'exchange_rate': output_amount / amount if amount > 0 else amm.get_exchange_rate()
        })
    elif swap_type == 'token2_to_token1':
        output_amount, slippage = amm.get_token1_output(amount)
        fee_amount = amount * amm.fee_percent
        
        return jsonify({
            'input_amount': amount,
            'output_amount': output_amount,
            'fee_amount': fee_amount,
            'slippage': slippage,
            'exchange_rate': amount / output_amount if output_amount > 0 else 1/amm.get_exchange_rate()
        })
    
    return jsonify({'error': '无效的交易类型'})

# API - 获取池子历史数据
@app.route('/api/pool_history')
def pool_history():
    # 获取池子变化历史
    transactions = Transaction.query.order_by(Transaction.timestamp).all()
    
    # 从交易历史重建池子变化
    history_data = []
    token1_reserve = 10.0
    token2_reserve = 1000.0
    
    for tx in transactions:
        if tx.transaction_type == 'token1_to_token2':
            token1_reserve += tx.token1_amount
            token2_reserve -= tx.token2_amount
        else:
            token1_reserve -= tx.token1_amount
            token2_reserve += tx.token2_amount
        
        history_data.append({
            'timestamp': tx.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'token1_reserve': token1_reserve,
            'token2_reserve': token2_reserve,
            'exchange_rate': token2_reserve / token1_reserve,
            'fee': tx.fee_amount,
            'slippage': tx.slippage
        })
    
    return jsonify(history_data)

# API - 获取K线图数据
@app.route('/api/kline_data')
def kline_data():
    period = request.args.get('period', '1h')  # 默认获取小时线
    limit = int(request.args.get('limit', 500))  # 增加默认数据量
    
    # 处理不同的时间周期
    if period not in ['1h', '1d']:
        # 将TradingView的时间周期转换为我们的格式
        if period == '60':  # 1小时
            period = '1h'
        elif period == 'D':  # 1天
            period = '1d'
        elif period in ['1', '5', '15', '30']:  # 分钟级别，目前没有这些数据，使用1h近似
            period = '1h'
        elif period == '240':  # 4小时，目前没有，使用1h近似
            period = '1h'
    
    pool = Pool.query.first()
    if not pool:
        return jsonify([])
    
    # 获取K线数据
    kline_data = PoolPriceHistory.query.filter_by(
        pool_id=pool.id,
        period=period
    ).order_by(PoolPriceHistory.timestamp.desc()).limit(limit).all()
    
    # 格式化数据为前端可用格式
    result = []
    for candle in reversed(kline_data):  # 反转使其按时间从旧到新排序
        result.append({
            'time': candle.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'open': candle.open_price,
            'high': candle.high_price,
            'low': candle.low_price,
            'close': candle.close_price,
            'volume': candle.volume
        })
    
    return jsonify(result)

if __name__ == '__main__':
    initialize_app()  # 在app运行前初始化数据库
    app.run(debug=True) 