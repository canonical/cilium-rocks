package main

import (
	"embed"
	_ "embed"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
)

//go:embed bin/*
var embeddedFiles embed.FS

var binaryName string
var ldLibraryPath string

func main() {

	binaryData, err := embeddedFiles.ReadFile("bin/" + binaryName)
	if err != nil {
		fmt.Fprintf(os.Stderr, "failed to read embedded binary %q: %v\n", binaryName, err)
		os.Exit(1)
	}

	tmpDir := os.TempDir()
	binPath := filepath.Join(tmpDir, binaryName)

	err = os.WriteFile(binPath, binaryData, 0755)
	if err != nil {
		fmt.Fprintf(os.Stderr, "failed to write embedded binary: %v\n", err)
		os.Exit(1)
	}

	// Prepare command with custom environment variables
	cmd := exec.Command(binPath, os.Args[1:]...)
	cmd.Env = append(os.Environ(),
		fmt.Sprintf("LD_LIBRARY_PATH=%s", ldLibraryPath),
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
