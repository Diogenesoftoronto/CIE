package cli

import (
	"os"

	"github.com/spf13/cobra"

	"github.com/cie-team/cie/internal/config"
)

// LoadConfig resolves --config then ~/.cie/config.json, else defaults.
func LoadConfig(cmd *cobra.Command) (*config.Config, error) {
	path, err := cmd.Flags().GetString("config")
	if err != nil {
		return nil, err
	}
	if path != "" {
		return config.Load(path)
	}
	def, err := config.DefaultConfigPath()
	if err != nil || def == "" {
		c := config.Default()
		c.ExpandPaths()
		return c, nil
	}
	if _, err := os.Stat(def); os.IsNotExist(err) {
		c := config.Default()
		c.ExpandPaths()
		return c, nil
	}
	return config.Load(def)
}
