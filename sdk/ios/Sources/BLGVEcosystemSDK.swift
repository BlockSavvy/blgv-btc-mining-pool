import Foundation
import Alamofire
import Starscream
import CryptoSwift
import Crypto

/// Main SDK class providing unified access to BLGV ecosystem
@MainActor
public class BLGVEcosystemSDK: ObservableObject {
    
    // MARK: - Singleton
    public static let shared = BLGVEcosystemSDK()
    
    // MARK: - Properties
    @Published public var isAuthenticated = false
    @Published public var currentUser: BLGVUser?
    @Published public var connectionStatus: ConnectionStatus = .disconnected
    
    // MARK: - Clients
    public let auth: AuthenticationManager
    public let dex: DEXClient
    public let intelligence: IntelligenceClient
    public let mining: MiningClient
    public let realTime: RealTimeManager
    public let security: SecurityManager
    
    // MARK: - Configuration
    private let config: BLGVConfig
    private let session: Session
    
    // MARK: - Initialization
    public init(
        dexEndpoint: String = "https://dex.blgvbtc.com",
        intelligenceEndpoint: String = "https://blgvbtc.com", 
        miningPoolEndpoint: String = "https://pool.blgvbtc.com",
        config: BLGVConfig = .default
    ) {
        self.config = config
        self.session = Session(configuration: config.urlSessionConfiguration)
        
        // Initialize managers
        self.auth = AuthenticationManager(session: session)
        self.security = SecurityManager()
        self.realTime = RealTimeManager()
        
        // Initialize clients
        self.dex = DEXClient(endpoint: dexEndpoint, session: session)
        self.intelligence = IntelligenceClient(endpoint: intelligenceEndpoint, session: session)
        self.mining = MiningClient(endpoint: miningPoolEndpoint, session: session)
        
        setupDelegates()
    }
    
    private func setupDelegates() {
        auth.delegate = self
        realTime.delegate = self
    }
    
    // MARK: - Public Methods
    
    /// Initialize the SDK and establish connections
    public func initialize() async {
        await withTaskGroup(of: Void.self) { group in
            group.addTask { await self.auth.initialize() }
            group.addTask { await self.dex.initialize() }
            group.addTask { await self.intelligence.initialize() }
            group.addTask { await self.mining.initialize() }
            group.addTask { await self.realTime.initialize() }
        }
        
        updateConnectionStatus()
    }
    
    /// Authenticate user with wallet signature
    public func authenticate(walletAddress: String, signature: String) async throws {
        let token = try await auth.authenticate(walletAddress: walletAddress, signature: signature)
        
        // Set authentication for all clients
        dex.setAuthToken(token)
        intelligence.setAuthToken(token)
        mining.setAuthToken(token)
        
        // Load user profile
        currentUser = try await loadUserProfile()
        isAuthenticated = true
    }
    
    /// Get unified ecosystem portfolio
    public func getEcosystemPortfolio() async throws -> EcosystemPortfolio {
        async let dexPortfolio = dex.getPortfolio()
        async let miningRewards = mining.getMiningRewards()
        async let intelligenceData = intelligence.getPortfolioAnalysis()
        
        let (portfolio, rewards, analysis) = try await (dexPortfolio, miningRewards, intelligenceData)
        
        return EcosystemPortfolio(
            dexHoldings: portfolio.holdings,
            miningRewards: rewards,
            aiAnalysis: analysis,
            totalValue: portfolio.totalValue + rewards.totalValue,
            performance: calculatePerformance(portfolio: portfolio, rewards: rewards)
        )
    }
    
    /// Subscribe to real-time ecosystem updates
    public func subscribeToEcosystemUpdates() -> AsyncStream<EcosystemUpdate> {
        AsyncStream { continuation in
            Task {
                await withTaskGroup(of: Void.self) { group in
                    // Subscribe to all real-time feeds
                    group.addTask {
                        for await update in self.realTime.subscribeToPriceUpdates() {
                            continuation.yield(.priceUpdate(update))
                        }
                    }
                    
                    group.addTask {
                        for await update in self.realTime.subscribeToMiningStats() {
                            continuation.yield(.miningUpdate(update))
                        }
                    }
                    
                    group.addTask {
                        for await update in self.realTime.subscribeToOrderUpdates() {
                            continuation.yield(.orderUpdate(update))
                        }
                    }
                }
            }
        }
    }
    
