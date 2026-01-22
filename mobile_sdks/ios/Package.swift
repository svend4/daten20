// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "DMSSDK",
    platforms: [
        .iOS(.v14),
        .macOS(.v12)
    ],
    products: [
        .library(
            name: "DMSSDK",
            targets: ["DMSSDK"]),
    ],
    dependencies: [
        // Add package dependencies here
    ],
    targets: [
        .target(
            name: "DMSSDK",
            dependencies: []),
        .testTarget(
            name: "DMSSDKTests",
            dependencies: ["DMSSDK"]),
    ]
)
