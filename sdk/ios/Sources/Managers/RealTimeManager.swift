import Foundation
import Starscream
import Combine

/// Protocol for real-time manager delegates
public protocol RealTimeManagerDelegate: AnyObject {
    func connectionDidEstablish()
    func connectionDidFail(error: Error)
    func didReceiveMessage(_ message: RealTimeMessage)
}

/// Manages real-time WebSocket connections across the BLGV ecosystem
public class RealTimeManager: ObservableObject {
    
    // MARK: - Properties
    private var sockets: [String: WebSocket] = [:]
    private var subscriptions: [String: Set<String>] = [:]
    private var reconnectTimers: [String: Timer] = [:]
    
    @Published public var connectionStatus: [String: ConnectionState] = [:]
    @Published public var isConnected = false
    
    public weak var delegate: RealTimeManagerDelegate?
    
    private let maxReconnectAttempts = 5
    private let reconnectDelay: TimeInterval = 5.0
    
    // MARK: - Subjects for streaming data
    private let priceUpdateSubject = PassthroughSubject<PriceUpdate, Never>()
    private let miningUpdateSubject = PassthroughSubject<MiningUpdate, Never>()
    private let orderUpdateSubject = PassthroughSubject<OrderUpdate, Never>()
    private let portfolioUpdateSubject = PassthroughSubject<PortfolioUpdate, Never>()
    private let alertUpdateSubject = PassthroughSubject<AlertUpdate, Never>()
    
    // MARK: - Initialization
    public init() {
        setupConnections()
    }
    
    public func initialize() async {
        await connectToAllEndpoints()
    }
    
    // MARK: - Connection Management
    
    private func setupConnections() {
        let endpoints = [
            "dex": "wss://dex.blgvbtc.com/ws",
            "intelligence": "wss://blgvbtc.com/ws",
            "mining": "wss://pool.blgvbtc.com/ws"
        ]
        
        for (name, url) in endpoints {
            createWebSocketConnection(name: name, url: url)
        }
    }
    
    private func createWebSocketConnection(name: String, url: String) {
        guard let wsUrl = URL(string: url) else {
            print("Invalid WebSocket URL: \(url)")
            return
        }
        
        var request = URLRequest(url: wsUrl)
        request.timeoutInterval = 10
        
        let socket = WebSocket(request: request)
        socket.delegate = self
        
        sockets[name] = socket
        connectionStatus[name] = .disconnected
        subscriptions[name] = Set<String>()
    }
    
    private func connectToAllEndpoints() async {
        for (name, socket) in sockets {
            connect(endpoint: name, socket: socket)
        }
        
        updateOverallConnectionStatus()
    }
    
    private func connect(endpoint: String, socket: WebSocket) {
        connectionStatus[endpoint] = .connecting
        socket.connect()
    }
    
    private func disconnect(endpoint: String) {
        sockets[endpoint]?.disconnect()
        connectionStatus[endpoint] = .disconnected
        stopReconnectTimer(for: endpoint)
    }
    
    private func reconnect(endpoint: String) {
        guard let socket = sockets[endpoint] else { return }
        
        disconnect(endpoint: endpoint)
        
        DispatchQueue.main.asyncAfter(deadline: .now() + reconnectDelay) {
            self.connect(endpoint: endpoint, socket: socket)
        }
    }
    
    // MARK: - Subscription Management
    
    /// Subscribe to price updates
    public func subscribeToPriceUpdates(symbols: [String] = []) -> AsyncStream<PriceUpdate> {
        let subscription = PriceSubscription(symbols: symbols)
        subscribe(endpoint: "dex", subscription: subscription)
        
        return AsyncStream { continuation in
            let cancellable = priceUpdateSubject.sink { update in
                continuation.yield(update)
            }
            
            continuation.onTermination = { _ in
                cancellable.cancel()
            }
        }
    }
    
    /// Subscribe to mining statistics updates
    public func subscribeToMiningStats() -> AsyncStream<MiningUpdate> {
        let subscription = MiningSubscription()
        subscribe(endpoint: "mining", subscription: subscription)
        
        return AsyncStream { continuation in
            let cancellable = miningUpdateSubject.sink { update in
                continuation.yield(update)
            }
            
            continuation.onTermination = { _ in
                cancellable.cancel()
            }
        }
    }
    
