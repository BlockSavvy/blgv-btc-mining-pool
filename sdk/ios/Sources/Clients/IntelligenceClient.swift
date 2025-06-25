import Foundation
import Alamofire

/// Client for BLGV Intelligence Platform AI insights and analysis
public class IntelligenceClient: ObservableObject {
    
    // MARK: - Properties
    private let endpoint: String
    private let session: Session
    private var authToken: AuthToken?
    
    @Published public var isConnected = false
    @Published public var marketAnalysis: MarketAnalysis?
    @Published public var recommendations: [AIRecommendation] = []
    @Published public var priceAlerts: [PriceAlert] = []
    
    // MARK: - Initialization
    public init(endpoint: String, session: Session) {
        self.endpoint = endpoint
        self.session = session
    }
    
    public func initialize() async {
        await loadInitialData()
        isConnected = true
    }
    
    public func setAuthToken(_ token: AuthToken) {
        self.authToken = token
    }
    
    // MARK: - Authentication
    private var headers: HTTPHeaders {
        guard let token = authToken else { return [:] }
        return ["Authorization": "Bearer \(token.accessToken)"]
    }
    
    // MARK: - Market Analysis
    
    /// Get comprehensive market analysis
    public func getMarketAnalysis() async throws -> MarketAnalysis {
        let analysis = try await session.request(
            "\(endpoint)/api/intelligence/market-analysis",
            headers: headers
        ).serializingDecodable(MarketAnalysis.self).value
        
        DispatchQueue.main.async {
            self.marketAnalysis = analysis
        }
        
        return analysis
    }
    
    /// Get AI-powered trading recommendations
    public func getAIRecommendations() async throws -> [AIRecommendation] {
        let recommendations = try await session.request(
            "\(endpoint)/api/intelligence/recommendations",
            headers: headers
        ).serializingDecodable([AIRecommendation].self).value
        
        DispatchQueue.main.async {
            self.recommendations = recommendations
        }
        
        return recommendations
    }
    
    /// Get personalized insights based on user portfolio
    public func getPersonalizedInsights() async throws -> [Insight] {
        return try await session.request(
            "\(endpoint)/api/intelligence/insights/personalized",
            headers: headers
        ).serializingDecodable([Insight].self).value
    }
    
    /// Get market sentiment analysis
    public func getMarketSentiment() async throws -> SentimentAnalysis {
        return try await session.request(
            "\(endpoint)/api/intelligence/sentiment",
            headers: headers
        ).serializingDecodable(SentimentAnalysis.self).value
    }
    
    /// Get portfolio analysis with AI recommendations
    public func getPortfolioAnalysis() async throws -> PortfolioAnalysis {
        return try await session.request(
            "\(endpoint)/api/intelligence/portfolio/analysis",
            headers: headers
        ).serializingDecodable(PortfolioAnalysis.self).value
    }
    
    // MARK: - Price Alerts
    
    /// Get active price alerts
    public func getPriceAlerts() async throws -> [PriceAlert] {
        let alerts = try await session.request(
            "\(endpoint)/api/intelligence/alerts",
            headers: headers
        ).serializingDecodable([PriceAlert].self).value
        
        DispatchQueue.main.async {
            self.priceAlerts = alerts
        }
        
        return alerts
    }
    
    /// Create a new price alert
    public func createPriceAlert(_ alert: CreatePriceAlert) async throws -> PriceAlert {
        return try await session.request(
            "\(endpoint)/api/intelligence/alerts",
            method: .post,
            parameters: alert,
            encoder: JSONParameterEncoder.default,
            headers: headers
        ).serializingDecodable(PriceAlert.self).value
    }
    
    /// Update existing price alert
    public func updatePriceAlert(id: String, alert: UpdatePriceAlert) async throws -> PriceAlert {
        return try await session.request(
            "\(endpoint)/api/intelligence/alerts/\(id)",
            method: .put,
            parameters: alert,
            encoder: JSONParameterEncoder.default,
            headers: headers
        ).serializingDecodable(PriceAlert.self).value
    }
    
    /// Delete price alert
    public func deletePriceAlert(id: String) async throws {
        try await session.request(
            "\(endpoint)/api/intelligence/alerts/\(id)",
            method: .delete,
            headers: headers
        ).serializingDecodable(SuccessResponse.self).value
    }
    
