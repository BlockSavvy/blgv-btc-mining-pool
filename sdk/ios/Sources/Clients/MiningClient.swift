import Foundation
import Alamofire

/// Client for BLGV Mining Pool operations and statistics
public class MiningClient: ObservableObject {
    
    // MARK: - Properties
    private let endpoint: String
    private let session: Session
    private var authToken: AuthToken?
    
    @Published public var isConnected = false
    @Published public var poolStats: PoolStats?
    @Published public var minerStats: MinerStatistics?
    @Published public var payoutHistory: [Payout] = []
    @Published public var workers: [WorkerStats] = []
    
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
    
    // MARK: - Pool Statistics
    
    /// Get comprehensive pool statistics
    public func getPoolStatistics() async throws -> PoolStats {
        let stats = try await session.request(
            "\(endpoint)/api/stats",
            headers: headers
        ).serializingDecodable(PoolStats.self).value
        
        DispatchQueue.main.async {
            self.poolStats = stats
        }
        
        return stats
    }
    
    /// Get real-time mining data
    public func getRealTimeMiningData() async throws -> RealTimeMiningData {
        return try await session.request(
            "\(endpoint)/api/mining/realtime",
            headers: headers
        ).serializingDecodable(RealTimeMiningData.self).value
    }
    
    /// Get pool performance history
    public func getPoolPerformanceHistory(timeframe: String = "24h") async throws -> [PoolPerformancePoint] {
        return try await session.request(
            "\(endpoint)/api/stats/performance",
            parameters: ["timeframe": timeframe],
            headers: headers
        ).serializingDecodable([PoolPerformancePoint].self).value
    }
    
    // MARK: - Miner Management
    
    /// Register a new miner
    public func registerMiner(address: String, workerName: String? = nil) async throws -> MinerRegistrationResult {
        let parameters: [String: Any] = [
            "address": address,
            "worker_name": workerName ?? "default"
        ]
        
        return try await session.request(
            "\(endpoint)/api/miners/register",
            method: .post,
            parameters: parameters,
            encoding: JSONEncoding.default,
            headers: headers
        ).serializingDecodable(MinerRegistrationResult.self).value
    }
    
    /// Get miner statistics by address
    public func getMinerStatistics(address: String) async throws -> MinerStatistics {
        let stats = try await session.request(
            "\(endpoint)/api/miners/\(address)/stats",
            headers: headers
        ).serializingDecodable(MinerStatistics.self).value
        
        DispatchQueue.main.async {
            self.minerStats = stats
        }
        
        return stats
    }
    
    /// Get current user's miner profile
    public func getMinerProfile() async throws -> MinerProfile {
        return try await session.request(
            "\(endpoint)/api/miners/profile",
            headers: headers
        ).serializingDecodable(MinerProfile.self).value
    }
    
    /// Update miner configuration
    public func updateMinerConfig(_ config: MinerConfig) async throws -> MinerConfigResult {
        return try await session.request(
            "\(endpoint)/api/miners/config",
            method: .put,
            parameters: config,
            encoder: JSONParameterEncoder.default,
            headers: headers
        ).serializingDecodable(MinerConfigResult.self).value
    }
    
    // MARK: - Worker Management
    
    /// Get worker statistics
    public func getWorkerStats(minerId: String) async throws -> [WorkerStats] {
        let workers = try await session.request(
            "\(endpoint)/api/miners/\(minerId)/workers",
            headers: headers
        ).serializingDecodable([WorkerStats].self).value
        
        DispatchQueue.main.async {
            self.workers = workers
        }
        
        return workers
    }
    
    /// Add new worker
    public func addWorker(_ worker: CreateWorkerRequest) async throws -> WorkerStats {
        return try await session.request(
            "\(endpoint)/api/workers",
            method: .post,
            parameters: worker,
            encoder: JSONParameterEncoder.default,
            headers: headers
        ).serializingDecodable(WorkerStats.self).value
    }
    
    /// Update worker configuration
    public func updateWorker(id: String, config: UpdateWorkerRequest) async throws -> WorkerStats {
        return try await session.request(
            "\(endpoint)/api/workers/\(id)",
            method: .put,
            parameters: config,
            encoder: JSONParameterEncoder.default,
            headers: headers
        ).serializingDecodable(WorkerStats.self).value
    }
    
    /// Remove worker
    public func removeWorker(id: String) async throws {
        try await session.request(
            "\(endpoint)/api/workers/\(id)",
            method: .delete,
            headers: headers
        ).serializingDecodable(SuccessResponse.self).value
    }
    
    // MARK: - Payouts & Earnings
    
