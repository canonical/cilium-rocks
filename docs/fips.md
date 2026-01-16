# Cilium FIPS Compliance

For comprehensive information about FIPS 140-3 compliance in Canonical Kubernetes, including how ROCKs are built with FIPS support, please refer to the [k8s-snap FIPS documentation](https://github.com/canonical/k8s-snap/blob/main/docs/dev/fips.md).

> **Note:** As of now, pebble is not built in a FIPS-compliant way. This document will be updated once it is.

## Cilium-Specific Information

### WireGuard and FIPS Compliance

WireGuard is not FIPS-compliant due to its usage of non-certified cryptography algorithms 
such as `ChaCha20Poly1305`. Usage of this feature would result in a non-FIPS-compliant
setup of Cilium.

For Canonical Kubernetes, there is no supported path to enable the WireGuard feature. 
Therefore, deployments using the default Cilium configurations are FIPS-compliant.

### Using zig to link against specific glibc versions

The Cilium helm chart, which is used to deploy Cilium on a Kubernetes cluster 
and utilizes this image, has a few init containers that copy binaries from 
inside the image to the host and run them with the host namespace. Since we 
are dynamically building these binaries, to make sure they are working on the 
oldest supported host, we are linking against glibc shipped with the oldest
supported host for each image. The [Zig compiler] allows us to achieve 
that without changing the image base.

## Cryptographic Usage Details

### Cilium Agent Component

The Cilium agent is the core component running on each cluster node,
responsible for enforcing network policies, managing encryption, and handling
network connectivity. Its cryptographic usage includes:

- **Transparent Encryption**: [IPsec] encryption for pod-to-pod communication
- **TLS Communication**: Secure communication with the Kubernetes API server using Go's crypto packages
- **Certificate Management**: Handling TLS certificates for L7 proxy functionality
- **Key Management**: IPsec key rotation and distribution via Kubernetes secrets

### Cilium Operator Component

The operator component manages cluster-wide operations and coordination. Its
cryptographic involvement includes:

- **TLS for Kubernetes API**: Certificate validation and secure API communication
- **Secret Synchronization**: Managing and distributing cryptographic secrets across the cluster
- **Certificate Lifecycle**: Managing certificates for various Cilium features

### Envoy Proxy Integration

Cilium utilizes Envoy proxy for L7 policy enforcement and [TLS inspection]
capabilities:

- **TLS Termination**: Terminating TLS connections for inspection and policy enforcement
- **Certificate Handling**: Managing certificates via Secret Discovery Service (SDS) or Network Policy Discovery Service (NPDS)
- **Cryptographic Processing**: TLS handshakes and certificate validation

<!-- LINKS -->

[Zig compiler]: https://snapcraft.io/zig
[IPsec]: https://docs.cilium.io/en/latest/security/network/encryption-ipsec/
[TLS inspection]: https://docs.cilium.io/en/latest/security/tls-visibility/
