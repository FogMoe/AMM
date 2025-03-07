// 通用JavaScript功能

// 自动关闭警告消息
document.addEventListener('DOMContentLoaded', function() {
    // 获取所有警告消息
    const alerts = document.querySelectorAll('.alert');
    
    // 设置5秒后自动关闭
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });
    
    // 为数字输入添加格式化
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value) {
                const value = parseFloat(this.value);
                if (!isNaN(value)) {
                    this.value = value.toFixed(4);
                }
            }
        });
    });
    
    // 为TradingView图表容器添加全屏切换按钮
    const chartContainer = document.getElementById('tradingview_chart');
    if (chartContainer) {
        // 创建全屏按钮
        const fullscreenButton = document.createElement('button');
        fullscreenButton.className = 'chart-fullscreen-button';
        fullscreenButton.innerHTML = '<i class="fas fa-expand"></i> 全屏';
        fullscreenButton.title = '切换全屏模式';
        
        // 将按钮添加到图表容器
        chartContainer.parentElement.appendChild(fullscreenButton);
        
        // 添加全屏切换功能
        fullscreenButton.addEventListener('click', function() {
            const container = chartContainer.parentElement;
            
            if (container.classList.contains('fullscreen-chart')) {
                // 退出全屏
                container.classList.remove('fullscreen-chart');
                this.innerHTML = '<i class="fas fa-expand"></i> 全屏';
            } else {
                // 进入全屏
                container.classList.add('fullscreen-chart');
                this.innerHTML = '<i class="fas fa-compress"></i> 退出全屏';
            }
            
            // 通知图表重新调整大小
            setTimeout(() => {
                window.dispatchEvent(new Event('resize'));
            }, 100);
        });
    }
}); 