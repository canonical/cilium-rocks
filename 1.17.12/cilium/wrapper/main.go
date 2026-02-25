package main

import (
	"embed"
	"fmt"
	"os"
	"syscall"
)

//go:embed bin/*
var embeddedFiles embed.FS

var binaryName string
var ldLibraryPath string
var opensslmodulesPath string

func run() (exitCode int) {

	binaryData, err := embeddedFiles.ReadFile("bin/" + binaryName)
	if err != nil {
		fmt.Fprintf(os.Stderr, "failed to read embedded binary %q: %v\n", binaryName, err)
		return 1
	}

	f, err := os.CreateTemp("", binaryName)
	if err != nil {
		fmt.Fprintf(os.Stderr, "failed to create temp file: %v\n", err)
		return 1
	}
	defer func() {
		if err := os.Remove(f.Name()); err != nil {
			fmt.Fprintf(os.Stderr, "failed to remove the embedded binary: %v\n", err)
		}
	}()

	if _, err := f.Write(binaryData); err != nil {
		fmt.Fprintf(os.Stderr, "failed to write embedded binary: %v\n", err)
		return 1
	}

	if err := f.Close(); err != nil {
		fmt.Fprintf(os.Stderr, "failed to close the temp file: %v\n", err)
		return 1
	}

	if err := os.Chmod(f.Name(), 0700); err != nil {
		fmt.Fprintf(os.Stderr, "failed to make the embedded binary executable: %v\n", err)
		return 1
	}

	// Set environment variables for the target binary
	os.Setenv("LD_LIBRARY_PATH", ldLibraryPath)
	os.Setenv("OPENSSL_MODULES", opensslmodulesPath)

	// Replace current process with the target binary (execve)
	if err := syscall.Exec(f.Name(), append([]string{f.Name()}, os.Args[1:]...), os.Environ()); err != nil {
		fmt.Fprintf(os.Stderr, "failed to exec %s: %v\n", binaryName, err)
		return 1
	}

	// unreachable if exec succeeds
	return 0
}

func main() {
	os.Exit(run())
}