    // MARK: - Private Methods
    
    private func loadUserProfile() async throws -> BLGVUser {
        async let dexProfile = dex.getUserProfile()
        async let miningProfile = mining.getMinerProfile()
        async let intelligenceProfile = intelligence.getUserPreferences()
        
        let (dex, mining, intelligence) = try await (dexProfile, miningProfile, intelligenceProfile)
        
        return BLGVUser(
            walletAddress: dex.walletAddress,
            profileId: dex.profileId,
            permissions: dex.permissions,
            portfolioValue: dex.portfolioValue,
            miningStats: mining.statistics,
            tradingLevel: dex.tradingLevel,
            preferences: intelligence.preferences
        )
    }
    
    private func calculatePerformance(portfolio: Portfolio, rewards: MiningRewards) -> PerformanceMetrics {
        // Calculate combined performance metrics
        let totalReturn = portfolio.performance.totalReturn + rewards.performance.totalReturn
        let dailyChange = portfolio.performance.dailyChange + rewards.performance.dailyChange
        
        return PerformanceMetrics(
            totalReturn: totalReturn,
            dailyChange: dailyChange,
            weeklyChange: portfolio.performance.weeklyChange + rewards.performance.weeklyChange,
            monthlyChange: portfolio.performance.monthlyChange + rewards.performance.monthlyChange
        )
    }
    
    private func updateConnectionStatus() {
        let allConnected = dex.isConnected && intelligence.isConnected && mining.isConnected
        connectionStatus = allConnected ? .connected : .connecting
    }
}

// MARK: - Authentication Delegate
extension BLGVEcosystemSDK: AuthenticationManagerDelegate {
    public func authenticationDidSucceed(token: AuthToken) {
        isAuthenticated = true
    }
    
    public func authenticationDidFail(error: Error) {
        isAuthenticated = false
        currentUser = nil
    }
    
    public func authenticationDidExpire() {
        isAuthenticated = false
        currentUser = nil
    }
}

// MARK: - Real-time Delegate
extension BLGVEcosystemSDK: RealTimeManagerDelegate {
    public func connectionDidEstablish() {
        updateConnectionStatus()
    }
    
    public func connectionDidFail(error: Error) {
        updateConnectionStatus()
    }
}

// MARK: - Configuration
public struct BLGVConfig {
    public let environment: Environment
    public let apiTimeout: TimeInterval
    public let retryPolicy: RetryPolicy
    public let loggingLevel: LogLevel
    public let enableRealTimeUpdates: Bool
    
    public static let `default` = BLGVConfig(
        environment: .production,
        apiTimeout: 30.0,
        retryPolicy: .exponentialBackoff,
        loggingLevel: .info,
        enableRealTimeUpdates: true
    )
    
    var urlSessionConfiguration: URLSessionConfiguration {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = apiTimeout
        config.timeoutIntervalForResource = apiTimeout * 2
        return config
    }
}

// MARK: - Enums
public enum Environment {
    case development
    case staging
    case production
}

public enum ConnectionStatus {
    case disconnected
    case connecting
    case connected
    case error(Error)
}

public enum RetryPolicy {
    case none
    case linear
    case exponentialBackoff
}

public enum LogLevel {
    case debug
    case info
    case warning
    case error
    case none
}

// MARK: - Ecosystem Update Types
public enum EcosystemUpdate {
    case priceUpdate(PriceUpdate)
    case miningUpdate(MiningUpdate)
    case orderUpdate(OrderUpdate)
    case portfolioUpdate(PortfolioUpdate)
    case alertUpdate(AlertUpdate)
}