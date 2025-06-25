import Foundation
import Alamofire

/// Client for BLGV DEX trading and portfolio management
public class DEXClient: ObservableObject {
    
    // MARK: - Properties
    private let endpoint: String
    private let session: Session
    private var authToken: AuthToken?
    
    @Published public var isConnected = false
    @Published public var tradingPairs: [TradingPair] = []
    @Published public var portfolio: Portfolio?
    @Published public var activeOrders: [Order] = []
    
    // MARK: - Initialization
    public init(endpoint: String, session: Session) {
        self.endpoint = endpoint
        self.session = session
    }
    
    public func initialize() async {
        await loadTradingPairs()
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
    
    // MARK: - Trading Operations
    
    /// Get all available trading pairs
    public func getTradingPairs() async throws -> [TradingPair] {
        let response = try await session.request(
            "\(endpoint)/api/trading-pairs",
            headers: headers
        ).serializingDecodable([TradingPair].self).value
        
        DispatchQueue.main.async {
            self.tradingPairs = response
        }
        
        return response
    }
    
    /// Get order book for a specific trading pair
    public func getOrderBook(pair: String) async throws -> OrderBook {
        return try await session.request(
            "\(endpoint)/api/orderbook/\(pair)",
            headers: headers
        ).serializingDecodable(OrderBook.self).value
    }
    
    /// Place a new order
    public func placeOrder(_ order: NewOrder) async throws -> OrderResult {
        let parameters: [String: Any] = [
            "pair": order.pair,
            "side": order.side.rawValue,
            "type": order.type.rawValue,
            "amount": order.amount,
            "price": order.price as Any
        ]
        
        return try await session.request(
            "\(endpoint)/api/orders",
            method: .post,
            parameters: parameters,
            encoding: JSONEncoding.default,
            headers: headers
        ).serializingDecodable(OrderResult.self).value
    }
    
    /// Cancel an existing order
    public func cancelOrder(orderId: String) async throws -> CancelResult {
        return try await session.request(
            "\(endpoint)/api/orders/\(orderId)",
            method: .delete,
            headers: headers
        ).serializingDecodable(CancelResult.self).value
    }
    
    /// Get active orders
    public func getActiveOrders() async throws -> [Order] {
        let orders = try await session.request(
            "\(endpoint)/api/orders/active",
            headers: headers
        ).serializingDecodable([Order].self).value
        
        DispatchQueue.main.async {
            self.activeOrders = orders
        }
        
        return orders
    }
    
    /// Get order history
    public func getOrderHistory(limit: Int = 50) async throws -> [Order] {
        return try await session.request(
            "\(endpoint)/api/orders/history",
            parameters: ["limit": limit],
            headers: headers
        ).serializingDecodable([Order].self).value
    }
    
    // MARK: - Portfolio Management
    
    /// Get user portfolio
    public func getPortfolio() async throws -> Portfolio {
        let portfolio = try await session.request(
            "\(endpoint)/api/portfolio",
            headers: headers
        ).serializingDecodable(Portfolio.self).value
        
        DispatchQueue.main.async {
            self.portfolio = portfolio
        }
        
        return portfolio
    }
    
    /// Get account balances
    public func getBalances() async throws -> [TokenBalance] {
        return try await session.request(
            "\(endpoint)/api/account/balances",
            headers: headers
        ).serializingDecodable([TokenBalance].self).value
    }
    
    /// Get transaction history
    public func getTransactionHistory(limit: Int = 100) async throws -> [Transaction] {
        return try await session.request(
            "\(endpoint)/api/account/transactions",
            parameters: ["limit": limit],
            headers: headers
        ).serializingDecodable([Transaction].self).value
    }
    
    /// Get liquidity positions
    public func getLiquidityPositions() async throws -> [LPPosition] {
        return try await session.request(
            "\(endpoint)/api/liquidity/positions",
            headers: headers
        ).serializingDecodable([LPPosition].self).value
    }
    
    // MARK: - User Profile
    
    /// Get user profile
    public func getUserProfile() async throws -> DEXUserProfile {
        return try await session.request(
            "\(endpoint)/api/user/profile",
            headers: headers
        ).serializingDecodable(DEXUserProfile.self).value
    }
    
    /// Update user preferences
    public func updatePreferences(_ preferences: TradingPreferences) async throws {
        try await session.request(
            "\(endpoint)/api/user/preferences",
            method: .put,
            parameters: preferences,
            encoder: JSONParameterEncoder.default,
            headers: headers
        ).serializingDecodable(SuccessResponse.self).value
    }
    
    // MARK: - Market Data
    
    /// Get market statistics
    public func getMarketStats() async throws -> MarketStats {
        return try await session.request(
            "\(endpoint)/api/market/stats"
        ).serializingDecodable(MarketStats.self).value
    }
    
    /// Get price history for a pair
    public func getPriceHistory(pair: String, interval: String, limit: Int = 100) async throws -> [Candle] {
        return try await session.request(
            "\(endpoint)/api/market/history",
            parameters: [
                "pair": pair,
                "interval": interval,
                "limit": limit
            ]
        ).serializingDecodable([Candle].self).value
    }
    
    // MARK: - Private Methods
    
    private func loadTradingPairs() async {
        do {
            let pairs = try await getTradingPairs()
            DispatchQueue.main.async {
                self.tradingPairs = pairs
            }
        } catch {
            print("Failed to load trading pairs: \(error)")
        }
    }
}

// MARK: - Supporting Models

public struct NewOrder: Codable {
    public let pair: String
    public let side: Order.OrderSide
    public let type: Order.OrderType
    public let amount: Decimal
    public let price: Decimal?
    
