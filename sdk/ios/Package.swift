// swift-tools-version: 5.7
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "BLGVEcosystemSDK",
    platforms: [
        .iOS(.v15),
        .macOS(.v12),
        .watchOS(.v8),
        .tvOS(.v15)
    ],
    products: [
        .library(
            name: "BLGVEcosystemSDK",
            targets: ["BLGVEcosystemSDK"]
        ),
    ],
    dependencies: [
        .package(url: "https://github.com/Alamofire/Alamofire.git", from: "5.6.0"),
        .package(url: "https://github.com/daltoniam/Starscream.git", from: "4.0.0"),
        .package(url: "https://github.com/krzyzanowskim/CryptoSwift.git", from: "1.6.0"),
        .package(url: "https://github.com/apple/swift-crypto.git", from: "2.0.0"),
    ],
    targets: [
        .target(
            name: "BLGVEcosystemSDK",
            dependencies: [
                "Alamofire",
                "Starscream", 
                "CryptoSwift",
                .product(name: "Crypto", package: "swift-crypto")
            ],
            path: "Sources"
        ),
        .testTarget(
            name: "BLGVEcosystemSDKTests",
            dependencies: ["BLGVEcosystemSDK"],
            path: "Tests"
        ),
    ]
)