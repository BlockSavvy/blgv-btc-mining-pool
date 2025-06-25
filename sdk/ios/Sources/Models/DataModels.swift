import Foundation

// MARK: - User Models
public struct BLGVUser: Codable, Identifiable {
    public let id: String
    public let walletAddress: String
    public let profileId: String
    public let permissions: UserPermissions
    public let portfolioValue: Decimal
    public let miningStats: MinerStatistics
    public let tradingLevel: TradingLevel
    public let preferences: UserPreferences
    public let createdAt: Date
    public let lastActiveAt: Date
    
    public init(
        walletAddress: String,
        profileId: String,
        permissions: UserPermissions,
        portfolioValue: Decimal,
        miningStats: MinerStatistics,
        tradingLevel: TradingLevel,
        preferences: UserPreferences
    ) {
        self.id = profileId
        self.walletAddress = walletAddress
        self.profileId = profileId
        self.permissions = permissions
        self.portfolioValue = portfolioValue
        self.miningStats = miningStats
        self.tradingLevel = tradingLevel
        self.preferences = preferences
        self.createdAt = Date()
        self.lastActiveAt = Date()
    }
}

public struct UserPermissions: Codable {
    public let canTrade: Bool
    public let canMine: Bool
    public let canAccessIntelligence: Bool
    public let apiAccessLevel: APIAccessLevel
    
    public enum APIAccessLevel: String, Codable {
        case basic = "basic"
        case premium = "premium"
        case institutional = "institutional"
    }
}

public struct UserPreferences: Codable {
    public let currency: String
    public let timezone: String
    public let notificationSettings: NotificationSettings
    public let tradingPreferences: TradingPreferences
    public let miningPreferences: MiningPreferences
}

// MARK: - Portfolio Models
public struct EcosystemPortfolio: Codable, Identifiable {
    public let id = UUID()
    public let dexHoldings: [TokenHolding]
    public let miningRewards: MiningRewards
    public let aiAnalysis: PortfolioAnalysis
    public let totalValue: Decimal
    public let performance: PerformanceMetrics
    public let lastUpdated: Date
    
    public var totalBTCValue: Decimal {
        dexHoldings.reduce(0) { $0 + $1.btcValue } + miningRewards.totalBTC
    }
    
    public var diversification: DiversificationMetrics {
        DiversificationMetrics(holdings: dexHoldings)
    }
}

public struct TokenHolding: Codable, Identifiable {
    public let id = UUID()
    public let symbol: String
    public let name: String
    public let balance: Decimal
    public let usdValue: Decimal
    public let btcValue: Decimal
    public let percentage: Double
    public let priceChange24h: Double
    public let logo: String?
}

public struct MiningRewards: Codable {
    public let totalBTC: Decimal
    public let totalUSD: Decimal
    public let pendingBTC: Decimal
    public let paidBTC: Decimal
    public let performance: PerformanceMetrics
    public let payoutHistory: [Payout]
    public let lastPayout: Date?
    
    public var totalValue: Decimal { totalUSD }
}

public struct PerformanceMetrics: Codable {
    public let totalReturn: Decimal
    public let totalReturnPercent: Double
    public let dailyChange: Decimal
    public let dailyChangePercent: Double
    public let weeklyChange: Decimal
    public let weeklyChangePercent: Double
    public let monthlyChange: Decimal
    public let monthlyChangePercent: Double
    public let yearlyChange: Decimal
    public let yearlyChangePercent: Double
}

// MARK: - Trading Models
public struct TradingPair: Codable, Identifiable {
    public let id: String
    public let baseSymbol: String
    public let quoteSymbol: String
    public let price: Decimal
    public let volume24h: Decimal
    public let change24h: Double
    public let high24h: Decimal
    public let low24h: Decimal
    public let bid: Decimal
    public let ask: Decimal
    public let spread: Double
}

public struct Order: Codable, Identifiable {
    public let id: String
    public let pair: String
    public let side: OrderSide
    public let type: OrderType
    public let amount: Decimal
    public let price: Decimal?
    public let status: OrderStatus
    public let filled: Decimal
    public let remaining: Decimal
    public let createdAt: Date
    public let updatedAt: Date
    
    public enum OrderSide: String, Codable {
        case buy = "buy"
        case sell = "sell"
    }
    