    // MARK: - Research & Analytics
    
    /// Get detailed asset research
    public func getAssetResearch(symbol: String) async throws -> AssetResearch {
        return try await session.request(
            "\(endpoint)/api/intelligence/research/\(symbol)",
            headers: headers
        ).serializingDecodable(AssetResearch.self).value
    }
    
    /// Get risk assessment for portfolio or specific trades
    public func getRiskAssessment(request: RiskAssessmentRequest) async throws -> RiskAssessment {
        return try await session.request(
            "\(endpoint)/api/intelligence/risk/assessment",
            method: .post,
            parameters: request,
            encoder: JSONParameterEncoder.default,
            headers: headers
        ).serializingDecodable(RiskAssessment.self).value
    }
    
    /// Get market trends and technical analysis
    public func getMarketTrends(timeframe: String = "1d") async throws -> [MarketTrend] {
        return try await session.request(
            "\(endpoint)/api/intelligence/trends",
            parameters: ["timeframe": timeframe],
            headers: headers
        ).serializingDecodable([MarketTrend].self).value
    }
    
    /// Get DeFi opportunities and yield farming insights
    public func getDeFiOpportunities() async throws -> [DeFiOpportunity] {
        return try await session.request(
            "\(endpoint)/api/intelligence/defi/opportunities",
            headers: headers
        ).serializingDecodable([DeFiOpportunity].self).value
    }
    
    // MARK: - User Preferences & Settings
    
    /// Get user intelligence preferences
    public func getUserPreferences() async throws -> IntelligencePreferences {
        return try await session.request(
            "\(endpoint)/api/intelligence/user/preferences",
            headers: headers
        ).serializingDecodable(IntelligencePreferences.self).value
    }
    
    /// Update user preferences
    public func updateUserPreferences(_ preferences: IntelligencePreferences) async throws {
        try await session.request(
            "\(endpoint)/api/intelligence/user/preferences",
            method: .put,
            parameters: preferences,
            encoder: JSONParameterEncoder.default,
            headers: headers
        ).serializingDecodable(SuccessResponse.self).value
    }
    
    // MARK: - Backtesting & Strategy Analysis
    
    /// Run strategy backtest
    public func runBacktest(_ strategy: TradingStrategy) async throws -> BacktestResult {
        return try await session.request(
            "\(endpoint)/api/intelligence/backtest",
            method: .post,
            parameters: strategy,
            encoder: JSONParameterEncoder.default,
            headers: headers
        ).serializingDecodable(BacktestResult.self).value
    }
    
    /// Get strategy performance analysis
    public func getStrategyAnalysis(strategyId: String) async throws -> StrategyAnalysis {
        return try await session.request(
            "\(endpoint)/api/intelligence/strategies/\(strategyId)/analysis",
            headers: headers
        ).serializingDecodable(StrategyAnalysis.self).value
    }
    
    // MARK: - News & Social Sentiment
    
    /// Get aggregated news with sentiment analysis
    public func getNewsWithSentiment(symbols: [String] = [], limit: Int = 50) async throws -> [NewsItem] {
        var parameters: [String: Any] = ["limit": limit]
        if !symbols.isEmpty {
            parameters["symbols"] = symbols.joined(separator: ",")
        }
        
        return try await session.request(
            "\(endpoint)/api/intelligence/news",
            parameters: parameters,
            headers: headers
        ).serializingDecodable([NewsItem].self).value
    }
    
    /// Get social media sentiment for specific assets
    public func getSocialSentiment(symbol: String) async throws -> SocialSentiment {
        return try await session.request(
            "\(endpoint)/api/intelligence/social/sentiment/\(symbol)",
            headers: headers
        ).serializingDecodable(SocialSentiment.self).value
    }
    
    // MARK: - Private Methods
    
    private func loadInitialData() async {
        async let analysis = try? getMarketAnalysis()
        async let recommendations = try? getAIRecommendations()
        async let alerts = try? getPriceAlerts()
        
        let _ = await (analysis, recommendations, alerts)
    }
}

// MARK: - Supporting Models

public struct Insight: Codable, Identifiable {
    public let id = UUID()
    public let title: String
    public let description: String
    public let category: InsightCategory
    public let importance: InsightImportance
    public let actionRequired: Bool
    public let relatedAssets: [String]
    public let createdAt: Date
    
