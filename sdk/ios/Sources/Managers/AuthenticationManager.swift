import Foundation
import Alamofire
import CryptoSwift
import Crypto

/// Protocol for authentication manager delegates
public protocol AuthenticationManagerDelegate: AnyObject {
    func authenticationDidSucceed(token: AuthToken)
    func authenticationDidFail(error: Error)
    func authenticationDidExpire()
}

/// Manages authentication across the BLGV ecosystem
public class AuthenticationManager: ObservableObject {
    
    // MARK: - Properties
    private let session: Session
    private let keychain = KeychainManager()
    
    @Published public var isAuthenticated = false
    @Published public var currentToken: AuthToken?
    
    public weak var delegate: AuthenticationManagerDelegate?
    
    private let tokenRefreshThreshold: TimeInterval = 300 // 5 minutes
    private var refreshTimer: Timer?
    
    // MARK: - Initialization
    public init(session: Session) {
        self.session = session
        loadStoredToken()
    }
    
    public func initialize() async {
        await validateStoredToken()
        startTokenRefreshTimer()
    }
    
    // MARK: - Authentication Methods
    
    /// Authenticate with wallet signature
    public func authenticate(walletAddress: String, signature: String) async throws -> AuthToken {
        let parameters: [String: Any] = [
            "wallet_address": walletAddress,
            "signature": signature,
            "timestamp": Date().timeIntervalSince1970
        ]
        
        let response = try await session.request(
            "https://api.blgvbtc.com/auth/wallet-login",
            method: .post,
            parameters: parameters,
            encoding: JSONEncoding.default
        ).serializingDecodable(AuthResponse.self).value
        
        let token = response.token
        await storeToken(token)
        
        DispatchQueue.main.async {
            self.currentToken = token
            self.isAuthenticated = true
            self.delegate?.authenticationDidSucceed(token: token)
        }
        
        return token
    }
    
    /// Authenticate with username/password (fallback)
    public func authenticate(username: String, password: String) async throws -> AuthToken {
        let parameters: [String: Any] = [
            "username": username,
            "password": password
        ]
        
        let response = try await session.request(
            "https://api.blgvbtc.com/auth/login",
            method: .post,
            parameters: parameters,
            encoding: JSONEncoding.default
        ).serializingDecodable(AuthResponse.self).value
        
        let token = response.token
        await storeToken(token)
        
        DispatchQueue.main.async {
            self.currentToken = token
            self.isAuthenticated = true
            self.delegate?.authenticationDidSucceed(token: token)
        }
        
        return token
    }
    
    /// Refresh authentication token
    public func refreshToken() async throws -> AuthToken {
        guard let currentToken = currentToken else {
            throw AuthenticationError.noTokenAvailable
        }
        
        let parameters: [String: Any] = [
            "refresh_token": currentToken.refreshToken
        ]
        
        let response = try await session.request(
            "https://api.blgvbtc.com/auth/refresh",
            method: .post,
            parameters: parameters,
            encoding: JSONEncoding.default
        ).serializingDecodable(AuthResponse.self).value
        
        let newToken = response.token
        await storeToken(newToken)
        
        DispatchQueue.main.async {
            self.currentToken = newToken
        }
        
        return newToken
    }
    
    /// Logout user and clear authentication
    public func logout() async throws {
        if let token = currentToken {
            // Notify server of logout
            try? await session.request(
                "https://api.blgvbtc.com/auth/logout",
                method: .post,
                headers: ["Authorization": "Bearer \(token.accessToken)"]
            ).serializingDecodable(SuccessResponse.self).value
        }
        
        await clearAuthentication()
    }
    
    /// Generate wallet signature for authentication
    public func generateWalletSignature(privateKey: String, message: String) throws -> String {
        // Implementation would depend on the specific cryptographic library used
        // This is a simplified example
        let messageData = message.data(using: .utf8)!
        let signature = try HMAC(key: privateKey.bytes, variant: .sha256).authenticate(messageData.bytes)
        return signature.toHexString()
    }
    
