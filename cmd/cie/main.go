package main

import (
	"github.com/cie-team/cie/internal/cli"
)

func main() {
	if err := cli.NewRoot().Execute(); err != nil {
		cli.Exit(1, err.Error())
	}
}