    public enum InsightCategory: String, Codable {
        case portfolio = "portfolio"
        case market = "market"
        case risk = "risk"
        case opportunity = "opportunity"
        case warning = "warning"
    }
    
    public enum InsightImportance: String, Codable {
        case low = "low"
        case medium = "medium"
        case high = "high"
        case critical = "critical"
    }
}

public struct PortfolioAnalysis: Codable {
    public let overallScore: Double
    public let riskLevel: RiskLevel
    public let diversificationScore: Double
    public let performanceScore: Double
    public let recommendations: [AIRecommendation]
    public let strengths: [String]
    public let weaknesses: [String]
    public let opportunities: [String]
    public let threats: [String]
    public let rebalanceRecommendations: [RebalanceRecommendation]
}

public struct PriceAlert: Codable, Identifiable {
    public let id: String
    public let symbol: String
    public let type: AlertType
    public let targetPrice: Decimal
    public let currentPrice: Decimal
    public let isActive: Bool
    public let isTriggered: Bool
    public let createdAt: Date
    public let triggeredAt: Date?
    
    public enum AlertType: String, Codable {
        case above = "above"
        case below = "below"
        case percentageChange = "percentage_change"
        case volumeSpike = "volume_spike"
    }
}

public struct CreatePriceAlert: Codable {
    public let symbol: String
    public let type: PriceAlert.AlertType
    public let targetPrice: Decimal
    public let note: String?
    
    public init(symbol: String, type: PriceAlert.AlertType, targetPrice: Decimal, note: String? = nil) {
        self.symbol = symbol
        self.type = type
        self.targetPrice = targetPrice
        self.note = note
    }
}

public struct UpdatePriceAlert: Codable {
    public let targetPrice: Decimal?
    public let isActive: Bool?
    public let note: String?
}

public struct AssetResearch: Codable {
    public let symbol: String
    public let name: String
    public let overview: String
    public let fundamentalAnalysis: FundamentalAnalysis
    public let technicalAnalysis: TechnicalAnalysis
    public let sentimentAnalysis: SentimentAnalysis
    public let priceTargets: [PriceTarget]
    public let risks: [String]
    public let opportunities: [String]
    public let lastUpdated: Date
}

public struct FundamentalAnalysis: Codable {
    public let marketCap: Decimal
    public let volume24h: Decimal
    public let circulatingSupply: Decimal?
    public let maxSupply: Decimal?
    public let developerActivity: Double
    public let communityGrowth: Double
    public let institutionalAdoption: Double
    public let rating: String
}

public struct TechnicalAnalysis: Codable {
    public let trend: MarketTrend.TrendDirection
    public let support: Decimal
    public let resistance: Decimal
    public let rsi: Double
    public let macd: MACDIndicator
    public let movingAverages: MovingAverages
    public let signals: [TechnicalSignal]
}

public struct MACDIndicator: Codable {
    public let macd: Double
    public let signal: Double
    public let histogram: Double
    public let trend: String
}

public struct MovingAverages: Codable {
    public let sma20: Decimal
    public let sma50: Decimal
    public let sma200: Decimal
    public let ema12: Decimal
    public let ema26: Decimal
}

public struct TechnicalSignal: Codable {
    public let indicator: String
    public let signal: String
    public let strength: Double
    public let description: String
}

public struct RiskAssessmentRequest: Codable {
    public let type: AssessmentType
    public let portfolio: [String: Decimal]?
    public let trade: TradeRequest?
    
    public enum AssessmentType: String, Codable {
        case portfolio = "portfolio"
        case trade = "trade"
        case strategy = "strategy"
    }
}

public struct TradeRequest: Codable {
    public let symbol: String
    public let side: String
    public let amount: Decimal
    public let price: Decimal?
}

public struct DeFiOpportunity: Codable, Identifiable {
    public let id = UUID()
    public let protocol: String
    public let type: OpportunityType
    public let apy: Double
    public let tvl: Decimal
    public let riskLevel: RiskLevel
    public let description: String
    public let requirements: [String]
    public let pros: [String]
    public let cons: [String]
    