    /// Validate wallet signature
    public func validateWalletSignature(publicKey: String, signature: String, message: String) -> Bool {
        // Implementation would validate the signature against the public key
        // This is a simplified example
        return signature.count == 64 && publicKey.count >= 40
    }
    
    // MARK: - Token Management
    
    /// Check if current token needs refresh
    public func shouldRefreshToken() -> Bool {
        guard let token = currentToken else { return false }
        
        let timeUntilExpiry = token.expiresAt.timeIntervalSinceNow
        return timeUntilExpiry < tokenRefreshThreshold
    }
    
    /// Automatically refresh token if needed
    public func autoRefreshTokenIfNeeded() async {
        guard shouldRefreshToken() else { return }
        
        do {
            _ = try await refreshToken()
        } catch {
            await handleTokenExpiration()
        }
    }
    
    // MARK: - Biometric Authentication
    
    /// Enable biometric authentication
    public func enableBiometricAuth() async throws {
        guard BiometricManager.isAvailable else {
            throw AuthenticationError.biometricNotAvailable
        }
        
        let success = await BiometricManager.authenticate(reason: "Enable biometric authentication for BLGV")
        
        if success {
            UserDefaults.standard.set(true, forKey: "biometric_auth_enabled")
        } else {
            throw AuthenticationError.biometricAuthenticationFailed
        }
    }
    
    /// Authenticate with biometrics
    public func authenticateWithBiometrics() async throws -> Bool {
        guard BiometricManager.isAvailable,
              UserDefaults.standard.bool(forKey: "biometric_auth_enabled") else {
            throw AuthenticationError.biometricNotAvailable
        }
        
        return await BiometricManager.authenticate(reason: "Authenticate to access BLGV")
    }
    
    // MARK: - Multi-Factor Authentication
    
    /// Setup 2FA
    public func setup2FA() async throws -> TwoFactorSetup {
        guard let token = currentToken else {
            throw AuthenticationError.notAuthenticated
        }
        
        return try await session.request(
            "https://api.blgvbtc.com/auth/2fa/setup",
            method: .post,
            headers: ["Authorization": "Bearer \(token.accessToken)"]
        ).serializingDecodable(TwoFactorSetup.self).value
    }
    
    /// Verify 2FA code
    public func verify2FA(code: String) async throws -> Bool {
        guard let token = currentToken else {
            throw AuthenticationError.notAuthenticated
        }
        
        let parameters = ["code": code]
        
        let response = try await session.request(
            "https://api.blgvbtc.com/auth/2fa/verify",
            method: .post,
            parameters: parameters,
            encoding: JSONEncoding.default,
            headers: ["Authorization": "Bearer \(token.accessToken)"]
        ).serializingDecodable(VerificationResponse.self).value
        
        return response.verified
    }
    
    // MARK: - Private Methods
    
    private func loadStoredToken() {
        if let tokenData = keychain.getData(for: "auth_token"),
           let token = try? JSONDecoder().decode(AuthToken.self, from: tokenData) {
            currentToken = token
            isAuthenticated = !token.isExpired
        }
    }
    
    private func validateStoredToken() async {
        guard let token = currentToken, !token.isExpired else {
            await clearAuthentication()
            return
        }
        
        // Validate token with server
        do {
            let response = try await session.request(
                "https://api.blgvbtc.com/auth/validate",
                headers: ["Authorization": "Bearer \(token.accessToken)"]
            ).serializingDecodable(TokenValidationResponse.self).value
            
            if !response.valid {
                await clearAuthentication()
            }
        } catch {
            // If validation fails, try to refresh
            do {
                _ = try await refreshToken()
            } catch {
                await clearAuthentication()
            }
        }
    }
    
