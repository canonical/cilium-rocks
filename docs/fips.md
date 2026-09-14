# Cilium FIPS Compliance

For comprehensive information about FIPS 140-3 compliance in Canonical Kubernetes, including how ROCKs are built with FIPS support, please refer to the [k8s-snap FIPS documentation](https://github.com/canonical/k8s-snap/blob/main/docs/dev/fips.md).

> **Note:** As of now, pebble is not built in a FIPS-compliant way. This document will be updated once it is.

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

## WireGuard and FIPS Compliance

WireGuard is not FIPS-compliant due to its usage of non-certified cryptography algorithms
such as `ChaCha20Poly1305`. Usage of this feature would result in a non-FIPS-compliant
setup of Cilium.

For Canonical Kubernetes, there is no supported path to enable the WireGuard feature.
Therefore, deployments using the default Cilium configurations are FIPS-compliant.

## Cilium Wrapper Binary

The Cilium Helm chart, which is used to deploy Cilium on a Kubernetes cluster
and utilizes this Rock, has a few init containers that copy binaries from
inside the image to the host and run them within the host namespace. Since we
are building these binaries with dynamic linking, to make sure the dependencies
are always present on the machines, we have linked the binaries against
libraries from the `core22` snap package using `RPATH` at build time and
`LD_LIBRARY_PATH` at runtime. We also have modified the binaries to use
the dynamic linker from `core22` for compatibility.

However, since the OpenSSL shipped with the `core22` snap package is using the
modules like the FIPS module from the host, this modification doesn't work out
of the box. To make sure we are using the right FIPS module when calling the
OpenSSL library, we also provide the FIPS module path shipped with `core22`
using the `OPENSSL_MODULES` environment variable at runtime.

To provide the runtime environment variables, binaries are embedded inside a
wrapper binary that provides these values when the binary is executed.

<!-- LINKS -->

[IPsec]: https://docs.cilium.io/en/latest/security/network/encryption-ipsec/
[TLS inspection]: https://docs.cilium.io/en/latest/security/tls-visibility/