    public enum OpportunityType: String, Codable {
        case lending = "lending"
        case liquidityMining = "liquidity_mining"
        case staking = "staking"
        case farming = "farming"
        case arbitrage = "arbitrage"
    }
}

public struct IntelligencePreferences: Codable {
    public let riskTolerance: RiskLevel
    public let investmentStyle: InvestmentStyle
    public let notifications: NotificationPreferences
    public let researchDepth: ResearchDepth
    public let autoAlerts: Bool
    public let preferredTimeframes: [String]
    
    public enum InvestmentStyle: String, Codable {
        case conservative = "conservative"
        case moderate = "moderate"
        case aggressive = "aggressive"
        case dayTrader = "day_trader"
        case hodler = "hodler"
    }
    
    public enum ResearchDepth: String, Codable {
        case basic = "basic"
        case intermediate = "intermediate"
        case advanced = "advanced"
        case expert = "expert"
    }
}

public struct NotificationPreferences: Codable {
    public let priceAlerts: Bool
    public let marketNews: Bool
    public let portfolioInsights: Bool
    public let riskWarnings: Bool
    public let opportunities: Bool
    public let frequency: NotificationFrequency
    
    public enum NotificationFrequency: String, Codable {
        case realTime = "real_time"
        case hourly = "hourly"
        case daily = "daily"
        case weekly = "weekly"
    }
}

public struct TradingStrategy: Codable {
    public let name: String
    public let type: StrategyType
    public let parameters: [String: Any]
    public let assets: [String]
    public let timeframe: String
    public let description: String
    
    public enum StrategyType: String, Codable {
        case momentum = "momentum"
        case meanReversion = "mean_reversion"
        case arbitrage = "arbitrage"
        case dca = "dca"
        case gridTrading = "grid_trading"
        case custom = "custom"
    }
    
    public init(name: String, type: StrategyType, parameters: [String: Any], assets: [String], timeframe: String, description: String) {
        self.name = name
        self.type = type
        self.parameters = parameters
        self.assets = assets
        self.timeframe = timeframe
        self.description = description
    }
}

public struct BacktestResult: Codable {
    public let strategyId: String
    public let startDate: Date
    public let endDate: Date
    public let initialBalance: Decimal
    public let finalBalance: Decimal
    public let totalReturn: Decimal
    public let totalReturnPercent: Double
    public let maxDrawdown: Double
    public let sharpeRatio: Double
    public let winRate: Double
    public let trades: [BacktestTrade]
    public let equity: [EquityPoint]
}

public struct BacktestTrade: Codable {
    public let timestamp: Date
    public let symbol: String
    public let side: String
    public let amount: Decimal
    public let price: Decimal
    public let pnl: Decimal
}

public struct EquityPoint: Codable {
    public let timestamp: Date
    public let equity: Decimal
}

public struct StrategyAnalysis: Codable {
    public let performance: PerformanceMetrics
    public let riskMetrics: RiskMetrics
    public let tradeAnalysis: TradeAnalysis
    public let recommendations: [String]
    public let strengths: [String]
    public let weaknesses: [String]
}

public struct RiskMetrics: Codable {
    public let volatility: Double
    public let maxDrawdown: Double
    public let valueAtRisk: Double
    public let sharpeRatio: Double
    public let sortinoRatio: Double
    public let beta: Double
}

public struct TradeAnalysis: Codable {
    public let totalTrades: Int
    public let winningTrades: Int
    public let losingTrades: Int
    public let winRate: Double
    public let averageWin: Decimal
    public let averageLoss: Decimal
    public let profitFactor: Double
}

public struct NewsItem: Codable, Identifiable {
    public let id = UUID()
    public let title: String
    public let summary: String
    public let url: String
    public let source: String
    public let publishedAt: Date
    public let sentiment: SentimentAnalysis.SentimentScore
    public let relatedAssets: [String]
    public let importance: Double
}

public struct SocialSentiment: Codable {
    public let symbol: String
    public let overall: SentimentAnalysis.SentimentScore
    public let twitter: Double
    public let reddit: Double
    public let telegram: Double
    public let volume: Int
    public let trends: [SentimentTrend]
    public let lastUpdated: Date
}

public struct SentimentTrend: Codable {
    public let timestamp: Date
    public let score: Double
    public let volume: Int
}