    /// Subscribe to order updates
    public func subscribeToOrderUpdates() -> AsyncStream<OrderUpdate> {
        let subscription = OrderSubscription()
        subscribe(endpoint: "dex", subscription: subscription)
        
        return AsyncStream { continuation in
            let cancellable = orderUpdateSubject.sink { update in
                continuation.yield(update)
            }
            
            continuation.onTermination = { _ in
                cancellable.cancel()
            }
        }
    }
    
    /// Subscribe to portfolio updates
    public func subscribeToPortfolioUpdates() -> AsyncStream<PortfolioUpdate> {
        let subscription = PortfolioSubscription()
        subscribe(endpoint: "dex", subscription: subscription)
        
        return AsyncStream { continuation in
            let cancellable = portfolioUpdateSubject.sink { update in
                continuation.yield(update)
            }
            
            continuation.onTermination = { _ in
                cancellable.cancel()
            }
        }
    }
    
    /// Subscribe to alerts
    public func subscribeToAlerts() -> AsyncStream<AlertUpdate> {
        let subscription = AlertSubscription()
        subscribe(endpoint: "intelligence", subscription: subscription)
        
        return AsyncStream { continuation in
            let cancellable = alertUpdateSubject.sink { update in
                continuation.yield(update)
            }
            
            continuation.onTermination = { _ in
                cancellable.cancel()
            }
        }
    }
    
    // MARK: - Private Subscription Methods
    
    private func subscribe<T: Codable>(endpoint: String, subscription: T) {
        guard let socket = sockets[endpoint],
              connectionStatus[endpoint] == .connected else {
            // Queue subscription for when connection is established
            return
        }
        
        let message = WebSocketMessage(
            type: "subscribe",
            data: subscription
        )
        
        sendMessage(socket: socket, message: message)
    }
    
    private func sendMessage<T: Codable>(socket: WebSocket, message: T) {
        do {
            let data = try JSONEncoder().encode(message)
            socket.write(data: data)
        } catch {
            print("Failed to encode WebSocket message: \(error)")
        }
    }
    
    // MARK: - Message Processing
    
    private func processMessage(_ message: String) {
        guard let data = message.data(using: .utf8) else { return }
        
        do {
            let realTimeMessage = try JSONDecoder().decode(RealTimeMessage.self, from: data)
            
            switch realTimeMessage.type {
            case "price_update":
                if let update = try? JSONDecoder().decode(PriceUpdate.self, from: realTimeMessage.data) {
                    priceUpdateSubject.send(update)
                }
                
            case "mining_update":
                if let update = try? JSONDecoder().decode(MiningUpdate.self, from: realTimeMessage.data) {
                    miningUpdateSubject.send(update)
                }
                
            case "order_update":
                if let update = try? JSONDecoder().decode(OrderUpdate.self, from: realTimeMessage.data) {
                    orderUpdateSubject.send(update)
                }
                
            case "portfolio_update":
                if let update = try? JSONDecoder().decode(PortfolioUpdate.self, from: realTimeMessage.data) {
                    portfolioUpdateSubject.send(update)
                }
                
            case "alert_update":
                if let update = try? JSONDecoder().decode(AlertUpdate.self, from: realTimeMessage.data) {
                    alertUpdateSubject.send(update)
                }
                
            default:
                print("Unknown message type: \(realTimeMessage.type)")
            }
            
            delegate?.didReceiveMessage(realTimeMessage)
            
        } catch {
            print("Failed to decode WebSocket message: \(error)")
        }
    }
    
    // MARK: - Reconnection Logic
    
    private func startReconnectTimer(for endpoint: String) {
        stopReconnectTimer(for: endpoint)
        
        reconnectTimers[endpoint] = Timer.scheduledTimer(withTimeInterval: reconnectDelay, repeats: false) { [weak self] _ in
            self?.reconnect(endpoint: endpoint)
        }
    }
    
