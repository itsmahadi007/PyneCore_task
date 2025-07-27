# PyneCore Plugin System: Comprehensive Development and Implementation Plan

## Executive Summary

This document provides a complete architectural blueprint for implementing a plugin system in PyneCore, a Python framework for Pine Script execution and trading strategy development. The plugin system enables extensible data provider integration while maintaining a clean separation between core functionality and external data sources.

### Key Objectives
- **Embedded CCXT**: Keep CCXT provider as built-in core functionality
- **External Plugins**: Move CapitalCom and future providers to plugin architecture
- **Community Extensibility**: Enable third-party plugin development
- **Unified Interface**: Maintain consistent API across all providers
- **Browser Compatibility**: Support both local and browser-based execution

## Technical Architecture Overview

### Core Components

1. **Plugin Registry System**: Automatic discovery and management of data providers
2. **Base Provider Interface**: Abstract class defining required methods for all providers
3. **Provider Factory**: Creates and configures provider instances
4. **CLI Integration**: Commands for plugin management and discovery
5. **Configuration System**: Unified configuration handling across providers
6. **Entry Point Discovery**: Python setuptools entry points for automatic plugin detection

### Data Flow Architecture

```
Data Source → Provider Plugin → Iterator/Generator → PyneCore Script Runner → Results
                    ↓
            Configuration System
                    ↓
              Plugin Registry
```

### Provider Types

1. **Built-in Providers**
   - CCXT (embedded in PyneCore core)
   - File-based providers (existing functionality)

2. **External Plugin Providers**
   - CapitalCom (reference implementation)
   - Custom community providers
   - Third-party data sources

## Plugin Creation Flow

### 1. Plugin Developer Workflow

**Step 1: Initialize Plugin Project**
- Developer runs: `pyne plugins create my-custom-provider`
- PyneCore generates plugin template with proper structure
- Template includes setup.py, base provider class, configuration files
- Generated structure follows Python packaging best practices

**Step 2: Implement Provider Interface**
- Developer implements required methods from `DataProvider` abstract base class:
  - `get_name()` - returns unique provider identifier (string)
  - `get_supported_symbols()` - lists available trading pairs/instruments
  - `get_historical_data()` - returns OHLCV iterator for backtesting
  - `get_live_stream()` - returns real-time data stream for live trading
  - `configure()` - handles API keys, credentials, and provider settings
  - `validate_config()` - validates configuration before provider initialization

**Technical Requirements for Provider Implementation:**
- **Data Format**: All providers must return OHLCV tuples: (timestamp, open, high, low, close, volume)
- **Iterator Pattern**: Historical data must implement Python iterator protocol
- **Error Handling**: Robust exception handling for network failures, API limits, authentication errors
- **Rate Limiting**: Respect API rate limits and implement backoff strategies
- **Reconnection Logic**: Automatic reconnection for websocket connections
- **Data Validation**: Ensure data integrity and handle missing/invalid data points

**Step 3: Add Provider-Specific Logic**
- Implement API calls to data source
- Handle authentication (API keys, tokens)
- Convert data to PyneCore OHLCV format
- Implement error handling and reconnection logic
- Add websocket support for live data

**Step 4: Test Plugin Locally**
- Developer tests plugin in development environment
- Validates data format compatibility
- Tests both historical and live data feeds
- Ensures proper error handling

**Step 5: Package and Publish**
- Developer builds plugin package
- Publishes to PyPI as `pynecore-{provider-name}-plugin`
- Includes proper entry points for auto-discovery
- Documents configuration requirements

### 2. Plugin Distribution

**PyPI Publication**
- Plugin published with naming convention: `pynecore-{provider}-plugin`
- Entry points configured for automatic discovery
- Dependencies specified (PyneCore version, external APIs)

**Community Registry (Optional)**
- Plugin listed in PyneCore community registry
- Documentation and examples provided
- User ratings and reviews

## Plugin Usage Flow

### 3. End User Workflow

**Step 1: Discover Available Plugins**
- User runs: `pyne plugins list`
- Shows built-in providers (CCXT) and installed plugins
- User can search community registry for more plugins

**Step 2: Install Plugin**
- User runs: `pyne plugins install my-custom-provider`
- PyneCore automatically installs via pip
- Plugin becomes available immediately
- Alternative: `pip install pynecore-my-custom-provider-plugin`

