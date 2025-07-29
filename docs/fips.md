# Cilium FIPS Compliance Analysis

The following document summarizes the current state of [FIPS 140-3] compliance
for Cilium CNI, focusing on its cryptographic components and build
requirements. This overview is intended to guide users and developers in
understanding the compliance status and necessary steps for achieving FIPS mode
operation.

## Glossary

This document uses a set of abbreviations and technical concepts which are
explained below:

- **Federal Information Processing Standards (FIPS)**: A set of standards for
cryptographic modules published by the U.S. government.
- **Container Network Interface (CNI)**: A networking framework for Linux
containers and orchestration platforms like Kubernetes.
- **Transport Layer Security (TLS)**: A cryptographic protocol designed to
provide secure communication over a computer network.
- **Internet Protocol Security (IPsec)**: A secure network protocol suite that
authenticates and encrypts packets of data to provide secure encrypted
communication.
- **WireGuard**: A modern VPN protocol that uses state of the art cryptography
for secure tunneling.
- **Extended Berkeley Packet Filter (eBPF)**: A kernel technology that allows
programs to run in kernel space without changing kernel source code.
- **Envoy Proxy**: An L7 proxy and communication bus designed for large modern
service oriented architectures.

## Cryptographic Implementation Analysis

Cilium's cryptographic footprint encompasses multiple areas including
transparent encryption, TLS inspection, certificate management, and secure
communication with the Kubernetes API. The primary cryptographic usage involves
IPsec/WireGuard encryption, TLS termination and inspection, and API
authentication. FIPS compliance depends on the cryptographic libraries, Go
runtime, and build environment used for these components.

> **_NOTE:_** As of 2025-07-29, WireGuard has limited FIPS support due to ChaCha20Poly1305
> algorithm.

### Cilium Agent Component

The Cilium agent is the core component running on each cluster node,
responsible for enforcing network policies, managing encryption, and handling
network connectivity. Its cryptographic usage includes:

- **Transparent Encryption**: [IPsec] or [WireGuard] encryption for pod-to-pod
communication.
- **TLS Communication**: Secure communication with the Kubernetes API server
using Go's crypto packages.
- **Certificate Management**: Handling TLS certificates for L7 proxy
functionality.
- **Key Management**: IPsec key rotation and distribution via Kubernetes
secrets.

### Cilium Operator Component

The operator component manages cluster-wide operations and coordination. Its
cryptographic involvement includes:

- **TLS for Kubernetes API**: Certificate validation and secure API
communication.
- **Secret Synchronization**: Managing and distributing cryptographic secrets
across the cluster.
- **Certificate Lifecycle**: Managing certificates for various Cilium features.

### Envoy Proxy Integration

Cilium utilizes Envoy proxy for L7 policy enforcement and [TLS inspection]
capabilities:

- **TLS Termination**: Terminating TLS connections for inspection and policy
enforcement
- **Certificate Handling**: Managing certificates via Secret Discovery Service
(SDS) or Network Policy Discovery Service (NPDS)
- **Cryptographic Processing**: TLS handshakes and certificate validation

## FIPS Compliance Status

### Implementation Dependencies

Cilium's FIPS compliance depends on several key components:

1. **Go Runtime**: Cilium is written in Go and relies on Go's cryptographic
packages. A modified [Go toolchain from Microsoft] must be used.
2. **OpenSSL**: Cilium must link against a FIPS-validated OpenSSL
implementation. Currently, there is no FIPS base for Rocks, so it must be
sourced, for example, from `core22/fips`.
3. **Build Environment**: The build process must be performed on a Ubuntu Pro
machine (details provided below).

### Required Build Modifications

To build Cilium in FIPS-compliant mode, the following requirements must be met:

1. **Prerequisites**:
   - Ubuntu Pro enabled machine
   - FIPS **must NOT** enabled
   - Rockcraft installed from the `edge/pro-sources` channel (refer to this
   Discourse [post][discourse post])

2. **Building the Image**:
  Use the following command to build the image:
   ```bash
   sudo rockcraft pack --pro=fips-updates
   ```

<!-- LINKS -->

[discourse post]: https://discourse.ubuntu.com/t/build-rocks-with-ubuntu-pro-services/57578
[FIPS 140-3]: https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.140-3.pdf
[Go toolchain from Microsoft]: https://github.com/microsoft/go/blob/microsoft/release-branch.go1.23/eng/doc/fips/README.md
[IPsec]: https://docs.cilium.io/en/latest/security/network/encryption-ipsec/
[WireGuard]: https://docs.cilium.io/en/latest/security/network/encryption-wireguard/
[TLS inspection]: https://docs.cilium.io/en/latest/security/tls-visibility/