    /// Get payout history
    public func getPayoutHistory(limit: Int = 50) async throws -> [Payout] {
        let payouts = try await session.request(
            "\(endpoint)/api/payouts",
            parameters: ["limit": limit],
            headers: headers
        ).serializingDecodable([Payout].self).value
        
        DispatchQueue.main.async {
            self.payoutHistory = payouts
        }
        
        return payouts
    }
    
    /// Get mining rewards breakdown
    public func getMiningRewards() async throws -> MiningRewards {
        return try await session.request(
            "\(endpoint)/api/miners/rewards",
            headers: headers
        ).serializingDecodable(MiningRewards.self).value
    }
    
    /// Get earnings projections
    public func getEarningsProjections() async throws -> EarningsProjections {
        return try await session.request(
            "\(endpoint)/api/miners/projections",
            headers: headers
        ).serializingDecodable(EarningsProjections.self).value
    }
    
    /// Request manual payout
    public func requestPayout(amount: Decimal? = nil) async throws -> PayoutRequest {
        var parameters: [String: Any] = [:]
        if let amount = amount {
            parameters["amount"] = amount
        }
        
        return try await session.request(
            "\(endpoint)/api/payouts/request",
            method: .post,
            parameters: parameters,
            encoding: JSONEncoding.default,
            headers: headers
        ).serializingDecodable(PayoutRequest.self).value
    }
    
    // MARK: - Mining Configuration
    
    /// Generate mining configuration for specific hardware
    public func generateMiningConfig(_ request: MiningConfigRequest) async throws -> MiningConfigResponse {
        return try await session.request(
            "\(endpoint)/api/config/generate",
            method: .post,
            parameters: request,
            encoder: JSONParameterEncoder.default,
            headers: headers
        ).serializingDecodable(MiningConfigResponse.self).value
    }
    
    /// Get recommended mining settings
    public func getMiningRecommendations() async throws -> [MiningRecommendation] {
        return try await session.request(
            "\(endpoint)/api/mining/recommendations",
            headers: headers
        ).serializingDecodable([MiningRecommendation].self).value
    }
    
    /// Get hardware compatibility information
    public func getHardwareCompatibility(model: String) async throws -> HardwareCompatibility {
        return try await session.request(
            "\(endpoint)/api/hardware/compatibility",
            parameters: ["model": model],
            headers: headers
        ).serializingDecodable(HardwareCompatibility.self).value
    }
    
    // MARK: - Analytics & Performance
    
    /// Get detailed mining analytics
    public func getMiningAnalytics(timeframe: String = "7d") async throws -> MiningAnalytics {
        return try await session.request(
            "\(endpoint)/api/analytics",
            parameters: ["timeframe": timeframe],
            headers: headers
        ).serializingDecodable(MiningAnalytics.self).value
    }
    
    /// Get efficiency metrics
    public func getEfficiencyMetrics() async throws -> EfficiencyMetrics {
        return try await session.request(
            "\(endpoint)/api/miners/efficiency",
            headers: headers
        ).serializingDecodable(EfficiencyMetrics.self).value
    }
    
    /// Get comparative performance data
    public func getComparativePerformance() async throws -> ComparativePerformance {
        return try await session.request(
            "\(endpoint)/api/miners/performance/compare",
            headers: headers
        ).serializingDecodable(ComparativePerformance.self).value
    }
    
    // MARK: - Network Information
    
    /// Get Bitcoin network statistics
    public func getNetworkStats() async throws -> NetworkStats {
        return try await session.request(
            "\(endpoint)/api/network/stats"
        ).serializingDecodable(NetworkStats.self).value
    }
    
    /// Get difficulty adjustment predictions
    public func getDifficultyPredictions() async throws -> DifficultyPredictions {
        return try await session.request(
            "\(endpoint)/api/network/difficulty/predictions"
        ).serializingDecodable(DifficultyPredictions.self).value
    }
    
    // MARK: - Support & Monitoring
    
    /// Submit support ticket
    public func submitSupportTicket(_ ticket: SupportTicketRequest) async throws -> SupportTicket {
        return try await session.request(
            "\(endpoint)/api/support/tickets",
            method: .post,
            parameters: ticket,
            encoder: JSONParameterEncoder.default,
            headers: headers
        ).serializingDecodable(SupportTicket.self).value
    }
    
    /// Get system status
    public func getSystemStatus() async throws -> SystemStatus {
        return try await session.request(
            "\(endpoint)/api/system/status"
        ).serializingDecodable(SystemStatus.self).value
    }
    
    // MARK: - Private Methods
    
    private func loadInitialData() async {
        async let poolStats = try? getPoolStatistics()
        async let payouts = try? getPayoutHistory(limit: 10)
        
        let _ = await (poolStats, payouts)
    }
}

// MARK: - Supporting Models

