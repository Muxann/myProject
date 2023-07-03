package config

import (
	"fmt"
	"github.com/BurntSushi/toml"
	"github.com/labstack/gommon/log"
)

type Config struct {
	ServicePort string `toml:"service_port"`
	Db          dbConf `toml:"database"`
	Log         logSection
}

func (c *Config) load(confPath string) error {
	if _, err := toml.DecodeFile(confPath, c); err != nil {
		return fmt.Errorf("Config parse: %v\n", err)
	}
	return nil
}

func (c *Config) GetLogLever() log.Lvl {
	return c.Log.GetLevel()
}

type dbConf struct {
	Host     string
	Port     int
	Database string
	User     string
	Password string
}

func (dc *dbConf) GetConnectString() string {
	return fmt.Sprintf("dbname=%s host=%s port=%d user=%s password=%s sslmode=disable",
		dc.Database, dc.Host, dc.Port, dc.User, dc.Password)
}

type logSection struct {
	Level string
}

func (l *logSection) GetLevel() log.Lvl {
	var lvl log.Lvl

	switch l.Level {
	case "DEBUG":
		lvl = log.DEBUG
		break
	case "INFO":
		lvl = log.INFO
		break
	case "WARN":
		lvl = log.WARN
		break
	case "ERROR":
		lvl = log.ERROR
		break
	default:
		lvl = log.INFO
	}
	return lvl
}