    private func storeToken(_ token: AuthToken) async {
        guard let tokenData = try? JSONEncoder().encode(token) else { return }
        keychain.store(data: tokenData, for: "auth_token")
    }
    
    private func clearAuthentication() async {
        keychain.delete(for: "auth_token")
        
        DispatchQueue.main.async {
            self.currentToken = nil
            self.isAuthenticated = false
        }
        
        stopTokenRefreshTimer()
    }
    
    private func handleTokenExpiration() async {
        await clearAuthentication()
        
        DispatchQueue.main.async {
            self.delegate?.authenticationDidExpire()
        }
    }
    
    private func startTokenRefreshTimer() {
        stopTokenRefreshTimer()
        
        refreshTimer = Timer.scheduledTimer(withTimeInterval: 60, repeats: true) { [weak self] _ in
            Task {
                await self?.autoRefreshTokenIfNeeded()
            }
        }
    }
    
    private func stopTokenRefreshTimer() {
        refreshTimer?.invalidate()
        refreshTimer = nil
    }
}

// MARK: - Supporting Models

public struct AuthResponse: Codable {
    public let token: AuthToken
    public let user: AuthenticatedUser
}

public struct AuthenticatedUser: Codable {
    public let id: String
    public let walletAddress: String?
    public let username: String?
    public let email: String?
    public let permissions: [String]
    public let isVerified: Bool
    public let has2FA: Bool
}

public struct TwoFactorSetup: Codable {
    public let secret: String
    public let qrCode: String
    public let backupCodes: [String]
}

public struct VerificationResponse: Codable {
    public let verified: Bool
    public let message: String?
}

public struct TokenValidationResponse: Codable {
    public let valid: Bool
    public let expiresIn: TimeInterval?
}

// MARK: - Authentication Errors

public enum AuthenticationError: Error, LocalizedError {
    case invalidCredentials
    case noTokenAvailable
    case tokenExpired
    case networkError
    case biometricNotAvailable
    case biometricAuthenticationFailed
    case notAuthenticated
    case twoFactorRequired
    case invalidTwoFactorCode
    
    public var errorDescription: String? {
        switch self {
        case .invalidCredentials:
            return "Invalid credentials provided"
        case .noTokenAvailable:
            return "No authentication token available"
        case .tokenExpired:
            return "Authentication token has expired"
        case .networkError:
            return "Network error occurred during authentication"
        case .biometricNotAvailable:
            return "Biometric authentication is not available"
        case .biometricAuthenticationFailed:
            return "Biometric authentication failed"
        case .notAuthenticated:
            return "User is not authenticated"
        case .twoFactorRequired:
            return "Two-factor authentication is required"
        case .invalidTwoFactorCode:
            return "Invalid two-factor authentication code"
        }
    }
}

// MARK: - AuthToken Extension

extension AuthToken {
    public var isExpired: Bool {
        return expiresAt <= Date()
    }
    
    public var isExpiringSoon: Bool {
        return expiresAt.timeIntervalSinceNow < 300 // 5 minutes
    }
}

// MARK: - Keychain Manager

private class KeychainManager {
    private let service = "com.blgv.ecosystem.sdk"
    
    func store(data: Data, for key: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: key,
            kSecValueData as String: data
        ]
        
        SecItemDelete(query as CFDictionary)
        SecItemAdd(query as CFDictionary, nil)
    }
    
    func getData(for key: String) -> Data? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]
        
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        
        guard status == errSecSuccess else { return nil }
        return result as? Data
    }
    
    func delete(for key: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: key
        ]
        
        SecItemDelete(query as CFDictionary)
    }
}

// MARK: - Biometric Manager

private class BiometricManager {
    static var isAvailable: Bool {
        // Implementation would check for Face ID/Touch ID availability
        return true // Simplified for example
    }
    
    static func authenticate(reason: String) async -> Bool {
        // Implementation would use LocalAuthentication framework
        return true // Simplified for example
    }
}