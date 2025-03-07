# AMM交易模拟系统

中文 | [English](README.md)

这是一个使用Python开发的自动做市商(AMM)交易模拟系统，提供以下功能：

- 用户注册和登录
- 基于恒定乘积公式的代币交换
- 交易历史图表显示
- 用户资产管理
- 交易手续费和滑点模拟
- 历史价格和流动性数据

## 功能特点

- **AMM核心逻辑**：实现恒定乘积公式 (x * y = k)
- **实时图表**：K线价格图表和池流动性可视化
- **交易跟踪**：完整记录所有交易，包括手续费和滑点
- **用户管理**：账户创建和代币余额跟踪
- **教育工具**：适合学习DeFi和AMM概念

## 安装

1. 克隆此仓库
   ```
   git clone https://github.com/FogMoe/AMM.git
   cd AMM
   ```

2. 创建并激活虚拟环境
   ```
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # 或
   .venv\Scripts\activate  # Windows
   ```

3. 安装依赖
   ```
   pip install -r requirements.txt
   ```

## 使用方法

1. 运行应用程序
   ```
   python app.py
   ```

2. 在浏览器中访问 http://localhost:5000

3. 注册新账户（系统会自动赠送10枚Token1代币）

4. 探索仪表板并开始在Token1和Token2之间进行交易

## 技术细节

- **后端**：Flask, SQLAlchemy, SQLite
- **前端**：Bootstrap 5, Plotly.js
- **AMM模型**：使用恒定乘积模型，其中token1储备 * token2储备 = k
- **数据可视化**：价格历史和池流动性的交互式图表
- **初始池配置**：10个Token1和1000个Token2

## 截图

[截图](video/demo.mp4)

## 贡献

欢迎贡献！请随时提交Pull Request。

## 许可证

本项目采用MIT许可证 - 详情请参阅LICENSE文件。

## 仓库

GitHub: [https://github.com/FogMoe/AMM.git](https://github.com/FogMoe/AMM.git) 