**Step 3: Configure Provider**
- User adds configuration to `workdir/config/providers.toml`:
  ```
  [my_custom_provider]
  api_key = "user_api_key"
  api_secret = "user_secret"
  base_url = "https://api.provider.com"
  ```

**Step 4: Verify Plugin Installation**
- User runs: `pyne plugins info my-custom-provider`
- Shows provider details, supported symbols, configuration status
- Validates API connection and credentials

**Step 5: Download Data (Backtesting)**
- User runs: `pyne data download my-custom-provider --symbol "PROVIDER:BTC/USD" --timeframe 1D --from 30`
- Plugin downloads historical data
- Data saved in PyneCore OHLCV format
- Ready for backtesting

**Step 6: Run Backtest**
- User runs: `pyne run script.py data_file.ohlcv`
- PyneCore uses downloaded data for backtesting
- Same as existing workflow, provider-agnostic

**Step 7: Live Trading Setup**
- User configures live trading in script settings
- Specifies provider and symbol for live data
- PyneCore automatically uses plugin's live stream

**Step 8: Execute Live Trading**
- User runs: `pyne live script.py --provider my-custom-provider --symbol "BTC/USD"`
- Plugin establishes live data connection
- Real-time data feeds into PyneCore script
- Trading signals generated in real-time

## Plugin Lifecycle Management

### 4. Plugin Updates and Maintenance

**Plugin Updates**
- User runs: `pyne plugins update my-custom-provider`
- Or: `pip install --upgrade pynecore-my-custom-provider-plugin`
- Backward compatibility maintained through versioning

**Plugin Removal**
- User runs: `pyne plugins uninstall my-custom-provider`
- Plugin removed but configuration preserved
- Data files remain available

**Configuration Management**
- User can backup/restore provider configurations
- Multiple environment support (dev, prod)
- Encrypted credential storage options

## Integration Points

### 5. PyneCore Integration

**Automatic Discovery**
- PyneCore scans for plugins on startup
- Uses Python entry points for discovery
- Plugins registered in internal registry

**Unified Interface**
- All providers (built-in and plugins) use same interface
- Scripts work with any provider without modification
- Configuration handled uniformly

**Error Handling**
- Plugin failures don't crash PyneCore
- Graceful degradation when plugins unavailable
- Clear error messages for configuration issues

**Performance**
- Plugins loaded on-demand
- Minimal impact on PyneCore startup time
- Efficient data streaming for live trading

This flow ensures that plugin development is straightforward for developers while providing a seamless experience for end users, maintaining the same simplicity as the current PyneCore workflow.

## Detailed Technical Specifications

### Base Provider Interface (Abstract Class)

```python
from abc import ABC, abstractmethod
from typing import Iterator, Dict, Any, Optional, List
from datetime import datetime

class DataProvider(ABC):
    """Abstract base class for all PyneCore data providers"""
    
    @abstractmethod
    def get_name(self) -> str:
        """Return unique provider identifier"""
        pass
    
    @abstractmethod
    def get_supported_symbols(self) -> List[str]:
        """Return list of supported trading symbols"""
        pass
    
    @abstractmethod
    def get_historical_data(self, symbol: str, timeframe: str, 
                          start: datetime, end: datetime) -> Iterator[tuple]:
        """Return OHLCV iterator for backtesting
        
        Returns:
            Iterator yielding tuples: (timestamp, open, high, low, close, volume)
        """
        pass
    
    @abstractmethod
    def get_live_stream(self, symbol: str, timeframe: str) -> Iterator[tuple]:
        """Return real-time OHLCV stream for live trading"""
        pass
    
    @abstractmethod
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure provider with credentials and settings"""
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate provider configuration"""
        pass
```

### Plugin Package Structure Template

