package main

import (
	"embed"
	_ "embed"
	"fmt"
	"os"
	"os/exec"
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

	// Prepare command with custom environment variables
	cmd := exec.Command(f.Name(), os.Args[1:]...)
	cmd.Env = append(os.Environ(),
		fmt.Sprintf("LD_LIBRARY_PATH=%s", ldLibraryPath),
		fmt.Sprintf("OPENSSL_MODULES=%s", opensslmodulesPath),
	)

	// Connect stdin/stdout/stderr to this process
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	// Run the binary
	if err := cmd.Run(); err != nil {
		fmt.Fprintf(os.Stderr, "%v\n", err)
		if exitErr, ok := err.(*exec.ExitError); ok {
			return exitErr.ProcessState.ExitCode()
		} else {
			return 1
		}
	}

	return 0
}

func main() {
	os.Exit(run())
}
