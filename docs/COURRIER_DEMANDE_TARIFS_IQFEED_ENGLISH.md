# IQFEED PRICING REQUEST LETTER

**Date:** August 14, 2025  
**To:** IQFeed Sales Department  
**From:** [Your Name]  
**Subject:** Pricing Request for Automated Trading System ES/SPX

---

## 📋 PROJECT PRESENTATION

Hello,

I am currently developing a sophisticated automated trading system called **MIA_IA_SYSTEM** specialized in trading ES futures (E-mini S&P 500) and SPX options. My system uses a proprietary strategy called "Battle Navale" that requires very high-quality market data.

## 🎯 SPECIFIC TECHNICAL REQUIREMENTS

### **1. ES FUTURES DATA (E-mini S&P 500)**
- **Real-time tick data**: Tick-by-tick data with <50ms latency
- **Historical data**: Complete 1-minute bars history (minimum 2 years)
- **Level 2 order book**: Market depth bid/ask with sizes
- **Volume data**: Real-time volume and distribution
- **VWAP**: Volume Weighted Average Price calculated
- **Market Profile**: VAH/VAL/POC (Value Area High/Low/Point of Control)

### **2. SPX OPTIONS DATA (S&P 500 Options)**
- **Complete options chain**: All strikes and expirations
- **Real-time Greeks**: Delta, Gamma, Theta, Vega calculated
- **Open Interest**: Updated OI data
- **Implied Volatility**: Complete volatility surface
- **Options flow**: Options trading data (if available)
- **Gamma exposure**: Dealer gamma calculations for analysis

### **3. ORDER FLOW DATA**
- **Bid/Ask imbalance**: Order book imbalances
- **Large orders detection**: Detection of significant orders
- **Aggressive buying/selling**: Identification of aggressive flows
- **Cumulative delta**: Cumulative delta calculation
- **Volume profile**: Volume distribution by price level

### **4. HISTORICAL DATA**
- **ES futures**: 1-minute historical data (minimum 2 years)
- **SPX options**: Options chains history
- **Volume data**: Volume and distribution history
- **Market microstructure**: Historical microstructure data

## 🔧 TECHNICAL SPECIFICATIONS

### **System Architecture**
```
IQFeed (Data) → MIA_IA_SYSTEM → Sierra Chart (Execution)
```

### **Data Frequency**
- **Real-time**: Continuous streaming 24h/5d
- **Tick data**: All ES/SPX ticks
- **Update frequency**: <50ms latency required
- **Availability**: 99.9% uptime minimum

### **API Requirements**
- **REST API**: For historical data and snapshots
- **WebSocket**: For real-time streaming
- **Python SDK**: Official Python library
- **Documentation**: Complete technical documentation
- **Support**: Responsive technical support

## 📊 SPECIFIC USAGE

### **Battle Navale Strategy**
My system uses 8 advanced technical indicators:
1. **Gamma Levels Proximity** (32%) - Gamma walls proximity analysis
2. **Volume Confirmation** (23%) - Volume movement validation
3. **VWAP Trend Signal** (18%) - Position vs directional VWAP
4. **Sierra Pattern Strength** (18%) - Sierra Chart patterns
5. **Options Flow Bias** (15%) - Options market sentiment
6. **Order Book Imbalance** (15%) - Bid/ask imbalances
7. **ES/NQ Correlation** (8%) - ES/Nasdaq correlation
8. **Market Regime** (8%) - Current market regime

### **Trading Frequency**
- **Signals generated**: 8-12 signals per day
- **Trades executed**: 5-8 trades per day
- **Sessions**: London, NY, Asia
- **Timeframes**: 1m, 5m, 15m, 1h, 4h

## 💰 BUDGET AND CONSTRAINTS

### **Monthly Budget**
- **Target budget**: 100-200€/month
- **Maximum budget**: 300€/month
- **Commitment period**: 12 months minimum

### **Alternatives Considered**
- **IBKR TWS**: 19.44€/month (connection issues)
- **Polygon.io**: 99€/month (backup solution)
- **IQFeed**: To be determined (sought solution)

## 🎯 SPECIFIC QUESTIONS

### **1. Data Coverage**
- Are ES futures data available in real-time?
- Do SPX options include all strikes and expirations?
- Is Level 2 order flow available for ES?
- Do historical data go back 2+ years?

### **2. API and Integration**
- Is there an official Python library?
- Is technical documentation complete?
- Is technical support available in French?
- Are there API request limitations?

### **3. Performance and Reliability**
- What is the average latency of real-time data?
- What is the guaranteed uptime rate?
- Are there failover mechanisms?
- Are data validated for quality?

### **4. Costs and Conditions**
- What are the exact rates for my needs?
- Are there installation or activation fees?
- Are there discounts for long-term commitment?
- Is there a free trial period?

## 📞 CONTACT AND FOLLOW-UP

### **Contact Information**
- **Email**: [your.email@domain.com]
- **Phone**: [your.number]
- **Availability**: 9am-6pm (CET)

### **Next Steps**
1. **Receive quote**: Detailed rates for my needs
2. **Demonstration**: API and data testing (if possible)
3. **Trial period**: Technical validation (1-2 weeks)
4. **Contract**: Commitment if validation successful

## 📋 NEEDS SUMMARY

| Data Type | Frequency | Priority | Estimated Budget |
|-----------|-----------|----------|------------------|
| **ES Futures** | Real-time | Critical | 50-100€/month |
| **SPX Options** | Real-time | Critical | 50-100€/month |
| **Order Flow** | Real-time | Important | 30-50€/month |
| **Historical** | On demand | Medium | 20-30€/month |
| **API Support** | Continuous | Critical | Included |

## 🎯 FINAL OBJECTIVE

I am looking for a reliable and stable data partner to operate my MIA_IA_SYSTEM in production. Data quality and reliability are critical to the success of my trading strategy.

Thank you for your attention to my request and I remain at your disposal for any questions or clarifications.

Best regards,

**[Your Name]**  
MIA_IA_SYSTEM Developer  
[Your Email]  
[Your Phone]

---

**P.S.**: If you have specific technical questions about my needs, I can provide additional details about my system's architecture.