public struct RealTimeMiningData: Codable {
    public let currentHashRate: String
    public let activeWorkers: Int
    public let currentRound: MiningRound
    public let networkDifficulty: String
    public let nextBlockReward: Decimal
    public let estimatedBlockTime: TimeInterval
    public let poolLuck: Double
    public let timestamp: Date
}

public struct MiningRound: Codable {
    public let number: Int
    public let startTime: Date
    public let shares: Int
    public let progress: Double
    public let estimatedCompletion: Date
}

public struct PoolPerformancePoint: Codable {
    public let timestamp: Date
    public let hashRate: String
    public let miners: Int
    public let blocks: Int
    public let luck: Double
}

public struct MinerRegistrationResult: Codable {
    public let success: Bool
    public let minerId: String
    public let message: String
    public let configUrl: String?
}

public struct MinerProfile: Codable {
    public let minerId: String
    public let walletAddress: String
    public let registrationDate: Date
    public let statistics: MinerStatistics
    public let preferences: MinerPreferences
    public let tier: MinerTier
    public let achievements: [Achievement]
}

public struct MinerPreferences: Codable {
    public let autoReinvest: Bool
    public let payoutThreshold: Decimal
    public let notificationSettings: MiningNotificationSettings
    public let preferredDifficulty: String?
}

public struct MinerTier: Codable {
    public let level: Int
    public let name: String
    public let benefits: [String]
    public let requirements: TierRequirements
}

public struct TierRequirements: Codable {
    public let minimumHashRate: String
    public let minimumUptime: Double
    public let minimumDuration: TimeInterval
}

public struct Achievement: Codable, Identifiable {
    public let id: String
    public let name: String
    public let description: String
    public let unlockedAt: Date
    public let category: AchievementCategory
    
    public enum AchievementCategory: String, Codable {
        case mining = "mining"
        case efficiency = "efficiency"
        case loyalty = "loyalty"
        case milestone = "milestone"
    }
}

public struct MinerConfig: Codable {
    public let poolUrl: String
    public let workerName: String
    public let difficulty: String?
    public let payoutAddress: String
    public let autoReinvest: Bool
    public let notifications: MiningNotificationSettings
}

public struct MiningNotificationSettings: Codable {
    public let workerOffline: Bool
    public let payoutReceived: Bool
    public let blockFound: Bool
    public let efficiencyAlerts: Bool
}

public struct MinerConfigResult: Codable {
    public let success: Bool
    public let message: String
    public let restartRequired: Bool
}

public struct CreateWorkerRequest: Codable {
    public let name: String
    public let hardwareModel: String
    public let difficulty: String?
    public let location: String?
}

public struct UpdateWorkerRequest: Codable {
    public let name: String?
    public let difficulty: String?
    public let isActive: Bool?
}

public struct EarningsProjections: Codable {
    public let daily: Decimal
    public let weekly: Decimal
    public let monthly: Decimal
    public let yearly: Decimal
    public let basedOnHashRate: String
    public let assumptions: [String]
    public let confidence: Double
}

public struct PayoutRequest: Codable {
    public let requestId: String
    public let amount: Decimal
    public let estimatedProcessingTime: TimeInterval
    public let fee: Decimal
    public let status: String
}

public struct MiningConfigRequest: Codable {
    public let hardwareType: HardwareType
    public let model: String
    public let powerLimit: Double?
    public let fanSpeed: Double?
    public let difficulty: String?
    
    public enum HardwareType: String, Codable {
        case asic = "asic"
        case gpu = "gpu"
        case fpga = "fpga"
        case bitaxe = "bitaxe"
    }
}

public struct MiningConfigResponse: Codable {
    public let config: String
    public let filename: String
    public let instructions: [String]
    public let expectedHashRate: String
    public let powerConsumption: Double
    public let efficiency: Double
}

public struct MiningRecommendation: Codable, Identifiable {
    public let id = UUID()
    public let type: RecommendationType
    public let title: String
    public let description: String
    public let impact: Impact
    public let difficulty: Difficulty
    public let estimatedBenefit: String
    
    public enum RecommendationType: String, Codable {
        case hardware = "hardware"
        case software = "software"
        case configuration = "configuration"
        case strategy = "strategy"
    }
    
    public enum Impact: String, Codable {
        case low = "low"
        case medium = "medium"
        case high = "high"
    }
    
    public enum Difficulty: String, Codable {
        case easy = "easy"
        case medium = "medium"
        case hard = "hard"
    }
}

public struct HardwareCompatibility: Codable {
    public let model: String
    public let isSupported: Bool
    public let recommendedSettings: [String: Any]?
    public let limitations: [String]
    public let alternativeModels: [String]
}