    public enum OrderType: String, Codable {
        case market = "market"
        case limit = "limit"
        case stopLoss = "stop_loss"
        case takeProfit = "take_profit"
    }
    
    public enum OrderStatus: String, Codable {
        case pending = "pending"
        case open = "open"
        case filled = "filled"
        case cancelled = "cancelled"
        case rejected = "rejected"
    }
}

public struct Portfolio: Codable {
    public let holdings: [TokenHolding]
    public let totalValue: Decimal
    public let performance: PerformanceMetrics
    public let allocation: AssetAllocation
    public let rebalanceRecommendations: [RebalanceRecommendation]
}

// MARK: - Mining Models
public struct MinerStatistics: Codable {
    public let hashRate: String
    public let sharesSubmitted: Int
    public let sharesAccepted: Int
    public let sharesRejected: Int
    public let efficiency: Double
    public let uptime: Double
    public let lastSeen: Date
    public let workers: [WorkerStats]
    public let earnings: EarningsBreakdown
}

public struct WorkerStats: Codable, Identifiable {
    public let id: String
    public let name: String
    public let hashRate: String
    public let temperature: Double?
    public let power: Double?
    public let efficiency: Double
    public let status: WorkerStatus
    public let lastSeen: Date
    
    public enum WorkerStatus: String, Codable {
        case online = "online"
        case offline = "offline"
        case error = "error"
        case maintenance = "maintenance"
    }
}

public struct PoolStats: Codable {
    public let totalHashRate: String
    public let activeMiners: Int
    public let blocksFound: Int
    public let networkDifficulty: String
    public let nextDifficultyAdjustment: Date
    public let poolFee: Double
    public let payoutThreshold: Decimal
    public let lastBlockFound: Date?
}

public struct Payout: Codable, Identifiable {
    public let id: String
    public let amount: Decimal
    public let txHash: String
    public let timestamp: Date
    public let status: PayoutStatus
    public let fee: Decimal
    
    public enum PayoutStatus: String, Codable {
        case pending = "pending"
        case confirmed = "confirmed"
        case failed = "failed"
    }
}

// MARK: - Intelligence Models
public struct MarketAnalysis: Codable {
    public let sentiment: SentimentAnalysis
    public let priceTargets: [PriceTarget]
    public let recommendations: [AIRecommendation]
    public let riskAssessment: RiskAssessment
    public let marketTrends: [MarketTrend]
    public let generatedAt: Date
}

public struct SentimentAnalysis: Codable {
    public let overall: SentimentScore
    public let social: SentimentScore
    public let news: SentimentScore
    public let technical: SentimentScore
    public let confidence: Double
    
    public enum SentimentScore: String, Codable {
        case veryBearish = "very_bearish"
        case bearish = "bearish"
        case neutral = "neutral"
        case bullish = "bullish"
        case veryBullish = "very_bullish"
    }
}

public struct AIRecommendation: Codable, Identifiable {
    public let id = UUID()
    public let type: RecommendationType
    public let asset: String
    public let action: RecommendedAction
    public let confidence: Double
    public let reasoning: String
    public let timeframe: String
    public let riskLevel: RiskLevel
    public let createdAt: Date
    
    public enum RecommendationType: String, Codable {
        case trading = "trading"
        case mining = "mining"
        case portfolio = "portfolio"
        case risk = "risk"
    }
    
    public enum RecommendedAction: String, Codable {
        case buy = "buy"
        case sell = "sell"
        case hold = "hold"
        case increase = "increase"
        case decrease = "decrease"
        case rebalance = "rebalance"
    }
    
    public enum RiskLevel: String, Codable {
        case low = "low"
        case medium = "medium"
        case high = "high"
        case veryHigh = "very_high"
    }
}

// MARK: - Real-time Update Models
public struct PriceUpdate: Codable, Identifiable {
    public let id = UUID()
    public let symbol: String
    public let price: Decimal
    public let change24h: Double
    public let volume: Decimal
    public let timestamp: Date
}

public struct MiningUpdate: Codable, Identifiable {
    public let id = UUID()
    public let stats: MinerStatistics
    public let poolStats: PoolStats
    public let timestamp: Date
}

public struct OrderUpdate: Codable, Identifiable {
    public let id = UUID()
    public let orderId: String
    public let status: Order.OrderStatus
    public let filled: Decimal
    public let remaining: Decimal
    public let timestamp: Date
}