```
pynecore-{provider-name}-plugin/
├── setup.py                    # Package configuration with entry points
├── pyproject.toml             # Modern Python packaging configuration
├── README.md                  # Plugin documentation
├── LICENSE                    # Plugin license
├── requirements.txt           # Plugin dependencies
├── pynecore_{provider}/       # Main plugin package
│   ├── __init__.py           # Package initialization
│   ├── provider.py           # Main provider implementation
│   ├── config.py             # Configuration handling
│   ├── utils.py              # Utility functions
│   ├── exceptions.py         # Custom exceptions
│   └── websocket.py          # WebSocket implementation (if needed)
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── test_provider.py      # Provider tests
│   ├── test_config.py        # Configuration tests
│   └── fixtures/             # Test data
└── docs/                      # Documentation
    ├── installation.md
    ├── configuration.md
    └── examples/
```

### Entry Points Configuration

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="pynecore-{provider-name}-plugin",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pynecore>=6.0.0",
        "requests>=2.25.0",
        "websocket-client>=1.0.0",
    ],
    entry_points={
        'pynecore.providers': [
            '{provider_name} = pynecore_{provider}.provider:{ProviderClass}',
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8+",
    ],
)
```

### Plugin Registry Implementation

```python
# pynecore/core/plugins/registry.py
import importlib
import pkg_resources
from typing import Dict, Type, List
from ..providers.base import DataProvider
import logging

class PluginRegistry:
    """Central registry for all data providers"""
    
    def __init__(self):
        self._providers: Dict[str, Type[DataProvider]] = {}
        self._instances: Dict[str, DataProvider] = {}
        self.logger = logging.getLogger(__name__)
        
        self._load_builtin_providers()
        self._discover_external_plugins()
    
    def _load_builtin_providers(self):
        """Load embedded providers (CCXT)"""
        try:
            from pynecore.providers.ccxt_provider import CCXTProvider
            self.register_provider('ccxt', CCXTProvider)
            self.logger.info("Loaded built-in CCXT provider")
        except ImportError as e:
            self.logger.error(f"Failed to load CCXT provider: {e}")
    
    def _discover_external_plugins(self):
        """Discover and load pip-installed plugins"""
        for entry_point in pkg_resources.iter_entry_points('pynecore.providers'):
            try:
                provider_class = entry_point.load()
                self.register_provider(entry_point.name, provider_class)
                self.logger.info(f"Loaded plugin: {entry_point.name}")
            except Exception as e:
                self.logger.error(f"Failed to load plugin {entry_point.name}: {e}")
    
    def register_provider(self, name: str, provider_class: Type[DataProvider]):
        """Register a data provider class"""
        if not issubclass(provider_class, DataProvider):
            raise ValueError(f"Provider {name} must inherit from DataProvider")
        
        self._providers[name] = provider_class
        self.logger.debug(f"Registered provider: {name}")
    
    def get_provider_class(self, name: str) -> Type[DataProvider]:
        """Get provider class by name"""
        return self._providers.get(name)
    
    def get_provider_instance(self, name: str, config: Dict = None) -> DataProvider:
        """Get configured provider instance"""
        if name not in self._instances:
            provider_class = self.get_provider_class(name)
            if not provider_class:
                raise ValueError(f"Provider '{name}' not found")
            
            instance = provider_class()
            if config:
                instance.configure(config)
            
            self._instances[name] = instance
        
        return self._instances[name]
    
    def list_providers(self) -> List[str]:
        """List all available provider names"""
        return list(self._providers.keys())
    
    def reload_plugins(self):
        """Reload all plugins (useful for development)"""
        self._providers.clear()
        self._instances.clear()
        self._load_builtin_providers()
        self._discover_external_plugins()
```

### Configuration System Integration

```python
# pynecore/core/config/providers.py
import toml
from pathlib import Path
from typing import Dict, Any

class ProviderConfigManager:
    """Manages provider configurations from TOML files"""
    
    def __init__(self, config_path: Path = None):
        self.config_path = config_path or Path("workdir/config/providers.toml")
        self._config = {}
        self.load_config()
    
    def load_config(self):
        """Load provider configurations from TOML file"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self._config = toml.load(f)
    
    def get_provider_config(self, provider_name: str) -> Dict[str, Any]:
        """Get configuration for specific provider"""
        return self._config.get(provider_name, {})
    
    def set_provider_config(self, provider_name: str, config: Dict[str, Any]):
        """Set configuration for specific provider"""
        self._config[provider_name] = config
        self.save_config()
    
    def save_config(self):
        """Save configurations back to TOML file"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            toml.dump(self._config, f)