public struct MiningAnalytics: Codable {
    public let overview: AnalyticsOverview
    public let performance: PerformanceAnalytics
    public let earnings: EarningsAnalytics
    public let efficiency: EfficiencyAnalytics
    public let comparisons: ComparisonAnalytics
}

public struct AnalyticsOverview: Codable {
    public let totalEarnings: Decimal
    public let averageHashRate: String
    public let uptime: Double
    public let blocksContributed: Int
    public let rankingPercentile: Double
}

public struct PerformanceAnalytics: Codable {
    public let hashRateTrend: [DataPoint]
    public let uptimeTrend: [DataPoint]
    public let efficiencyTrend: [DataPoint]
    public let temperatureTrend: [DataPoint]?
}

public struct EarningsAnalytics: Codable {
    public let dailyEarnings: [DataPoint]
    public let cumulativeEarnings: [DataPoint]
    public let projectedEarnings: ProjectedEarnings
    public let earningsBreakdown: EarningsBreakdown
}

public struct EfficiencyAnalytics: Codable {
    public let powerEfficiency: Double
    public let hashRateStability: Double
    public let optimizationScore: Double
    public let improvementSuggestions: [String]
}

public struct ComparisonAnalytics: Codable {
    public let poolRanking: Int
    public let percentilePe: Double
    public let similarMinersComparison: [MinerComparison]
}

public struct DataPoint: Codable {
    public let timestamp: Date
    public let value: Double
}

public struct ProjectedEarnings: Codable {
    public let nextDay: Decimal
    public let nextWeek: Decimal
    public let nextMonth: Decimal
    public let confidence: Double
}

public struct MinerComparison: Codable {
    public let metric: String
    public let yourValue: Double
    public let averageValue: Double
    public let percentile: Double
}

public struct EfficiencyMetrics: Codable {
    public let hashRateEfficiency: Double
    public let powerEfficiency: Double
    public let uptimeEfficiency: Double
    public let overallScore: Double
    public let improvementAreas: [ImprovementArea]
}

public struct ImprovementArea: Codable {
    public let area: String
    public let currentScore: Double
    public let potentialImprovement: Double
    public let recommendations: [String]
}

public struct ComparativePerformance: Codable {
    public let poolRank: Int
    public let totalMiners: Int
    public let percentile: Double
    public let benchmarks: [PerformanceBenchmark]
    public let strengths: [String]
    public let improvements: [String]
}

public struct PerformanceBenchmark: Codable {
    public let metric: String
    public let yourValue: String
    public let poolAverage: String
    public let topTier: String
    public let performance: BenchmarkPerformance
    
    public enum BenchmarkPerformance: String, Codable {
        case excellent = "excellent"
        case good = "good"
        case average = "average"
        case belowAverage = "below_average"
        case poor = "poor"
    }
}

public struct NetworkStats: Codable {
    public let blockHeight: Int
    public let difficulty: String
    public let hashRate: String
    public let nextDifficultyAdjustment: Date
    public let estimatedDifficultyChange: Double
    public let averageBlockTime: TimeInterval
    public let memPoolSize: Int
}

public struct DifficultyPredictions: Codable {
    public let nextAdjustment: DifficultyAdjustment
    public let predictions: [DifficultyPrediction]
    public let factors: [String]
}

public struct DifficultyAdjustment: Codable {
    public let estimatedDate: Date
    public let estimatedChange: Double
    public let confidence: Double
    public let blocksRemaining: Int
}

public struct DifficultyPrediction: Codable {
    public let timeframe: String
    public let estimatedDifficulty: String
    public let change: Double
    public let confidence: Double
}

public struct SupportTicketRequest: Codable {
    public let category: TicketCategory
    public let subject: String
    public let description: String
    public let priority: TicketPriority
    public let attachments: [String]?
    
    public enum TicketCategory: String, Codable {
        case technical = "technical"
        case billing = "billing"
        case hardware = "hardware"
        case account = "account"
        case other = "other"
    }
    
    public enum TicketPriority: String, Codable {
        case low = "low"
        case normal = "normal"
        case high = "high"
        case urgent = "urgent"
    }
}

public struct SupportTicket: Codable {
    public let ticketId: String
    public let status: TicketStatus
    public let estimatedResponse: TimeInterval
    public let createdAt: Date
    
    public enum TicketStatus: String, Codable {
        case open = "open"
        case inProgress = "in_progress"
        case resolved = "resolved"
        case closed = "closed"
    }
}

public struct SystemStatus: Codable {
    public let overall: ServiceStatus
    public let services: [ServiceStatus]
    public let uptime: Double
    public let lastIncident: Date?
    
    public enum ServiceStatus: String, Codable {
        case operational = "operational"
        case degraded = "degraded"
        case partialOutage = "partial_outage"
        case majorOutage = "major_outage"
        case maintenance = "maintenance"
    }
}