    private func stopReconnectTimer(for endpoint: String) {
        reconnectTimers[endpoint]?.invalidate()
        reconnectTimers[endpoint] = nil
    }
    
    private func updateOverallConnectionStatus() {
        DispatchQueue.main.async {
            self.isConnected = self.connectionStatus.values.allSatisfy { $0 == .connected }
        }
    }
    
    // MARK: - Cleanup
    
    deinit {
        for (_, socket) in sockets {
            socket.disconnect()
        }
        
        for (_, timer) in reconnectTimers {
            timer.invalidate()
        }
    }
}

// MARK: - WebSocketDelegate

extension RealTimeManager: WebSocketDelegate {
    public func didReceive(event: WebSocketEvent, client: WebSocket) {
        let endpoint = findEndpointName(for: client)
        
        switch event {
        case .connected(let headers):
            print("WebSocket connected to \(endpoint): \(headers)")
            DispatchQueue.main.async {
                self.connectionStatus[endpoint] = .connected
                self.updateOverallConnectionStatus()
                self.delegate?.connectionDidEstablish()
            }
            
        case .disconnected(let reason, let code):
            print("WebSocket disconnected from \(endpoint): \(reason) with code: \(code)")
            DispatchQueue.main.async {
                self.connectionStatus[endpoint] = .disconnected
                self.updateOverallConnectionStatus()
            }
            startReconnectTimer(for: endpoint)
            
        case .text(let string):
            processMessage(string)
            
        case .binary(let data):
            if let string = String(data: data, encoding: .utf8) {
                processMessage(string)
            }
            
        case .error(let error):
            print("WebSocket error on \(endpoint): \(error?.localizedDescription ?? "Unknown error")")
            DispatchQueue.main.async {
                self.connectionStatus[endpoint] = .error
                self.updateOverallConnectionStatus()
            }
            
            if let error = error {
                delegate?.connectionDidFail(error: error)
            }
            
            startReconnectTimer(for: endpoint)
            
        case .viabilityChanged(let isViable):
            print("WebSocket viability changed for \(endpoint): \(isViable)")
            
        case .reconnectSuggested(let shouldReconnect):
            if shouldReconnect {
                reconnect(endpoint: endpoint)
            }
            
        case .cancelled:
            print("WebSocket cancelled for \(endpoint)")
            DispatchQueue.main.async {
                self.connectionStatus[endpoint] = .disconnected
                self.updateOverallConnectionStatus()
            }
        }
    }
    
    private func findEndpointName(for client: WebSocket) -> String {
        for (name, socket) in sockets {
            if socket === client {
                return name
            }
        }
        return "unknown"
    }
}

// MARK: - Supporting Models

public enum ConnectionState {
    case disconnected
    case connecting
    case connected
    case error
}

public struct RealTimeMessage: Codable {
    public let type: String
    public let data: Data
    public let timestamp: Date
    
    public init(type: String, data: Data, timestamp: Date = Date()) {
        self.type = type
        self.data = data
        self.timestamp = timestamp
    }
}

public struct WebSocketMessage<T: Codable>: Codable {
    public let type: String
    public let data: T
    public let timestamp: Date
    
    public init(type: String, data: T, timestamp: Date = Date()) {
        self.type = type
        self.data = data
        self.timestamp = timestamp
    }
}

// MARK: - Subscription Models

public struct PriceSubscription: Codable {
    public let symbols: [String]
    
    public init(symbols: [String] = []) {
        self.symbols = symbols
    }
}

public struct MiningSubscription: Codable {
    public let includeWorkers: Bool
    public let includePool: Bool
    
    public init(includeWorkers: Bool = true, includePool: Bool = true) {
        self.includeWorkers = includeWorkers
        self.includePool = includePool
    }
}

public struct OrderSubscription: Codable {
    public let includeAll: Bool
    
    public init(includeAll: Bool = true) {
        self.includeAll = includeAll
    }
}

public struct PortfolioSubscription: Codable {
    public let includePerformance: Bool
    
    public init(includePerformance: Bool = true) {
        self.includePerformance = includePerformance
    }
}

public struct AlertSubscription: Codable {
    public let types: [String]
    
    public init(types: [String] = []) {
        self.types = types
    }
}