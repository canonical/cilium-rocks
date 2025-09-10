package main

import (
	_ "embed"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
)

//go:embed cilium-sysctlfix
var embeddedBinary []byte

func main() {

	tmpDir := os.TempDir()
	binPath := filepath.Join(tmpDir, "wrapped-binary")

	err := os.WriteFile(binPath, embeddedBinary, 0755)
	if err != nil {
		fmt.Fprintf(os.Stderr, "failed to write embedded binary: %v\n", err)
		os.Exit(1)
	}

	// Prepare command with custom environment variables
	cmd := exec.Command(binPath, os.Args[1:]...)
	cmd.Env = append(os.Environ(),
		"LD_LIBRARY_PATH=/snap/core22/current/usr/lib/x86_64-linux-gnu",
	)

	// Connect stdin/stdout/stderr to this process
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	// Run the binary
	if err := cmd.Run(); err != nil {
		fmt.Fprintf(os.Stderr, "%w", err)
		os.Exit(1)
	}
}