public struct PortfolioUpdate: Codable, Identifiable {
    public let id = UUID()
    public let totalValue: Decimal
    public let change: Decimal
    public let changePercent: Double
    public let timestamp: Date
}

public struct AlertUpdate: Codable, Identifiable {
    public let id = UUID()
    public let type: AlertType
    public let title: String
    public let message: String
    public let severity: AlertSeverity
    public let timestamp: Date
    
    public enum AlertType: String, Codable {
        case priceAlert = "price_alert"
        case orderFilled = "order_filled"
        case minerOffline = "miner_offline"
        case payoutReceived = "payout_received"
        case securityAlert = "security_alert"
    }
    
    public enum AlertSeverity: String, Codable {
        case info = "info"
        case warning = "warning"
        case error = "error"
        case critical = "critical"
    }
}

// MARK: - Helper Models
public struct AuthToken: Codable {
    public let accessToken: String
    public let refreshToken: String
    public let expiresAt: Date
    public let tokenType: String
}

public struct TradingLevel: Codable {
    public let level: Int
    public let name: String
    public let requirements: TradingRequirements
    public let benefits: TradingBenefits
}

public struct TradingRequirements: Codable {
    public let minimumVolume: Decimal
    public let minimumBalance: Decimal
    public let verificationLevel: String
}

public struct TradingBenefits: Codable {
    public let reducedFees: Double
    public let advancedFeatures: [String]
    public let prioritySupport: Bool
}

public struct NotificationSettings: Codable {
    public let priceAlerts: Bool
    public let orderUpdates: Bool
    public let miningAlerts: Bool
    public let marketNews: Bool
    public let pushNotifications: Bool
    public let emailNotifications: Bool
}

public struct TradingPreferences: Codable {
    public let defaultOrderType: Order.OrderType
    public let riskTolerance: RiskLevel
    public let autoRebalance: Bool
    public let stopLossPercentage: Double?
    public let takeProfitPercentage: Double?
}

public struct MiningPreferences: Codable {
    public let autoReinvest: Bool
    public let payoutThreshold: Decimal
    public let preferredPool: String?
    public let notifyOnOfflineWorkers: Bool
}

public struct AssetAllocation: Codable {
    public let btc: Double
    public let altcoins: Double
    public let stablecoins: Double
    public let target: AllocationTarget
}

public struct AllocationTarget: Codable {
    public let btc: Double
    public let altcoins: Double
    public let stablecoins: Double
}

public struct RebalanceRecommendation: Codable, Identifiable {
    public let id = UUID()
    public let asset: String
    public let currentAllocation: Double
    public let targetAllocation: Double
    public let recommendedAction: String
    public let amount: Decimal
}

public struct DiversificationMetrics: Codable {
    public let concentrationRisk: Double
    public let numberOfAssets: Int
    public let largestHolding: Double
    public let herfindahlIndex: Double
    
    public init(holdings: [TokenHolding]) {
        self.numberOfAssets = holdings.count
        let percentages = holdings.map { $0.percentage }
        self.largestHolding = percentages.max() ?? 0
        self.herfindahlIndex = percentages.reduce(0) { $0 + ($1 * $1) }
        self.concentrationRisk = largestHolding > 50 ? largestHolding / 100 : 0
    }
}

public struct PriceTarget: Codable {
    public let asset: String
    public let target: Decimal
    public let timeframe: String
    public let confidence: Double
    public let analysis: String
}

public struct RiskAssessment: Codable {
    public let overallRisk: RiskLevel
    public let portfolioRisk: Double
    public let marketRisk: Double
    public let concentrationRisk: Double
    public let recommendations: [String]
}

public struct MarketTrend: Codable, Identifiable {
    public let id = UUID()
    public let asset: String
    public let trend: TrendDirection
    public let strength: Double
    public let timeframe: String
    public let indicators: [String]
    
    public enum TrendDirection: String, Codable {
        case uptrend = "uptrend"
        case downtrend = "downtrend"
        case sideways = "sideways"
        case reversal = "reversal"
    }
}

public struct EarningsBreakdown: Codable {
    public let daily: Decimal
    public let weekly: Decimal
    public let monthly: Decimal
    public let total: Decimal
    public let projectedMonthly: Decimal
}