    public init(pair: String, side: Order.OrderSide, type: Order.OrderType, amount: Decimal, price: Decimal? = nil) {
        self.pair = pair
        self.side = side
        self.type = type
        self.amount = amount
        self.price = price
    }
}

public struct OrderResult: Codable {
    public let orderId: String
    public let status: String
    public let message: String
}

public struct CancelResult: Codable {
    public let success: Bool
    public let message: String
}

public struct OrderBook: Codable {
    public let pair: String
    public let bids: [OrderBookEntry]
    public let asks: [OrderBookEntry]
    public let timestamp: Date
}

public struct OrderBookEntry: Codable {
    public let price: Decimal
    public let amount: Decimal
}

public struct TokenBalance: Codable, Identifiable {
    public let id = UUID()
    public let symbol: String
    public let available: Decimal
    public let reserved: Decimal
    public let total: Decimal
    
    public var totalValue: Decimal { available + reserved }
}

public struct Transaction: Codable, Identifiable {
    public let id: String
    public let type: TransactionType
    public let symbol: String
    public let amount: Decimal
    public let fee: Decimal
    public let status: String
    public let timestamp: Date
    public let txHash: String?
    
    public enum TransactionType: String, Codable {
        case deposit = "deposit"
        case withdrawal = "withdrawal"
        case trade = "trade"
        case fee = "fee"
    }
}

public struct LPPosition: Codable, Identifiable {
    public let id: String
    public let pair: String
    public let liquidity: Decimal
    public let token0Amount: Decimal
    public let token1Amount: Decimal
    public let share: Double
    public let value: Decimal
    public let fees24h: Decimal
    public let apy: Double
}

public struct DEXUserProfile: Codable {
    public let walletAddress: String
    public let profileId: String
    public let permissions: UserPermissions
    public let portfolioValue: Decimal
    public let tradingLevel: TradingLevel
    public let verificationStatus: String
    public let createdAt: Date
}

public struct MarketStats: Codable {
    public let totalVolume24h: Decimal
    public let totalPairs: Int
    public let topGainers: [TradingPair]
    public let topLosers: [TradingPair]
    public let highestVolume: [TradingPair]
}

public struct Candle: Codable {
    public let timestamp: Date
    public let open: Decimal
    public let high: Decimal
    public let low: Decimal
    public let close: Decimal
    public let volume: Decimal
}

public struct SuccessResponse: Codable {
    public let success: Bool
    public let message: String
}