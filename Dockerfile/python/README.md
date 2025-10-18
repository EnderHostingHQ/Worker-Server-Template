# Python Docker Images

Pre-built Docker images for Python applications with intelligent dependency management.

## Supported Python Versions

This repository provides Docker images for the following Python versions that are currently supported and not end-of-life:

*Last updated: 03.10.2025*

| Version | Status | End of Life | Image Tag |
|---------|--------|-------------|-----------|
| 3.14 | Bugfix | 2030-10 | `enderhostinghq/worker-python:3.14` |
| 3.13 | Bugfix | 2029-10 | `enderhostinghq/worker-python:3.13` |
| 3.12 | Security | 2028-10 | `enderhostinghq/worker-python:3.12` |
| 3.11 | Security | 2027-10 | `enderhostinghq/worker-python:3.11` |
| 3.10 | Security | 2026-10 | `enderhostinghq/worker-python:3.10` |
| Latest | Alias to 3.14 | - | `enderhostinghq/worker-python:latest` |

> **Note**: We only support Python versions that are not end-of-life according to the [official Python release schedule](https://devguide.python.org/versions/).

## Features

- **Intelligent Dependency Management**: Automatic `requirements.txt` detection and hash-based caching
- **Auto-execution**: Automatically runs `python main.py` or custom commands

## Quick Start

### Basic Usage

```bash
docker run -v /path/to/your/app:/app enderhostinghq/worker-python:3.13
```

### With Docker Compose

```yaml
services:
  app:
    image: enderhostinghq/worker-python:3.13
    volumes:
      - ./app:/app
    # Command is optional - defaults to "python main.py"
    # command: python custom_script.py
```

## Intelligent Dependency Management

The images feature smart dependency handling:

### Automatic Requirements Detection
- Scans for `requirements.txt` on startup
- If found, manages dependencies automatically
- Uses virtual environment isolation

### Hash-Based Caching
- Stores SHA256 hash of `requirements.txt` in `.venv/requirements.sha256`
- Compares current requirements with cached hash
- Only reinstalls dependencies when requirements change

### Dependency Installation Process
1. **First Run**: If no `.venv/requirements.sha256` exists, installs all dependencies from `requirements.txt`
2. **Subsequent Runs**: Compares current requirements hash with stored hash
3. **Hash Match**: Skips installation, uses existing virtual environment
4. **Hash Mismatch**: Uninstalls all dependencies and reinstalls from updated `requirements.txt`

### Command Execution
- **Default**: Executes `python main.py` after dependency setup
- **Custom Command**: Override with custom command via Docker CMD
- **Fallback**: If custom command fails, falls back to `python main.py`

## Usage Examples

### Running with Automatic Dependency Management

```bash
# Place your requirements.txt and main.py in the current directory
docker run -v $(pwd):/app enderhostinghq/worker-python:3.13
# Dependencies are automatically installed and main.py is executed
```

### Running a Custom Script

```bash
docker run -v $(pwd):/app enderhostinghq/worker-python:3.13 python custom_script.py
```

## Building Custom Images

Use these base images to create your own application-specific containers:

```dockerfile
FROM enderhostinghq/worker-python:3.13

# Copy your application (requirements.txt will be handled automatically)
COPY . /app

# No need to manually install dependencies - handled by entrypoint
# Custom command (optional - defaults to "python main.py")
CMD ["python", "your_custom_script.py"]
```

## Image Sizes

All images are optimized for production use while maintaining compatibility:

- Based on official Python images

## Version Support Policy

We follow the official Python release cycle:

- **Bugfix versions**: Latest stable release with active development
- **Security versions**: Receive security updates only
- **End-of-life**: No longer supported or maintained

Images are automatically updated every week when new security patches are released for supported Python versions.

## Contributing

To build images locally:

```bash
# Navigate to the specific version directory
cd 3.13/

# Build the image
docker build -t enderhostinghq/worker-python:3.13 .
```

## Support

For issues, questions, or contributions, please refer to the main repository documentation.

## License

See the [LICENSE](https://github.com/EnderHostingHQ/Worker-Server-Template/blob/master/LICENSE) file for licensing information.
