# AMM Trading Simulation System

[中文](README_CN.md) | English

A Python-based Automated Market Maker (AMM) trading simulation system providing the following features:

- User registration and authentication
- Token swapping based on constant product formula
- Advanced data visualization with real-time charts
- User asset management
- Transaction fee and slippage simulation
- Historical price and liquidity data

## Features

- **AMM Core Logic**: Implementation of the constant product formula (x * y = k)
- **Real-time Charts**: Candlestick price charts and pool data visualizations 
- **Transaction Tracking**: Complete history of all trades with fees and slippage
- **User Management**: Account creation and token balance tracking
- **Educational Tool**: Perfect for learning about DeFi and AMM concepts

## Installation

1. Clone this repository
   ```
   git clone https://github.com/FogMoe/AMM.git
   cd AMM
   ```

2. Create and activate a virtual environment
   ```
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate  # Windows
   ```

3. Install dependencies
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application
   ```
   python app.py
   ```

2. Open your browser and navigate to http://localhost:5000

3. Register a new account (you'll receive 10 Token1 tokens automatically)

4. Explore the dashboard and start trading between Token1 and Token2

## Technical Details

- **Backend**: Flask, SQLAlchemy, SQLite
- **Frontend**: Bootstrap 5, Plotly.js
- **AMM Model**: Uses the constant product model where token1_reserve * token2_reserve = k
- **Data Visualization**: Interactive charts for price history and pool liquidity
- **Initial Pool Configuration**: 10 Token1 and 1000 Token2

## Screenshots

[screenshots](video/demo.mp4)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Repository

GitHub: [https://github.com/FogMoe/AMM.git](https://github.com/FogMoe/AMM.git) 