```

### CLI Commands Implementation

```python
# pynecore/cli/plugins.py
import click
import subprocess
import sys
from ..core.plugins.registry import PluginRegistry
from ..core.config.providers import ProviderConfigManager

@click.group()
def plugins():
    """Plugin management commands"""
    pass

@plugins.command()
def list():
    """List all available data providers"""
    registry = PluginRegistry()
    providers = registry.list_providers()
    
    click.echo("Available Data Providers:")
    click.echo("=" * 40)
    
    for name in providers:
        provider_class = registry.get_provider_class(name)
        try:
            instance = provider_class()
            description = instance.__doc__ or "No description available"
            click.echo(f"  {name}: {description}")
        except Exception as e:
            click.echo(f"  {name}: Error loading - {e}")

@plugins.command()
@click.argument('plugin_name')
def install(plugin_name):
    """Install a plugin via pip"""
    package_name = f"pynecore-{plugin_name}-plugin"
    
    try:
        click.echo(f"Installing {package_name}...")
        subprocess.run([sys.executable, "-m", "pip", "install", package_name], 
                      check=True, capture_output=True, text=True)
        click.echo(f"Successfully installed {plugin_name} plugin")
        
        # Reload registry to detect new plugin
        registry = PluginRegistry()
        registry.reload_plugins()
        
        if plugin_name in registry.list_providers():
            click.echo(f"Plugin {plugin_name} is now available")
        else:
            click.echo(f"Warning: Plugin {plugin_name} installed but not detected")
            
    except subprocess.CalledProcessError as e:
        click.echo(f"Failed to install {plugin_name} plugin: {e.stderr}")
        sys.exit(1)

@plugins.command()
@click.argument('provider_name')
def info(provider_name):
    """Show detailed information about a provider"""
    registry = PluginRegistry()
    config_manager = ProviderConfigManager()
    
    provider_class = registry.get_provider_class(provider_name)
    
    if not provider_class:
        click.echo(f"Provider '{provider_name}' not found")
        return
    
    try:
        config = config_manager.get_provider_config(provider_name)
        provider = registry.get_provider_instance(provider_name, config)
        
        click.echo(f"Provider Information: {provider_name}")
        click.echo("=" * 50)
        click.echo(f"Name: {provider.get_name()}")
        click.echo(f"Class: {provider_class.__name__}")
        click.echo(f"Module: {provider_class.__module__}")
        
        # Test configuration
        if config:
            is_valid = provider.validate_config(config)
            click.echo(f"Configuration: {'Valid' if is_valid else 'Invalid'}")
        else:
            click.echo("Configuration: Not configured")
        
        # Get supported symbols (with error handling)
        try:
            symbols = provider.get_supported_symbols()
            click.echo(f"Supported symbols: {len(symbols)} available")
            if len(symbols) <= 10:
                click.echo(f"Symbols: {', '.join(symbols)}")
        except Exception as e:
            click.echo(f"Supported symbols: Error retrieving - {e}")
            
    except Exception as e:
        click.echo(f"Error getting provider info: {e}")

@plugins.command()
@click.argument('provider_name')
def configure(provider_name):
    """Interactive configuration for a provider"""
    registry = PluginRegistry()
    config_manager = ProviderConfigManager()
    
    provider_class = registry.get_provider_class(provider_name)
    if not provider_class:
        click.echo(f"Provider '{provider_name}' not found")
        return
    
    click.echo(f"Configuring {provider_name} provider")
    click.echo("Enter configuration values (press Enter to skip):")
    
    config = {}
    
    # Common configuration fields
    common_fields = {
        'api_key': 'API Key',
        'api_secret': 'API Secret', 
        'api_password': 'API Password',
        'base_url': 'Base URL',
        'demo': 'Demo Mode (true/false)'
    }
    
    for field, description in common_fields.items():
        value = click.prompt(f"{description}", default="", show_default=False)
        if value:
            if field == 'demo':
                config[field] = value.lower() in ('true', 'yes', '1')
            else:
                config[field] = value
    
    if config:
        config_manager.set_provider_config(provider_name, config)
        click.echo(f"Configuration saved for {provider_name}")
    else:
        click.echo("No configuration provided")
```

### Error Handling and Logging

```python
# pynecore/core/providers/exceptions.py
class ProviderError(Exception):
    """Base exception for provider errors"""
    pass

