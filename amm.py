class AMM:
    """
    自动做市商(AMM)逻辑实现
    使用恒定乘积公式: x * y = k
    其中x是token1的数量，y是token2的数量，k是常数
    """
    
    def __init__(self, token1_reserve, token2_reserve):
        self.token1_reserve = token1_reserve
        self.token2_reserve = token2_reserve
        self.k = token1_reserve * token2_reserve
        self.fee_percent = 0.01  # 1%交易手续费
    
    def get_token2_output(self, token1_input):
        """根据输入的token1计算能换取的token2数量"""
        # 确保输入有效
        if token1_input <= 0:
            return 0
        
        # 计算手续费
        token1_with_fee = token1_input * (1 - self.fee_percent)
        
        # 新的token1储备量
        new_token1_reserve = self.token1_reserve + token1_with_fee
        # 根据恒定乘积计算新的token2储备量
        new_token2_reserve = self.k / new_token1_reserve
        # 输出的token2数量为储备减少量
        token2_output = self.token2_reserve - new_token2_reserve
        
        return token2_output, self.calculate_slippage(token1_input, token2_output)
    
    def get_token1_output(self, token2_input):
        """根据输入的token2计算能换取的token1数量"""
        # 确保输入有效
        if token2_input <= 0:
            return 0
        
        # 计算手续费
        token2_with_fee = token2_input * (1 - self.fee_percent)
        
        # 新的token2储备量
        new_token2_reserve = self.token2_reserve + token2_with_fee
        # 根据恒定乘积计算新的token1储备量
        new_token1_reserve = self.k / new_token2_reserve
        # 输出的token1数量为储备减少量
        token1_output = self.token1_reserve - new_token1_reserve
        
        return token1_output, self.calculate_slippage(token2_input, token1_output)
    
    def swap_token1_to_token2(self, token1_amount):
        """将token1兑换成token2"""
        token2_amount, slippage = self.get_token2_output(token1_amount)
        
        # 计算手续费
        fee_amount = token1_amount * self.fee_percent
        token1_with_fee = token1_amount - fee_amount
        
        # 更新储备量
        self.token1_reserve += token1_amount
        self.token2_reserve -= token2_amount
        
        # 更新常数k (理论上应该不变，但由于浮点数计算可能有微小误差)
        self.k = self.token1_reserve * self.token2_reserve
        
        return token2_amount, slippage, fee_amount
    
    def swap_token2_to_token1(self, token2_amount):
        """将token2兑换成token1"""
        token1_amount, slippage = self.get_token1_output(token2_amount)
        
        # 计算手续费
        fee_amount = token2_amount * self.fee_percent
        token2_with_fee = token2_amount - fee_amount
        
        # 更新储备量
        self.token2_reserve += token2_amount
        self.token1_reserve -= token1_amount
        
        # 更新常数k (理论上应该不变，但由于浮点数计算可能有微小误差)
        self.k = self.token1_reserve * self.token2_reserve
        
        return token1_amount, slippage, fee_amount
    
    def get_exchange_rate(self):
        """获取当前交易对的汇率 (token2/token1)"""
        return self.token2_reserve / self.token1_reserve
    
    def calculate_slippage(self, input_amount, output_amount):
        """计算交易滑点百分比"""
        if input_amount <= 0 or output_amount <= 0:
            return 0
            
        # 计算当前汇率
        current_rate = self.get_exchange_rate()
        
        # 如果是token1→token2
        if current_rate > 1:  # token2比token1值多
            expected_output = input_amount * current_rate
            actual_output = output_amount
        else:  # token1比token2值多
            expected_output = input_amount / current_rate
            actual_output = output_amount
            
        # 滑点计算: (预期输出 - 实际输出) / 预期输出
        slippage = abs((expected_output - actual_output) / expected_output) * 100
        return slippage 