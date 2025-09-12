## Wrapper binary with LD_LIBRARY_PATH set

This software provides a wrapper around an arbitrary binary, ensuring it always runs with a fixed
LD_LIBRARY_PATH environment variable set at runtime. Both the target binary and the value of
LD_LIBRARY_PATH must be provided at build time:

```
go build -o wrapper-bin -ldflags "-X main.binaryName=<BINARY_NAME> -X main.ldLibraryPath=<LD_LIBRARY_PATH>" main.go
```

This is needed for the Cilium rock image since the Cilium binaries are built with
dynamic linking and may sometimes run outside the namespaces of their container.
While setting RPATH works for direct dependencies, indirect dependencies are not resolved correctly.
This wrapper ensures all dynamic links resolve to the correct libraries. 


