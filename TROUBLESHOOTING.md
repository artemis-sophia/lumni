# Troubleshooting Guide

## Build Issues

### better-sqlite3 Native Module Build Fails

**Error:**
```
npm error gyp ERR! build error
npm error gyp ERR! stack Error: `make` failed with exit code: 2
```

**Solutions:**

1. **Install Build Dependencies (Recommended)**
   ```bash
   # Fedora/RHEL
   sudo dnf install make gcc-c++ python3
   
   # Ubuntu/Debian
   sudo apt-get install build-essential python3
   
   # macOS
   xcode-select --install
   ```

2. **Use Alternative Storage (Quick Fix)**
   Edit `src/storage/storage.ts` to use in-memory storage for development:
   ```typescript
   // Change storage type in config.json to "memory"
   // Or modify Storage class to use Map instead of SQLite
   ```

3. **Switch to sqlite3 Package**
   ```bash
   npm uninstall better-sqlite3
   npm install sqlite3
   ```
   Then update `src/storage/storage.ts` to use `sqlite3` instead.

4. **Move Project Directory**
   If the issue is related to directory names with special characters:
   ```bash
   cd ..
   mv "old-name" lumni
   cd lumni
   # Continue with setup
   ```

### TypeScript Not Found

**Error:**
```
sh: line 1: tsc: command not found
```

**Solution:**
```bash
npm install
# This installs TypeScript as a dev dependency
```

### Missing .env.example

**Error:**
```
cp: cannot stat '.env.example': No such file or directory
```

**Solution:**
The init script now handles this automatically. If you see this error:
1. The script will create a basic `.env` file
2. Or manually create `.env.example` from the template in the repository

## Runtime Issues

### Port Already in Use

**Error:**
```
Error: listen EADDRINUSE: address already in use :::3000
```

**Solution:**
1. Change port in `config.json`:
   ```json
   {
     "server": {
       "port": 3001
     }
   }
   ```
2. Or kill the process using port 3000:
   ```bash
   lsof -ti:3000 | xargs kill
   ```

### Providers Failing

**Symptoms:**
- All requests return errors
- Provider status shows "unhealthy"

**Solutions:**
1. Verify API keys in `.env` are correct
2. Check provider status: `GET /api/v1/providers/status`
3. Review logs in `logs/combined.log`
4. Ensure provider is enabled in `config.json`

### Rate Limits Hit Immediately

**Symptoms:**
- Providers fail with "Rate limit exceeded" immediately

**Solutions:**
1. Check rate limit configuration in `config.json` matches actual provider limits
2. Enable more providers for better fallback
3. Consider enabling VPN rotation
4. Review usage statistics: `GET /api/v1/usage`

## Configuration Issues

### Environment Variables Not Loading

**Symptoms:**
- API keys not found
- Configuration errors

**Solutions:**
1. Ensure `.env` file exists in project root
2. Check `.env` file format (no spaces around `=`)
3. Verify `dotenv` package is installed
4. Restart the server after changing `.env`

### Invalid Configuration

**Error:**
```
Configuration file not found: ./config.json
```

**Solution:**
```bash
cp config.example.json config.json
# Then edit config.json with your settings
```

## Getting Help

1. Check logs in `logs/combined.log` for detailed error messages
2. Review `ARCHITECTURE.md` for system design
3. See `SETUP.md` for detailed configuration instructions
4. Check provider status endpoint for health information