class ProviderConfigurationError(ProviderError):
    """Raised when provider configuration is invalid"""
    pass

class ProviderConnectionError(ProviderError):
    """Raised when provider cannot connect to data source"""
    pass

class ProviderAuthenticationError(ProviderError):
    """Raised when provider authentication fails"""
    pass

class ProviderRateLimitError(ProviderError):
    """Raised when provider hits rate limits"""
    pass

class ProviderDataError(ProviderError):
    """Raised when provider receives invalid data"""
    pass
```

### Integration with PyneCore Script Runner

```python
# pynecore/core/script_runner.py (modifications)
from .plugins.registry import PluginRegistry
from .config.providers import ProviderConfigManager
from .providers.exceptions import ProviderError

class ScriptRunner:
    def __init__(self, script_path, data_source, syminfo, **kwargs):
        self.script_path = script_path
        self.syminfo = syminfo
        self.kwargs = kwargs
        
        # Initialize plugin system
        self.plugin_registry = PluginRegistry()
        self.config_manager = ProviderConfigManager()
        
        # Handle different data source types
        if isinstance(data_source, str):
            # Data source is a provider name
            self.data_iterator = self._create_provider_iterator(data_source)
        else:
            # Existing file-based data source
            self.data_iterator = data_source
    
    def _create_provider_iterator(self, provider_name: str):
        """Create data iterator from provider"""
        try:
            config = self.config_manager.get_provider_config(provider_name)
            provider = self.plugin_registry.get_provider_instance(provider_name, config)
            
            # Extract parameters from kwargs
            symbol = self.kwargs.get('symbol')
            timeframe = self.kwargs.get('timeframe', '1D')
            start_date = self.kwargs.get('start_date')
            end_date = self.kwargs.get('end_date')
            live_mode = self.kwargs.get('live_mode', False)
            
            if live_mode:
                return provider.get_live_stream(symbol, timeframe)
            else:
                return provider.get_historical_data(symbol, timeframe, start_date, end_date)
                
        except ProviderError as e:
            raise RuntimeError(f"Provider error: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to create provider iterator: {e}")
```

## Implementation Roadmap

### Phase 1: Core Infrastructure (Weeks 1-2)
- Implement base `DataProvider` interface
- Create plugin registry system
- Add entry point discovery mechanism
- Implement configuration management
- Create CLI plugin commands

### Phase 2: CCXT Integration (Weeks 3-4)
- Refactor existing CCXT code to implement `DataProvider` interface
- Ensure backward compatibility
- Add comprehensive error handling
- Implement rate limiting and reconnection logic

### Phase 3: CapitalCom Plugin (Weeks 5-6)
- Extract CapitalCom code to external plugin
- Create reference plugin implementation
- Develop plugin packaging and distribution
- Write comprehensive documentation

### Phase 4: Plugin Development Tools (Weeks 7-8)
- Create plugin template generator
- Develop testing framework for plugins
- Add plugin validation tools
- Create developer documentation

### Phase 5: Community and Documentation (Weeks 9-10)
- Set up plugin registry/marketplace
- Create comprehensive developer guides
- Add example plugins
- Community outreach and feedback

## Testing Strategy

### Unit Tests
- Test each provider interface method
- Mock external API calls
- Test configuration validation
- Test error handling scenarios

### Integration Tests
- Test plugin discovery and loading
- Test data flow from provider to script runner
- Test CLI commands
- Test configuration management

### End-to-End Tests
- Test complete plugin development workflow
- Test plugin installation and usage
- Test live trading scenarios
- Test browser compatibility

## Security Considerations

### API Key Management
- Secure storage of credentials
- Environment variable support
- Encryption for sensitive data
- Clear separation of demo/live credentials

### Plugin Validation
- Code signing for official plugins
- Security scanning for community plugins
- Sandboxing for untrusted plugins
- Permission system for plugin capabilities

### Network Security
- TLS/SSL for all API communications
- Certificate validation
- Proxy support for corporate environments
- Rate limiting to prevent abuse

This comprehensive plan provides the complete technical foundation for implementing a robust, extensible plugin system in PyneCore while maintaining simplicity for end users and providing powerful capabilities for developers.
        