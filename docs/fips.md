# Cilium FIPS Compliance Analysis

The following document summarizes the current state of [FIPS 140-3] compliance
for Cilium CNI, focusing on its cryptographic components and build
requirements. This overview is intended to guide users and developers in
understanding the compliance status and necessary steps for achieving FIPS mode
operation.

> **Note:** As of now, pebble is not built in a FIPS-compliant way. This document will be updated once it is.

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

Wireguard is not fips compliant due to its usage of non-certified cryptography algorithms 
such as `ChaCha20Poly1305`. Usage of this feature would result in a non-fips compliant 
setup of Cilium.

For Canonical Kubernetes, this mode is not enabled by default and there is no 
provided/supported UX for turning this on. Based on this our current setup of Cilium 
remains fips compliant.

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

### Cilium Wrapper Binary

The Cilium helm chart, which is used to deploy Cilium on a Kubernetes cluster 
and utilizes this image, has a few init containers that copy binaries from 
inside the image to the host and run them with the host namespace. Since we 
are building these binaries with dynamic linking, to make sure the dependencies 
are always present on the machines, we have linked the binaries against 
libraries from the `core22` snap package using `RPATH` in build time and 
`LD_LIBRARY_PATH` at runtime. We also have modified the binaries to use 
the dynamic linker from `core22` for compatibility. 

However, since the OpenSSL shipped with the `core22` snap package is using the 
modules like the FIPS module from the host, this modification doesn't work out 
of the box. To make sure we are using the right FIPS module when calling the 
OpenSSL library, we also provide the FIPS module path shipped with `core22` 
using the `OPENSSL_MODULES` environment variable at runtime. 

To provide the runtime environment variables, binaries are embedded inside a 
wrapper binary that provides these values when the binary is executed.

## FIPS Compliance Status

### Implementation Dependencies

Cilium's FIPS compliance depends on several key components:

1. **Go Runtime**: Cilium is written in Go and relies on Go's cryptographic
packages. A modified [Go toolchain from Microsoft] must be used.
2. **OpenSSL**: Cilium must link against a FIPS-validated OpenSSL
implementation.

**NOTE**: This ROCK is bundled with a FIPS-validated OpenSSL library which is described in the 
ROCK manifest (refer to this Discourse [post][discourse post]).
```yaml
...
parts:
  openssl:
    plugin: nil
    stage-packages:
      - openssl-fips-module-3
      - openssl
...
```

### Required Build Modifications

To build Cilium in FIPS-compliant mode, the following requirements must be met:

1. **Prerequisites**:
   - a `rockcraft` version that contains the pro feature. (refer to this
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
